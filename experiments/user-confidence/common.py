#!/usr/bin/env python3
"""Four-arm user-diagnosis experiment, accessed through a ChatGPT subscription."""
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

