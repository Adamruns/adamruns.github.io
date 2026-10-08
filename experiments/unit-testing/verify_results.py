#!/usr/bin/env python3
"""Validate final reported outcomes against raw trajectories and grader XML."""
import argparse,collections,csv,hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
p.add_argument('--public',type=Path,default=Path(__file__).resolve().parents[2]/'assets/experiments/unit-testing')
a=p.parse_args();data=a.data.resolve()
manifest=json.loads((data/'manifest.json').read_text())
expected={(r['instance_id'],r['condition'],r['repetition']) for r in manifest['schedule']}
tasks={r['instance_id']:r for r in manifest['tasks']}
paths=list((data/'runs').glob('*/result.json'));assert len(paths)==80
observed=set();counts=collections.Counter();regression=collections.Counter()

def check_grade(g,path,minimum=1):
    if g.get('error'):
        assert not g['all_pass']
        return
    xml=ET.parse(path);actual=collections.Counter();cases=[]
    for e in xml.iter('testcase'):
        status='errors' if e.find('error') is not None else 'failed' if e.find('failure') is not None else 'skipped' if e.find('skipped') is not None else 'passed'
        actual[status]+=1;cases.append(dict(name=e.get('name'),status=status))
    for k in ['passed','failed','errors','skipped']:assert g[k]==actual[k],str(path)
    assert g['collected']==sum(actual.values())
    assert g['cases']==cases
    assert g['all_pass']==(g['returncode']==0 and actual['passed']>=minimum and not (actual['failed'] or actual['errors'] or actual['skipped']))

def detected(g):
    return g.get('returncode')==1 and g.get('failed',0)>0 and not g.get('errors') and not g.get('skipped')

for path in paths:
    r=json.loads(path.read_text());key=(r['instance_id'],r['condition'],r['repetition']);assert key not in observed;observed.add(key)
    start=json.loads((path.parent/'started.json').read_text());command=start['command']
    assert command[command.index('-m')+1]==manifest['protocol']['model']
    assert 'forced_login_method="chatgpt"' in command
    assert f'model_reasoning_effort="{manifest["protocol"]["reasoning_effort"]}"' in command
    assert '--ignore-user-config' in command
    assert start['manifest_sha256']==hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest()
    assert 'compliance_review' in r, r['run_id']
    events=[json.loads(line) for line in (path.parent/'trajectory.jsonl').read_text().splitlines() if line.startswith('{')]
    complete=[e for e in events if e.get('type')=='turn.completed']
    if r['status']=='completed':assert complete and r['usage']==complete[-1]['usage']
    assert not r.get('evaluation_error'),r['run_id']
    g=r['acceptance'];task=tasks[r['instance_id']]
    check_grade(g,path.parent/'acceptance.xml',len(task['fail_nodes'])+len(task['pass_nodes']))
    counts[(r['condition'],'attempts')]+=1;counts[(r['condition'],'solved')]+=int(g['all_pass'])
    if r['condition']=='write-tests' and 'regression' in r:
        reg=r['regression'];regression['suites_created']+=1
        for variant in ['agent','reference','original']:
            check_grade(reg[variant],path.parent/f'test-{variant}.xml')
        regression['pass_agent']+=int(reg['agent']['all_pass'])
        if reg['reference']['all_pass']:
            regression['valid_reference']+=1
            regression['original_caught']+=int(detected(reg['original']))
            assert len(reg['mutants'])==len(task['mutants'])
            for mutant in reg['mutants']:
                check_grade(mutant,path.parent/f'test-mutant-{mutant["index"]}.xml')
                assert mutant['killed']==detected(mutant)
                regression['mutants_tested']+=1;regression['mutants_killed']+=int(mutant['killed'])
        else:assert not reg['mutants']
assert observed==expected
out=a.public.resolve()
d=json.loads((out/'results.json').read_text());assert d['status']=='complete'
for condition in ['no-new-tests','write-tests']:
    assert counts[(condition,'attempts')]==40
    assert d['arms'][condition]['solved']==counts[(condition,'solved')]
for metric in ['suites_created','pass_agent','valid_reference','original_caught','mutants_tested','mutants_killed']:
    assert d['regression'][metric]==regression[metric],metric
with (out/'runs.csv').open() as f:assert len(list(csv.DictReader(f)))==80
assert len((out/'tweet.txt').read_text().strip())<=280
print('PASS: 80 unique scheduled runs; model/auth; manifest hash; token provenance; acceptance/regression/mutation XML; public counts/CSV; tweet length.')
print(dict(counts))
