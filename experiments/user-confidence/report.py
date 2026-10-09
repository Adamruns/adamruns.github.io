#!/usr/bin/env python3
"""Analysis and shareable artifacts; no conclusions from an unfinished schedule."""
import argparse, collections, csv, datetime, hashlib, json, math, random, re, statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]/'assets/experiments/user-confidence'
LABELS={'no-diagnosis':'No added diagnosis','correct-diagnosis':'Correct diagnosis','tentative-wrong':'Wrong · “I suspect”','confident-wrong':'Wrong · “I’ve confirmed”'}


def save(path, data):
    path.write_text(json.dumps(data,indent=2)+'\n')


def redact(text, data):
    manifest=json.loads((data/'manifest.json').read_text())
    text=text.replace(manifest['python'],'<PYTHON>')
    text=text.replace(str(data),'<EXPERIMENT_DATA>')
    text=re.sub(r'/(?:private/)?var/folders/[^\s"\']+/confidence-trial-[^/\s"\']+/repo','<TRIAL>',text)
    return text.replace(str(Path.home()),'<HOME>')


def contrast(runs, treatment, control, repetitions=2):
    pairs=collections.defaultdict(dict)
    for r in runs:
        if r['evaluated']:pairs[(r['instance_id'],r['repetition'])][r['condition']]=int(r['solved'])
    task_values=collections.defaultdict(list);wins=losses=ties=0
    for (iid,rep),pair in pairs.items():
        if treatment in pair and control in pair:
            v=pair[treatment]-pair[control];task_values[iid].append(v)
            wins+=v>0;losses+=v<0;ties+=v==0
    if len(task_values)!=20 or any(len(v)!=repetitions for v in task_values.values()):return None
    values=[statistics.mean(task_values[k]) for k in sorted(task_values)]
    rng=random.Random(90210)
    samples=sorted(100*statistics.mean(rng.choices(values,k=len(values))) for _ in range(20000))
    dist={0:1}
    for v in values:
        n=round(v*repetitions); new=collections.Counter()
        for total,count in dist.items():new[total+n]+=count;new[total-n]+=count
        dist=new
    threshold=abs(sum(round(v*repetitions) for v in values))
    p=sum(count for total,count in dist.items() if abs(total)>=threshold)/sum(dist.values())
    return dict(treatment=treatment,control=control,difference_pp=100*statistics.mean(values),
        cluster_bootstrap_95_pp=[samples[499],samples[19499]],bootstrap_degenerate=len(set(values))==1,
        exact_task_sign_flip_p=p,treatment_only_pass=wins,control_only_pass=losses,same_outcome=ties,
        nonzero_task_count=sum(v!=0 for v in values),
        task_effects={k:statistics.mean(v) for k,v in sorted(task_values.items())})


def wilson(k,n):
    if not n:return None
    z=1.95996398454;p=k/n;den=1+z*z/n
    middle=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [100*(middle-half),100*(middle+half)]


def analyze(manifest, raw):
    runs=[dict(r,solved=bool(r.get('acceptance',{}).get('all_pass')),evaluated='acceptance' in r and not r.get('evaluation_error')) for r in raw]
    full=len(runs)==len(manifest['schedule']) and all(r['evaluated'] for r in runs)
    arms={}
    for condition in LABELS:
        arm=[r for r in runs if r['condition']==condition];timed=[r for r in arm if r['status'] in ('completed','timeout')]
        solved=sum(r['solved'] for r in arm);evaluated=sum(r['evaluated'] for r in arm)
        reviews=[r['diagnosis_review'] for r in arm if 'diagnosis_review' in r]
        arms[condition]=dict(label=LABELS[condition],scheduled=40,recorded=len(arm),evaluated=evaluated,solved=solved,
            timeouts=sum(r['status']=='timeout' for r in arm),errors=sum(r['status']=='infrastructure-error' or bool(r.get('evaluation_error')) for r in arm),
            mean_seconds=statistics.mean(r['elapsed_seconds'] for r in timed) if timed else None,
            median_seconds=statistics.median(r['elapsed_seconds'] for r in timed) if timed else None,
            total_seconds=sum(r['elapsed_seconds'] for r in timed),
            usage_reports=sum('input_tokens' in r.get('usage',{}) for r in arm),
            usage_unavailable=sum('input_tokens' not in r.get('usage',{}) for r in arm),
            **{k:sum(r.get('usage',{}).get(k,0) for r in arm) for k in ('input_tokens','cached_input_tokens','output_tokens')},
            descriptive_marginal_wilson_95_percent=wilson(solved,evaluated),
            reviewed=len(reviews),diagnosis_categories=dict(collections.Counter(r['category'] for r in reviews)),
            compliance_reviewed=sum('compliance_review' in r for r in arm),
            compliant=sum(r.get('compliance_review',{}).get('compliant',False) for r in arm))
    contrasts={}
    if full:
        for name,treatment,control in [('confidence','confident-wrong','tentative-wrong'),('correct-vs-none','correct-diagnosis','no-diagnosis'),('tentative-vs-none','tentative-wrong','no-diagnosis'),('confident-vs-none','confident-wrong','no-diagnosis')]:
            contrasts[name]=contrast(runs,treatment,control)
    return dict(schema_version=1,status='complete' if full else 'incomplete',model=manifest['protocol']['model'],reasoning_effort=manifest['protocol']['reasoning_effort'],
        planned=len(manifest['schedule']),recorded=len(runs),evaluated=sum(r['evaluated'] for r in runs),task_count=len(manifest['tasks']),arms=arms,contrasts=contrasts,
        review_complete=all('compliance_review' in r and ('wrong' not in r['condition'] or 'diagnosis_review' in r) for r in runs) and full,
        interval_note='Primary effect intervals resample 20 issue clusters, preserving both repetitions. Marginal Wilson intervals are descriptive only and ignore within-issue dependence; they are not the inferential comparison. Nonsignificance does not establish equivalence.',
        runs=[{k:v for k,v in r.items() if k not in ('commands','messages')} for r in runs])


def build(data, output=OUT):
    output.mkdir(parents=True,exist_ok=True);manifest=json.loads((data/'manifest.json').read_text())
    raw=[json.loads(p.read_text()) for p in sorted((data/'runs').glob('*/result.json'))]
    result=analyze(manifest,raw)
    result.update(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest_sha256=hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest())
    save(output/'results.json',json.loads(redact(json.dumps(result),data)))
    evidence_notes=json.loads((HERE/'evidence-notes.json').read_text())
    save(output/'evidence-notes.json',evidence_notes)
    save(output/'tasks.json',[{k:r[k] for k in ('instance_id','repo','base_commit','version','issue_text','diagnosis','fail_nodes','pass_nodes')} | {'evidence_note':evidence_notes.get(r['instance_id'])} for r in manifest['tasks']])
    fields=['run_id','instance_id','condition','repetition','status','evaluated','solved','elapsed_seconds','input_tokens','cached_input_tokens','output_tokens','diagnosis_category','explicit_rejection','compliant']
    with (output/'runs.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in result['runs']:
            row={k:r.get(k,r.get('usage',{}).get(k,'')) for k in fields}
            review=r.get('diagnosis_review');row['diagnosis_category']=review['category'] if review else ''
            row['explicit_rejection']=review['category']=='explicit-rejection' if review else ''
            row['compliant']=r.get('compliance_review',{}).get('compliant','');writer.writerow(row)
    if result['status']=='complete':
        a=result['arms']
        tweet=(f"I confidently gave AI the wrong diagnosis.\nIt still passed {a['confident-wrong']['solved']}/40 debugging attempts.\n\nGPT-6 Astra · 20 bugs · 160 runs\nHidden-check passes:\nNone added: {a['no-diagnosis']['solved']}/40\nCorrect: {a['correct-diagnosis']['solved']}/40\nWrong, unsure: {a['tentative-wrong']['solved']}/40\nWrong + certain: {a['confident-wrong']['solved']}/40\n\nSmall pilot + data: https://adamruns.com/user-confidence.html")
    else:tweet=f"DRAFT — INCOMPLETE EXPERIMENT\n{result['recorded']}/{result['planned']} attempts recorded. Do not post interim arm comparisons as final findings.\n"
    (output/'tweet.txt').write_text(tweet+'\n');chart(result,output)
    print(result['status'],result['recorded'],'/',result['planned'])
    for key,value in result['arms'].items():print(key,value['solved'],'/',value['evaluated'],'mean',value['mean_seconds'])
    return result


def chart(result,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bg='#090d18';fg='#f3f5ff';muted='#acb8d5';blue='#88b2ff';pink='#f3b1c6'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':fg,'axes.labelcolor':muted,'xtick.color':muted,'ytick.color':fg})
    fig=plt.figure(figsize=(16,9),dpi=100,facecolor=bg)
    fig.text(.045,.925,'CAN A CONFIDENTLY WRONG USER DERAIL AI?',fontsize=29,fontweight='bold')
    fig.text(.045,.865,'GPT-6 Astra · 20 selected SymPy bugs · 4 prompts · 2 repeats · 160 runs',fontsize=19,color=muted)
    if result['status']!='complete':
        fig.text(.045,.55,f"Experiment in progress: {result['recorded']}/160",fontsize=34,color=blue)
        fig.text(.045,.44,'No final comparison until every scheduled attempt is graded.',fontsize=22)
    else:
        ax=fig.add_axes([.305,.30,.64,.47],facecolor=bg)
        colors=['#8d9ab5',blue,'#d3b1f3',pink]
        for i,(key,label) in enumerate(LABELS.items()):
            a=result['arms'][key];value=100*a['solved']/a['evaluated'];y=3-i
            ax.barh(y,value,height=.48,color=colors[i])
            ax.text(value+2,y,f"{a['solved']}/40  ({value:g}%)",va='center',fontsize=23,fontweight='bold')
            ax.text(138,y,f"{a['mean_seconds']:.0f} s",ha='center',va='center',fontsize=21,color=muted)
        ax.text(138/150,1.055,'Mean wall time',transform=ax.transAxes,ha='center',fontsize=14,color=muted)
        ax.set_yticks([3,2,1,0],list(LABELS.values()),fontsize=21);ax.set_xlim(0,150)
        ax.set_xticks([0,25,50,75,100],['0%','25%','50%','75%','100%'],fontsize=15)
        ax.set_xlabel('Attempts passing every withheld acceptance check',fontsize=16,labelpad=12)
        ax.tick_params(length=0,pad=12);ax.set_axisbelow(True);ax.xaxis.grid(True,color='#293248',linewidth=.6)
        for spine in ax.spines.values():spine.set_visible(False)
        effect=result['contrasts']['confidence'];low,high=effect['cluster_bootstrap_95_pp']
        note=f"Confidence effect: {effect['difference_pp']:+.1f} percentage points"
        if effect['bootstrap_degenerate']:
            note+=' · identical task effects; bootstrap interval uninformative.'
        elif effect['nonzero_task_count']==1:
            note+=' · only 1 of 20 issues differed; no established advantage.'
        else:
            note+=f' · task-cluster 95% interval: {low:+.1f} to {high:+.1f} points'
        fig.text(.045,.19,note,fontsize=17,color=fg)
    fig.text(.045,.12,'20 historical issues · one model · five-minute cap. Results describe this selected pilot.',fontsize=16,color=muted)
    fig.text(.045,.052,'ADAM SMITH / @TOKENSMAX',fontsize=13,fontweight='bold',color=blue)
    fig.text(.58,.052,'adamruns.com/user-confidence.html',fontsize=16)
    fig.savefig(output/'results-chart.png',facecolor=bg);fig.savefig(output/'results-chart.svg',facecolor=bg);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,default=OUT);a=p.parse_args();build(a.data.resolve(),a.output)
