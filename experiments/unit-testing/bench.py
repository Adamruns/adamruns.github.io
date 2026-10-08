#!/usr/bin/env python3
"""Subscription-only paired benchmark. Private artifacts stay under --data."""
import argparse, ast, collections, hashlib, itertools, json, os, random, re
import shutil, signal, subprocess, sys, tarfile, tempfile, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE/'protocol.json').read_text())


def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def env():
    e={k:v for k,v in os.environ.items() if k in ['HOME','PATH','TMPDIR','LANG','LC_ALL','USER','LOGNAME','CODEX_HOME']}
    e.update(PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONHASHSEED='0')
    return e


def cmd(args,cwd,timeout=180):
    p=subprocess.Popen(args,cwd=cwd,env=env(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
    try:
        out,_=p.communicate(timeout=timeout);return p.returncode,out
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);out,_=p.communicate();return 124,out


def patch(repo,text):
    p=subprocess.run(['git','apply','--whitespace=nowarn','-'],input=text,cwd=repo,text=True,capture_output=True,env=env())
    if p.returncode:raise RuntimeError(p.stderr.strip())


def nodes(repo,row,category):
    lookup=collections.defaultdict(list)
    for path in re.findall(r'^\+\+\+ b/(.+)$',row['test_patch'],re.M):
        for node in ast.parse((repo/path).read_text()).body:
            if isinstance(node,ast.FunctionDef):lookup[node.name].append(f'{path}::{node.name}')
    result=[]
    for name in json.loads(row[category]):
        if not lookup[name]:raise ValueError(f'Cannot map {category}: {name}')
        result.extend(lookup[name])
    if not result:raise ValueError('Empty '+category)
    return result


def grade(repo,python,tests,log,timeout=180):
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    xml=log.with_suffix('.xml');xml.unlink(missing_ok=True)
    code,out=cmd([str(python),'-m','pytest','-q','-o','addopts=','--tb=short',f'--junitxml={xml}',*tests],repo,timeout)
    log.write_text(out)
    counts=dict(passed=0,failed=0,errors=0,skipped=0,collected=0);cases=[]
    if xml.exists():
        for e in ET.parse(xml).iter('testcase'):
            status='errors' if e.find('error') is not None else 'failed' if e.find('failure') is not None else 'skipped' if e.find('skipped') is not None else 'passed'
            counts[status]+=1;counts['collected']+=1;cases.append(dict(name=e.get('name'),status=status))
    return dict(returncode=code,**counts,all_pass=code==0 and counts['passed']>=len(tests) and not any(counts[k] for k in ['failed','errors','skipped']),cases=cases)


def snapshot(row,target,data):
    archive=data/'archives'/(row['base_commit']+'.tar.gz');archive.parent.mkdir(exist_ok=True)
    if not archive.exists():
        with urllib.request.urlopen(f"https://codeload.github.com/{row['repo']}/tar.gz/{row['base_commit']}",timeout=90) as r:archive.write_bytes(r.read())
    target.mkdir(parents=True)
    with tarfile.open(archive) as tf:
        for m in tf:
            parts=Path(m.name).parts[1:]
            if not parts or '..' in parts or m.issym() or m.islnk():continue
            dest=target.joinpath(*parts)
            if m.isdir():dest.mkdir(parents=True,exist_ok=True)
            elif m.isfile():
                dest.parent.mkdir(parents=True,exist_ok=True)
                with tf.extractfile(m) as source:dest.write_bytes(source.read())
                dest.chmod(m.mode & 0o777)
    # Prevent git apply from discovering the enclosing website repository and
    # silently skipping patch paths outside its current subdirectory.
    code,out=cmd(['git','init','-q'],target)
    if code:raise RuntimeError(out)


def added_lines(diff):
    result=collections.defaultdict(set);path=None;line=0
    for text in diff.splitlines():
        if text.startswith('+++ b/'):path=text[6:]
        elif text.startswith('@@'):line=int(re.search(r'\+(\d+)',text).group(1))
        elif text.startswith('+') and path:result[path].add(line);line+=1
        elif text.startswith(' '):line+=1
    return result


def mutants(repo,row):
    repl={'==':'!=','!=':'==','<=':'<','>=':'>','<':'>=','>':'<=','True':'False','False':'True','+':'-','-':'+','0':'1','1':'0'}
    pattern=re.compile(r'(?<![\w])(?:True|False|0|1)(?![\w])|==|!=|<=|>=|(?<![<>=])[<>](?![<>=])|(?<= )[-+](?= )')
    for path,numbers in sorted(added_lines(row['patch']).items()):
        if not path.endswith('.py') or '/tests/' in path:continue
        lines=(repo/path).read_text().splitlines(keepends=True)
        for number in sorted(numbers):
            line=lines[number-1]
            if line.lstrip().startswith('#'):continue
            for match in pattern.finditer(line):
                changed=line[:match.start()]+repl[match.group()]+line[match.end():]
                code=''.join(lines[:number-1]+[changed]+lines[number:])
                try:ast.parse(code)
                except SyntaxError:continue
                yield dict(path=path,line=number,before=line.rstrip(),after=changed.rstrip(),code=code)


def prepare(data):
    if (data/'manifest.json').exists():raise SystemExit('Manifest already frozen.')
    python=data/'venv/bin/python';rows=json.loads((data/'swebench-verified.json').read_text())
    candidates=[r for r in rows if r['repo']=='sympy/sympy' and tuple(map(int,r['version'].split('.')))>=(1,7)]
    random.Random(PROTOCOL['order_seed']).shuffle(candidates);selected=[];audit=[]
    for row in candidates:
        iid=row['instance_id'];root=data/'preflight'/iid;root.mkdir(parents=True,exist_ok=True);repo=root/'repo'
        print('PREFLIGHT',iid,flush=True);record=dict(instance_id=iid,eligible=False)
        try:
            snapshot(row,repo,data);patch(repo,row['test_patch'])
            ftp=nodes(repo,row,'FAIL_TO_PASS');ptp=nodes(repo,row,'PASS_TO_PASS')
            original_f=grade(repo,python,ftp,root/'original-fail.log')
            original_p=grade(repo,python,ptp,root/'original-pass.log')
            patch(repo,row['patch']);reference=grade(repo,python,ftp+ptp,root/'reference.log')
            record.update(original_fail=original_f,original_pass=original_p,reference=reference)
            if original_f['failed']<1 or original_f['errors'] or original_f['skipped'] or original_f['returncode']!=1:raise ValueError('Original FAIL_TO_PASS did not fail cleanly')
            if not original_p['all_pass'] or not reference['all_pass']:raise ValueError('Original PASS_TO_PASS or reference acceptance not green')
            accepted=[]
            for i,m in enumerate(itertools.islice(mutants(repo,row),20)):
                file=repo/m['path'];original=file.read_text();file.write_text(m['code'])
                try:outcome=grade(repo,python,ftp,root/f'mutant-{i}.log',45)
                finally:file.write_text(original)
                if outcome['returncode']==1 and outcome['failed'] and not outcome['errors'] and not outcome['skipped']:
                    m['validation']=outcome;accepted.append(m)
                    if len(accepted)==3:break
            row=dict(row,fail_nodes=ftp,pass_nodes=ptp,mutants=accepted)
            save(root/'task.json',row);record.update(eligible=True,mutants=len(accepted));selected.append(row)
            print('SELECTED',iid,'tasks',len(selected),'mutants',len(accepted),flush=True)
        except Exception as exc:record['reason']=str(exc);print('EXCLUDED',iid,str(exc)[:200],flush=True)
        finally:
            audit.append(record);save(data/'selection-audit.json',audit)
            if repo.exists():shutil.rmtree(repo)
        if len(selected)==PROTOCOL['target_tasks']:break
    if len(selected)!=PROTOCOL['target_tasks']:raise SystemExit(f'Only {len(selected)} validated tasks; no scored inference started.')
    schedule=[dict(instance_id=r['instance_id'],condition=c,repetition=n) for r in selected for c in PROTOCOL['conditions'] for n in range(1,PROTOCOL['repetitions']+1)]
    random.Random(PROTOCOL['order_seed']).shuffle(schedule)
    manifest=dict(protocol=PROTOCOL,protocol_sha256=sha(HERE/'protocol.json'),dataset_sha256=sha(data/'swebench-verified.json'),prepared_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),tasks=selected,schedule=schedule,cli_version=cmd(['codex','--version'],HERE)[1].strip(),python_version=cmd([str(python),'--version'],HERE)[1].strip())
    save(data/'manifest.json',manifest);print('FROZEN',len(selected),'tasks',len(schedule),'runs',sha(data/'manifest.json'),flush=True)


def prompt(row,condition,python):
    policy=('Do not create or modify tests, new assertions, test snippets, or ad-hoc behavioral test scripts. You may run existing tests and inspect source code.' if condition=='no-new-tests' else 'Write at least one behavioral regression test with pytest assertions in a new root file named test_agent_regression.py. Run it using the Python interpreter below and leave it in the final workspace. It should pass with your fix and detect the reported bug. You may also run existing tests.')
    return f'''Fix the following issue in this repository. Make a production code change that resolves the reported behavior while preserving existing behavior.

{row['problem_statement']}

Testing policy:
{policy}

Common constraints:
- Do not alter, remove, or disable existing test files, configuration, dependencies, or test infrastructure.
- Work only in this repository. Do not read other workspaces, saved chats, caches, evaluation files, or hidden acceptance tests. Do not use the internet or other models or agents.
- You have a five-minute wall-clock cap including inspection, coding, and test execution. Finish promptly; do not spend the entire budget writing a report.
- Run Python and pytest with {python}. Runtime packages are already installed. Do not install packages.
- The checkout contains original code and existing tests. Its git history contains only this baseline.
- Leave actual edits on disk. Conclude with a concise explanation and the commands you ran. Do not commit.
'''


def init_git(repo):
    for args in [['git','init','-q'],['git','add','.'],['git','-c','user.name=Benchmark','-c','user.email=benchmark@localhost','commit','-qm','baseline']]:
        code,out=cmd(args,repo)
        if code:raise RuntimeError(out)


def is_test(p):return '/tests/' in '/'+p or Path(p).name.startswith('test_') or Path(p).name.endswith('_test.py')


def suite(repo,python,test,log):
    (repo/'test_agent_regression.py').write_text(test)
    return grade(repo,python,['test_agent_regression.py'],log,90)


def evaluate(row,trial,root,data):
    python=data/'venv/bin/python'
    changed=cmd(['git','diff','--name-only'],trial)[1].splitlines();untracked=cmd(['git','ls-files','--others','--exclude-standard'],trial)[1].splitlines()
    tests=[p for p in changed+untracked if is_test(p)]
    production=[p for p in changed+untracked if p.endswith('.py') and not is_test(p)]
    excluded=[p for p in changed+untracked if p not in production and p not in tests]
    for p in untracked:
        if p in production:cmd(['git','add','--intent-to-add','--',p],trial)
    prod_patch=cmd(['git','diff','--binary','--',*production],trial)[1] if production else ''
    (root/'production.patch').write_text(prod_patch);(root/'all.patch').write_text(cmd(['git','diff','--binary'],trial)[1])
    generated=trial/'test_agent_regression.py';test=generated.read_text() if generated.exists() else None
    if test is not None:(root/'test_agent_regression.py').write_text(test)
    work=root/'evaluation';snapshot(row,work,data)
    result=dict(changed=changed,untracked=untracked,test_artifacts=tests,excluded_changes=excluded)
    try:
        if prod_patch:patch(work,prod_patch)
        patch(work,row['test_patch'])
        result['acceptance']=grade(work,python,row['fail_nodes']+row['pass_nodes'],root/'acceptance.log')
    except Exception as exc:result['evaluation_error']=str(exc)
    finally:shutil.rmtree(work)
    if test:
        reg={}
        for variant in ['agent','reference','original']:
            snapshot(row,work,data)
            try:
                if variant=='agent' and prod_patch:patch(work,prod_patch)
                if variant=='reference':patch(work,row['patch'])
                reg[variant]=suite(work,python,test,root/f'test-{variant}.log')
            except Exception as exc:reg[variant]=dict(error=str(exc),all_pass=False)
            finally:shutil.rmtree(work)
        reg['mutants']=[]
        if reg['reference'].get('all_pass'):
            for i,m in enumerate(row['mutants']):
                snapshot(row,work,data)
                try:
                    patch(work,row['patch']);(work/m['path']).write_text(m['code'])
                    outcome=suite(work,python,test,root/f'test-mutant-{i}.log')
                    killed=outcome['returncode']==1 and outcome['failed']>0 and not outcome['errors'] and not outcome['skipped']
                    reg['mutants'].append(dict(index=i,killed=killed,**outcome))
                finally:shutil.rmtree(work)
        result['regression']=reg
    return result


def run(data,limit=None):
    manifest=json.loads((data/'manifest.json').read_text())
    if manifest['protocol_sha256']!=sha(HERE/'protocol.json'):raise SystemExit('Protocol changed after freeze.')
    code,auth=cmd(['codex','login','status'],HERE)
    if code or 'Logged in using ChatGPT' not in auth:raise SystemExit('ChatGPT login required; API fallback prohibited.')
    rows={r['instance_id']:r for r in manifest['tasks']};done=0
    for position,item in enumerate(manifest['schedule'],1):
        rid=f"{item['instance_id']}--{item['condition']}--r{item['repetition']}";root=data/'runs'/rid
        if (root/'result.json').exists():continue
        if (root/'started.json').exists():raise SystemExit('Interrupted attempt requires audit: '+rid)
        root.mkdir(parents=True,exist_ok=True);row=rows[item['instance_id']]
        trial=Path(tempfile.mkdtemp(prefix='unit-testing-trial-'))/'repo';snapshot(row,trial,data);init_git(trial)
        instruction=prompt(row,item['condition'],data/'venv/bin/python');(root/'prompt.txt').write_text(instruction)
        blocked=[p for p in data.iterdir() if p.name!='venv']+[HERE,HERE.parent.parent/'assets/experiments']
        profile='(version 1)(allow default)'+''.join('(deny file-read* (subpath '+json.dumps(str(p))+'))' for p in blocked)
        profile+='(deny file-write* (subpath '+json.dumps(str(HERE.parent.parent))+'))'
        # Seatbelt cannot be nested. The outer profile withholds evaluation data;
        # do not ask Codex to launch a second nested Seatbelt process.
        args=['/usr/bin/sandbox-exec','-p',profile,'codex','exec','--ignore-user-config','--ephemeral','--sandbox','danger-full-access','-c','approval_policy="never"','-c','forced_login_method="chatgpt"','-c','model_reasoning_effort="medium"','-c','project_doc_max_bytes=0','-m',PROTOCOL['model'],'--json','-']
        started=time.time();save(root/'started.json',dict(**item,started_at=started,command=args,manifest_sha256=sha(data/'manifest.json')))
        print('RUN',position,'/',len(manifest['schedule']),rid,flush=True)
        p=subprocess.Popen(args,cwd=trial,env=env(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True);status='completed'
        try:stdout,stderr=p.communicate(instruction,timeout=PROTOCOL['timeout_seconds'])
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);stdout,stderr=p.communicate();status='timeout'
        elapsed=time.time()-started;(root/'trajectory.jsonl').write_text(stdout);(root/'stderr.log').write_text(stderr)
        events=[]
        for line in stdout.splitlines():
            try:events.append(json.loads(line))
            except ValueError:pass
        complete=[e for e in events if e.get('type')=='turn.completed']
        if status=='completed' and (p.returncode or not complete):status='infrastructure-error'
        usage=complete[-1].get('usage',{}) if complete else {}
        result=dict(**item,run_id=rid,status=status,elapsed_seconds=elapsed,usage=usage,started_at=started,exit_code=p.returncode)
        if status!='infrastructure-error':
            try:result.update(evaluate(row,trial,root,data))
            except Exception as exc:result['evaluation_error']=str(exc)
        commands=[e['item'].get('command','') for e in events if e.get('item',{}).get('type')=='command_execution' and e.get('type')=='item.completed']
        result['commands']=commands
        result['test_execution_observed']=any('test_agent_regression.py' in c and ('pytest' in c or 'python' in c) for c in commands)
        result['compliance_auto']=(not result.get('test_artifacts') if item['condition']=='no-new-tests' else bool(result.get('regression')) and result['test_execution_observed'])
        result['compliance_note']='Artifact and command audit; inline or subsequently deleted tests require trajectory review.'
        save(root/'result.json',result);shutil.rmtree(trial.parent)
        report=subprocess.run([sys.executable,str(HERE/'report.py'),'--data',str(data)],capture_output=True,text=True)
        if report.returncode:print('REPORT ERROR',report.stderr[-500:],flush=True)
        print('RESULT',rid,status,'solved',result.get('acceptance',{}).get('all_pass'),'seconds',round(elapsed),'tokens',usage.get('input_tokens'),flush=True)
        if status=='infrastructure-error':
            print(stderr[-1500:],stdout[-1500:],flush=True);raise SystemExit('Stopped on infrastructure/auth/quota error; no automatic retry.')
        done+=1
        if limit and done>=limit:break


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run']);p.add_argument('--data',type=Path,required=True);p.add_argument('--limit',type=int)
    args=p.parse_args();data=args.data.resolve();data.mkdir(parents=True,exist_ok=True)
    if args.action=='prepare':prepare(data)
    else:run(data,args.limit)
