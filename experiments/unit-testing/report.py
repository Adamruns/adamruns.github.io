#!/usr/bin/env python3
"""Export real measurements, paired statistics, CSV, chart and reviewable tweet."""
import argparse, collections, csv, datetime, hashlib, io, json, random, re, statistics, tempfile, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SITE=HERE.parent.parent
OUT=SITE/'assets/experiments/unit-testing'
LABELS={'no-new-tests':'No new tests','write-tests':'Write a test'}

def save(path,value):
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as f:
        f.write(json.dumps(value,indent=2)+'\n');temp=Path(f.name)
    temp.replace(path)

def redact_local_paths(text,data):
    text=text.replace(str(data/'venv/bin/python'),'<PYTHON>')
    text=text.replace(str(data),'<EXPERIMENT_DATA>')
    text=re.sub(r'/private/var/folders/[^\s"\']+/unit-testing-trial-[^/\s"\']+/repo','<TRIAL>',text)
    text=re.sub(r'/var/folders/[^\s"\']+/unit-testing-trial-[^/\s"\']+/repo','<TRIAL>',text)
    return text.replace(str(Path.home()),'<HOME>')

def build(data):
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=json.loads((HERE/'protocol.json').read_text());mp=data/'manifest.json'
    manifest=json.loads(mp.read_text()) if mp.exists() else None
    import audit
    for path in sorted((data/'runs').glob('*/result.json')):
        if (path.parent/'trajectory.jsonl').exists():audit.audit(path)
    raw=[json.loads(p.read_text()) for p in sorted((data/'runs').glob('*/result.json'))] if (data/'runs').exists() else []
    runs=[]
    for r in raw:
        r=dict(r);r['solved']=bool(r.get('acceptance',{}).get('all_pass'))
        r['evaluated']='acceptance' in r and not r.get('evaluation_error')
        runs.append(r)
    arms={}
    for condition in LABELS:
        arm=[r for r in runs if r['condition']==condition];complete=[r for r in arm if r['status']=='completed']
        audited=[r for r in arm if 'compliance_review' in r]
        arms[condition]=dict(scheduled=40,completed=len(complete),evaluated=sum(r['evaluated'] for r in arm),solved=sum(r['solved'] for r in arm),
            timeouts=sum(r['status']=='timeout' for r in arm),errors=sum(r['status']=='infrastructure-error' or bool(r.get('evaluation_error')) for r in arm),
            mean_seconds=statistics.mean(r['elapsed_seconds'] for r in complete) if complete else 0,
            attempted=len(arm),total_seconds=sum(r['elapsed_seconds'] for r in arm),
            mean_attempt_seconds=statistics.mean(r['elapsed_seconds'] for r in arm) if arm else 0,
            audited=len(audited),compliant=sum(r['compliance_review']['compliant'] for r in audited),
            **{k:sum(r.get('usage',{}).get(k,0) for r in arm) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']})
    tests=[r for r in runs if r['condition']=='write-tests'];valid=[r for r in tests if r.get('regression',{}).get('reference',{}).get('all_pass')]
    caught=lambda x:x.get('returncode')==1 and x.get('failed',0)>0 and not x.get('errors') and not x.get('skipped')
    original=sum(caught(r['regression'].get('original',{})) for r in valid)
    mutation_results=[m for r in valid for m in r['regression']['mutants']]
    distinct_mutants={(r['instance_id'],m['index']) for r in valid for m in r['regression']['mutants']}
    regression=dict(test_attempts=len(tests),suites_created=sum('regression' in r for r in tests),valid_reference=len(valid),
                    pass_agent=sum(r.get('regression',{}).get('agent',{}).get('all_pass',False) for r in tests),
                    original_caught=original,mutants_killed=sum(m['killed'] for m in mutation_results),mutants_tested=len(mutation_results),
                    distinct_mutants_tested=len(distinct_mutants),mutation_issues_tested=len({iid for iid,index in distinct_mutants}),
                    reference_suites_with_failures=sum(r.get('regression',{}).get('reference',{}).get('failed',0)>0 for r in tests),
                    reference_suites_with_skips=sum(r.get('regression',{}).get('reference',{}).get('skipped',0)>0 for r in tests),
                    reference_suites_with_errors=sum(r.get('regression',{}).get('reference',{}).get('errors',0)>0 or bool(r.get('regression',{}).get('reference',{}).get('error')) for r in tests))
    completed=sum(r['status']=='completed' for r in runs);evaluated=sum(r['evaluated'] for r in runs)
    full=len(runs)==80 and evaluated==80
    pairs={}
    for r in runs:
        if r['evaluated']:pairs.setdefault((r['instance_id'],r['repetition']),{})[r['condition']]=int(r['solved'])
    task_diffs=collections.defaultdict(list)
    for (iid,rep),pair in pairs.items():
        if len(pair)==2:task_diffs[iid].append(pair['write-tests']-pair['no-new-tests'])
    diff=None;interval=None;pvalue=None;bootstrap_degenerate=False
    if full:
        values=[statistics.mean(v) for v in task_diffs.values()];diff=100*statistics.mean(values)
        bootstrap_degenerate=len(set(values))==1
        rng=random.Random(20261008);boots=sorted(100*statistics.mean(rng.choices(values,k=len(values))) for _ in range(20000));interval=[boots[499],boots[19499]]
        dist={0:1}
        for value in values:
            n=round(value*2);new=collections.Counter()
            for total,count in dist.items():new[total+n]+=count;new[total-n]+=count
            dist=new
        threshold=abs(sum(round(v*2) for v in values));pvalue=sum(c for total,c in dist.items() if abs(total)>=threshold)/sum(dist.values())
    if not runs:
        status='Preparing environments · no scored model attempts yet'
        takeaway='The benchmark is being validated before any scored runs. No experimental conclusion is available yet.'
    elif full:
        status=f'Pilot complete · {evaluated} evaluated attempts · 20 issues'
        a,b=arms.values()
        takeaway=f"Writing a test passed every acceptance check in {b['solved']}/40 attempts; no new tests in {a['solved']}/40. Of the generated suites valid on the reference fix, {original}/{len(valid)} detected the original bug. This is a selected SymPy pilot, not a verdict on all unit testing."
    else:
        failed=any(r['status']=='infrastructure-error' for r in runs)
        status=f"{'Stopped: runner needs attention' if failed else 'Experiment in progress'} · {len(runs)}/80 attempts recorded · {evaluated} evaluated"
        takeaway='The experiment is incomplete. These are measured interim outcomes, not a final comparison; the two policies may cover different issues so far.'
    stats=(f"Write-tests minus no-new-tests: {diff:+.1f} percentage points. Task-cluster bootstrap 95% interval: {interval[0]:+.1f} to {interval[1]:+.1f} points. Exact task-level sign-flip p={pvalue:.4f}. Twenty selected tasks; no equivalence claim."
           if full else 'Paired effect, task-cluster confidence interval, and sign-flip test are withheld until all 80 attempts have evaluable outcomes. Repeated attempts are clustered by issue.')
    if bootstrap_degenerate:
        stats=(f"Observed write-tests minus no-new-tests: {diff:+.1f} percentage points. All 20 task-level differences are identical, so the prespecified task-cluster bootstrap returns a degenerate [{interval[0]:.1f}, {interval[1]:.1f}] interval. This cannot provide useful population uncertainty or establish equivalence. Exact task-level sign-flip p={pvalue:.4f}. Twenty selected tasks; no equivalence claim.")
    regtext=f"Experiment B: {regression['suites_created']} generated suites from {len(tests)} test-arm attempts. {len(valid)} pass on the reference fix; {regression['pass_agent']} pass on their own agent patch. Of the {len(valid)} reference-valid suites, {original} detect the original bug. They detect {regression['mutants_killed']}/{regression['mutants_tested']} tested mutant/suite pairs, covering {regression['distinct_mutants_tested']} distinct mutations across {regression['mutation_issues_tested']} issues. Collection errors do not count as detection. Suites not passing the reference fix are excluded from this score; they can sometimes expose flaws in the reference itself. Existing regression protection in the no-new-tests arm is not measured here."
    regtext+=f" Reference-suite exclusions include {regression['reference_suites_with_failures']} suites with test failures, {regression['reference_suites_with_skips']} with skips, and {regression['reference_suites_with_errors']} with execution or collection errors; these categories can overlap."
    public_runs=json.loads(redact_local_paths(json.dumps([{k:v for k,v in r.items() if k not in ['commands']} for r in runs]),data))
    result=dict(schema_version=1,model=protocol['model'],reasoning_effort=protocol['reasoning_effort'],updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='complete' if full else 'incomplete',status_text=status,takeaway=takeaway,planned=80,task_count=len(manifest['tasks']) if manifest else 0,completed=completed,evaluated=evaluated,
                arms=arms,runs=public_runs,regression=regression,regression_text=regtext,paired_difference_pp=diff,confidence_interval_pp=interval,bootstrap_degenerate=bootstrap_degenerate,sign_flip_p=pvalue,statistical_note=stats,
                chart_caption='20 selected SymPy issues · 2 repetitions per policy · GPT-6 Astra (medium) · 5-minute cap. '+('Complete pilot.' if full else 'Incomplete pilot; policies may cover different issues.'),
                manifest_sha256=hashlib.sha256(mp.read_bytes()).hexdigest() if manifest else None,bundle_available=(OUT/'reproducibility.zip').exists())
    if manifest:
        save(OUT/'tasks.json',[{k:r[k] for k in ['instance_id','repo','base_commit','version','problem_statement','FAIL_TO_PASS','PASS_TO_PASS','fail_nodes','pass_nodes']}|{'mutants':[{k:v for k,v in m.items() if k!='code'} for m in r['mutants']]} for r in manifest['tasks']])
    with (OUT/'runs.csv').open('w',newline='') as f:
        fields=['run_id','instance_id','condition','repetition','status','solved','evaluated','elapsed_seconds','input_tokens','cached_input_tokens','output_tokens',
                'policy_compliant','suite_passes_agent','suite_passes_reference','original_detected_if_reference_valid','mutants_tested','mutants_detected']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in runs:
            record={k:r.get('usage',{}).get(k,r.get(k,'')) for k in fields}
            record['policy_compliant']=r.get('compliance_review',{}).get('compliant','')
            if 'regression' in r:
                reg=r['regression'];reference_valid=reg.get('reference',{}).get('all_pass',False)
                record.update(suite_passes_agent=reg.get('agent',{}).get('all_pass',False),suite_passes_reference=reference_valid)
                if reference_valid:
                    record.update(original_detected_if_reference_valid=caught(reg.get('original',{})),
                                  mutants_tested=len(reg['mutants']),mutants_detected=sum(m['killed'] for m in reg['mutants']))
            writer.writerow(record)
    chart(result)
    a,b=arms.values()
    tweet=(f"AI-written tests: useful?\n\nGPT-6 Astra · 20 SymPy issues · 80 runs\nAcceptance passes:\nNo new tests: {a['solved']}/40\nWrite a test: {b['solved']}/40\n\n{original}/{len(valid)} valid generated suites caught the original bug.\n\nSmall pilot; limits & data:\nhttps://adamruns.com/unit-testing.html" if full else
           f"DRAFT — NOT READY TO POST\nThe pilot is incomplete ({evaluated}/80 attempts evaluated). Wait for the paired results and review the limitations before tweeting.\n")
    (OUT/'tweet.txt').write_text(tweet+'\n')
    save(OUT/'results.json',result)
    print(status);print(takeaway)
    return result


def chart(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bg='#111310';fg='#f1f2e9';muted='#aab09e';lime='#d2fa69';purple='#cec3ff'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':fg,'axes.labelcolor':fg,'xtick.color':muted,'ytick.color':fg})
    fig=plt.figure(figsize=(16,9),dpi=100,facecolor=bg)
    fig.text(.055,.925,'DO AI AGENTS BENEFIT FROM WRITING TESTS?',fontsize=32,fontweight='bold')
    fig.text(.055,.866,'GPT-6 Astra · medium reasoning · ChatGPT subscription · 20 selected SymPy issues',fontsize=17,color=muted)
    if not d['runs']:
        fig.text(.055,.59,'Benchmark preparation',fontsize=38,color=lime,fontweight='bold')
        fig.text(.055,.49,'20 issues × 2 testing policies × 2 repetitions = 80 planned runs',fontsize=22)
        fig.text(.055,.36,'No measured model results yet.',fontsize=25,color=muted)
    else:
        a,b=d['arms'].values()
        timing=lambda arm:f"{arm['mean_attempt_seconds']:.0f} sec" if arm['attempted'] else 'pending'
        fig.text(.055,.798,f"Mean agent time: no new tests {timing(a)}  /  write a test {timing(b)}",fontsize=15,color=muted)
        ax=fig.add_axes([.21,.39,.66,.35],facecolor=bg)
        values=[];labels=[]
        for key in LABELS:
            arm=d['arms'][key];values.append(100*arm['solved']/arm['evaluated'] if arm['evaluated'] else 0);labels.append(LABELS[key])
        ax.barh([1,0],values,color=[purple,lime],height=.38)
        ax.set_yticks([1,0],labels,fontsize=22);ax.set_xlim(0,120);ax.set_xticks([0,25,50,75,100],['0%','25%','50%','75%','100%'],fontsize=15)
        ax.set_xlabel('Attempts passing every withheld check',fontsize=16,labelpad=12)
        for y,(key,v) in enumerate(zip(LABELS,values)):
            a=d['arms'][key];label=f"{a['solved']}/{a['evaluated']} ({v:.0f}%)" if a['evaluated'] else 'No scored attempts'
            ax.text(min(v+2,103),1-y,label,va='center',fontsize=24,fontweight='bold',color=fg)
        for spine in ax.spines.values():spine.set_visible(False)
        ax.tick_params(length=0);ax.set_axisbelow(True);ax.xaxis.grid(True,color='#30362b',linewidth=.6)
        r=d['regression'];fig.text(.055,.225,f"{r['original_caught']}/{r['valid_reference']}",fontsize=37,fontweight='bold',color=lime)
        fig.text(.21,.255,'Reference-valid generated suites',fontsize=16)
        fig.text(.21,.218,'that detect the original bug',fontsize=16,color=muted)
        fig.text(.59,.255,f"{r['mutants_killed']}/{r['mutants_tested']} mutant/suite pairs detected",fontsize=17)
        fig.text(.59,.218,f"{r['suites_created']} suites generated; {r['valid_reference']} reference-valid",fontsize=15,color=muted)
        if d['confidence_interval_pp'] is not None:
            low,high=d['confidence_interval_pp']
            note=(f"Observed difference: {d['paired_difference_pp']:+.1f} pp · Identical task differences; bootstrap interval is uninformative."
                  if d.get('bootstrap_degenerate') else f"Acceptance-rate difference: {d['paired_difference_pp']:+.1f} pp  ·  Task-cluster 95% interval: {low:+.1f} to {high:+.1f} pp")
            fig.text(.055,.154,note,fontsize=14,color=muted)
    note='Small pilot · 2 repeats per policy. Existing tests allowed in both policies.' if d['status']=='complete' else 'INCOMPLETE PILOT — interim counts; policies may cover different issues.'
    fig.text(.055,.105,note,fontsize=17,color=muted)
    fig.text(.055,.055,'ADAM SMITH / @TOKENSMAX',fontsize=12,fontweight='bold',color=lime)
    fig.text(.62,.055,'adamruns.com/unit-testing.html',fontsize=14)
    fig.savefig(OUT/'results-chart.png',facecolor=bg);fig.savefig(OUT/'results-chart.svg',facecolor=bg);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',required=True,type=Path);a=p.parse_args();build(a.data.resolve())
