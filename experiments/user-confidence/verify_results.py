#!/usr/bin/env python3
"""Verify measured outcomes, prompts, schedule and token provenance without inference."""
import argparse, collections, csv, hashlib, json
from pathlib import Path
import xml.etree.ElementTree as ET
import report


def check_grade(grade, path, minimum):
    counts=collections.Counter();cases=[]
    for e in ET.parse(path).iter('testcase'):
        status='errors' if e.find('error') is not None else 'failed' if e.find('failure') is not None else 'skipped' if e.find('skipped') is not None else 'passed'
        counts[status]+=1;cases.append(dict(name=e.get('name'),status=status))
    for key in ('passed','failed','errors','skipped'):assert grade[key]==counts[key],str(path)
    assert grade['collected']==sum(counts.values())
    assert grade['cases']==cases
    assert grade['all_pass']==(grade['returncode']==0 and counts['passed']>=minimum and not any(counts[k] for k in ('failed','errors','skipped')))


def verify(data, public):
    manifest_path=data/'manifest.json';manifest=json.loads(manifest_path.read_text());raw=[]
    for key,name in [('protocol','protocol.json'),('diagnoses','diagnoses.json'),('runner','bench.py'),('common','common.py')]:
        assert hashlib.sha256((Path(__file__).resolve().parent/name).read_bytes()).hexdigest()==manifest[key+'_sha256'],name
    digest=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    provenance=data/'manifest-redaction.json'
    if provenance.exists():
        p=json.loads(provenance.read_text());assert p['published_sha256']==digest;digest=p['original_sha256']
    expected={(r['instance_id'],r['condition'],r['repetition']) for r in manifest['schedule']};seen=set()
    tasks={r['instance_id']:r for r in manifest['tasks']}
    assert len(expected)==160 and len(tasks)==20
    for row in tasks.values():
        assert row['prompts']['tentative-wrong'].replace('I suspect the cause is:',"I've confirmed the cause is:")==row['prompts']['confident-wrong']
    preflight=json.loads((data/'preflight.json').read_text())
    assert len(preflight)==20
    for row in preflight:
        task=tasks[row['instance_id']];folder=data/'preflight'/row['instance_id']
        for key,log,minimum in [('original_fail','original-fail',len(task['fail_nodes'])),('original_pass','original-pass',len(task['pass_nodes'])),('reference','reference',len(task['fail_nodes'])+len(task['pass_nodes']))]:
            check_grade(row[key],folder/(log+'.xml'),minimum)
        assert row['original_fail']['failed'] and row['original_pass']['all_pass'] and row['reference']['all_pass']
    for path in sorted((data/'runs').glob('*/result.json')):
        r=json.loads(path.read_text());key=(r['instance_id'],r['condition'],r['repetition'])
        assert key in expected and key not in seen;seen.add(key);raw.append(r)
        row=tasks[r['instance_id']];start=json.loads((path.parent/'started.json').read_text());command=start['command']
        assert start['manifest_sha256']==digest
        assert command[command.index('-m')+1]==manifest['protocol']['model']
        assert 'forced_login_method="chatgpt"' in command and 'model_reasoning_effort="medium"' in command
        assert '--ignore-user-config' in command and '--ephemeral' in command
        # Original issue statements contain CRLF; preserve the actual input bytes.
        assert (path.parent/'prompt.txt').read_bytes().decode('utf-8')==row['prompts'][r['condition']],r['run_id']
        events=[json.loads(line) for line in (path.parent/'trajectory.jsonl').read_text().splitlines() if line.startswith('{')]
        completed=[e for e in events if e.get('type')=='turn.completed']
        if r['status']=='completed':assert completed and r['usage']==completed[-1]['usage']
        messages=[e['item'].get('text','') for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
        assert messages==r['messages']
        commands=[e['item'].get('command','') for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
        assert commands==r['commands']
        changes=[change for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='file_change' for change in e['item'].get('changes',[])]
        assert changes==r['trajectory_audit']['file_changes']
        assert not r.get('evaluation_error') and r['status'] in ('completed','timeout')
        check_grade(r['acceptance'],path.parent/'acceptance.xml',len(row['fail_nodes'])+len(row['pass_nodes']))
        assert 'compliance_review' in r,r['run_id']
        if 'wrong' in r['condition']:
            review=r['diagnosis_review'];assert review['category'] in manifest['protocol']['challenge_rubric']
            for quote in review.get('quotes',[]):assert quote in '\n'.join(messages),(r['run_id'],quote)
            if review['category']=='explicit-rejection':assert review.get('quotes'),r['run_id']
    assert seen==expected
    actual=report.analyze(manifest,raw);published=json.loads((public/'results.json').read_text())
    assert published['status']=='complete' and published['review_complete']
    assert published['manifest_sha256']==digest
    assert published['arms']==actual['arms'] and published['contrasts']==actual['contrasts']
    assert published['runs']==json.loads(report.redact(json.dumps(actual['runs']),data))
    for key in ('model','reasoning_effort','planned','recorded','evaluated','task_count'):
        assert published[key]==actual[key],key
    with (public/'runs.csv').open() as f:csv_rows=list(csv.DictReader(f))
    by_id={r['run_id']:r for r in actual['runs']}
    assert len(csv_rows)==160 and {r['run_id'] for r in csv_rows}==set(by_id)
    for row in csv_rows:
        recorded=by_id[row['run_id']]
        for key in ('instance_id','condition','repetition','status','evaluated','solved','elapsed_seconds'):
            assert row[key]==str(recorded[key]),(row['run_id'],key)
        for key in ('input_tokens','cached_input_tokens','output_tokens'):
            assert row[key]==str(recorded.get('usage',{}).get(key,'')),(row['run_id'],key)
        review=recorded.get('diagnosis_review')
        assert row['diagnosis_category']==(review['category'] if review else '')
        assert row['explicit_rejection']==(str(review['category']=='explicit-rejection') if review else '')
        assert row['compliant']==str(recorded['compliance_review']['compliant'])
    assert len((public/'tweet.txt').read_text().strip())<=280
    print('PASS: 160 scheduled attempts; 20 original/reference checks; controlled prompts; model/auth; manifest provenance; usage; acceptance XML; review quote provenance; recomputed paired statistics; CSV; tweet length.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--public',type=Path,default=report.OUT);a=p.parse_args();verify(a.data.resolve(),a.public.resolve())
