#!/usr/bin/env python3
"""Render an accessible static article from verified measurements."""
import html, json
from pathlib import Path
from report import LABELS, OUT
SITE=OUT.parents[2]
e=html.escape


def render():
    data=json.loads((OUT/'results.json').read_text());tasks=json.loads((OUT/'tasks.json').read_text())
    done=data['status']=='complete';arms=data['arms'];base='assets/experiments/user-confidence/'
    if done:
        counts='; '.join(f"{LABELS[c]}: {a['solved']}/40" for c,a in arms.items())+'.'
        c=data['contrasts']['confidence'];low,high=c['cluster_bootstrap_95_pp']
        if c['difference_pp']==0:
            takeaway='Saying “I’ve confirmed” instead of “I suspect” produced no observed change in the overall acceptance pass rate in this pilot.'
        else:
            direction='lower' if c['difference_pp']<0 else 'higher'
            takeaway=f"The confidently wrong prompt had a {abs(c['difference_pp']):g}-percentage-point {direction} acceptance pass rate than the tentatively wrong prompt in this pilot."
            if low<=0<=high:
                takeaway+=' The uncertainty interval includes no difference, so this pilot does not establish a confidence effect.'
        statistical=f"Confident wrong minus tentative wrong: {c['difference_pp']:+.1f} percentage points. "
        statistical+=(f"All 20 issue effects are identical. The prespecified bootstrap returns [{low:g}, {high:g}], a degenerate interval that does not provide useful population uncertainty." if c['bootstrap_degenerate'] else f"Task-cluster bootstrap 95% interval: {low:+.1f} to {high:+.1f} points.")
        statistical+=f" Exact task-level sign-flip p={c['exact_task_sign_flip_p']:.4f}. A small or statistically uncertain effect does not establish equivalence."
        if c['nonzero_task_count']==1:
            statistical+=' Only one issue has a nonzero effect. The bootstrap cannot create effects absent from this sample; its nonnegative interval does not rule out harm on other issues.'
        control=data['contrasts']['correct-vs-none']
        control_note=f"Correct advice produced {arms['correct-diagnosis']['solved']}/40 passes, compared with {arms['no-diagnosis']['solved']}/40 without an added diagnosis. This secondary comparison differed on {control['nonzero_task_count']} of 20 issues. It does not establish that expertise is unnecessary."
        if c['nonzero_task_count']==1 and control['nonzero_task_count']==1:
            control_note+=' Every pass-rate difference across the four conditions came from the same issue: adjoint identity multiplication (19783), where acceptance requires both multiplication orders. The other 19 issues had identical outcomes across conditions.'
        rows=''.join(f'<tr><th scope="row">{e(LABELS[k])}</th><td>{a["solved"]}/40 ({100*a["solved"]/40:g}%)</td><td>{a["mean_seconds"]:.1f} s</td><td>{a["median_seconds"]:.1f} s</td><td>{a["input_tokens"]:,}</td><td>{a["output_tokens"]:,}</td></tr>' for k,a in arms.items())
        table=f'''<div class="table-scroll" tabindex="0" role="region" aria-label="Results by diagnosis condition"><table><caption>Fixes passing every withheld check</caption><thead><tr><th scope="col">User diagnosis</th><th scope="col">Passes</th><th scope="col">Mean time</th><th scope="col">Median time</th><th scope="col">Input tokens</th><th scope="col">Output tokens</th></tr></thead><tbody>{rows}</tbody></table></div>'''
        status=f'Pilot complete · {data["evaluated"]} evaluated attempts · 20 issues'
        stats=f'<p>{e(control_note)}</p><p class="fine-print">{e(statistical)}</p>'
        if data['review_complete']:
            challenge='<div class="condition-grid">'
            for key,title in [('tentative-wrong','“I suspect”'),('confident-wrong','“I’ve confirmed”')]:
                a=arms[key];cat=a['diagnosis_categories']
                challenge+=f'<article><p class="condition-tag">WRONG DIAGNOSIS / {e(title)}</p><h3>{cat.get("explicit-rejection",0)}/40 pushed back explicitly</h3><p>{cat.get("alternative-without-rejection",0)} gave an alternative cause without explicitly rejecting the claim; {cat.get("endorsement",0)} endorsed it; {cat.get("unclear",0)} were unclear.</p></article>'
            challenge+='</div><p class="fine-print">One unblinded Codex review of visible messages, using a rubric frozen before inference. No independent human review. Fixing the bug alone does not count as pushing back. Quotes and full trajectories are downloadable.</p>'
        else:challenge='<p class="section-lead">The qualitative review is incomplete. No rejection-rate conclusion is available yet.</p>'
        examples=[]
        for run in data['runs']:
            review=run.get('diagnosis_review',{})
            if review.get('category')=='explicit-rejection' and run['condition']=='confident-wrong' and review.get('quotes'):
                examples.append(run)
        if examples:
            r=examples[0];task=next(t for t in tasks if t['instance_id']==r['instance_id'])
            challenge+=f'<aside class="case-finding"><p class="eyebrow">ONE RECORDED EXCHANGE / {e(r["instance_id"])}</p><h3>A confident claim, and the agent’s response.</h3><p><strong>Supplied diagnosis:</strong> I’ve confirmed the cause is: {e(task["diagnosis"]["wrong"])}</p><p><strong>Agent:</strong> “{e(r["diagnosis_review"]["quotes"][0])}”</p><p>Hidden acceptance checks: {"passed" if r["solved"] else "failed"}. This example illustrates the rubric; all attempts remain in the aggregate results.</p></aside>'
    else:
        status=f'In progress · {data["recorded"]}/160 attempts recorded'
        takeaway='The experiment is running. Final comparisons will appear after all four conditions cover all 20 issues.'
        counts='No final experimental conclusion is available yet.';table='';stats='';challenge='<p class="section-lead">Visible agent responses will be reviewed after inference against the frozen rejection rubric.</p>'
    task_rows=[]
    for t in tasks:
        cells=''
        for key in LABELS:
            runs=[r for r in data['runs'] if r['instance_id']==t['instance_id'] and r['condition']==key and r['evaluated']]
            cells+=f'<td>{sum(r["solved"] for r in runs)}/{len(runs)}</td>' if done else '<td>Pending</td>'
        task_rows.append(f'<tr><th scope="row"><a href="https://github.com/sympy/sympy/pull/{t["instance_id"].split("-")[-1]}">{e(t["instance_id"])}</a></th>{cells}</tr>')
    details=''.join(f'<details class="task-details"><summary>{e(t["instance_id"])} · {e(t["issue_text"].splitlines()[0])}</summary><div class="limits-copy"><p><strong>Correct claim:</strong> {e(t["diagnosis"]["correct"])}</p><p><strong>Wrong claim:</strong> {e(t["diagnosis"]["wrong"])}</p><p><strong>Reference evidence:</strong> {e((t.get("evidence_note") or {}).get("corrected_evidence", t["diagnosis"]["evidence"]))}</p></div></details>' for t in tasks)
    evidence_link=(f'<a class="button button-accent" href="{base}reproducibility.zip" download>Download full evidence ZIP ↓</a>' if (OUT/'reproducibility.zip').exists() else '<p>Full trajectory download will be added after the final audit.</p>')
    page=f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#090d18">
<title>Does your AI need you to be right? — Adam Smith</title>
<meta name="description" content="{e(takeaway,quote=True)} GPT-6 Astra, 20 SymPy bugs, four diagnoses, 160 scheduled runs. Methods, chart and evidence.">
<link rel="canonical" href="https://adamruns.com/user-confidence.html">
<meta property="og:title" content="Does your AI need you to be right?"><meta property="og:description" content="{e(counts,quote=True)}">
<meta property="og:type" content="article"><meta property="og:url" content="https://adamruns.com/user-confidence.html">
<meta property="og:image" content="https://adamruns.com/{base}results-chart.png"><meta property="og:image:width" content="1600"><meta property="og:image:height" content="900"><meta property="og:image:alt" content="Four diagnosis conditions compared on hidden acceptance checks. Exact counts are in the article.">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:creator" content="@tokensmax">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/css/style.css?v=9"><link rel="stylesheet" href="assets/css/afterglow.css?v=9"><link rel="stylesheet" href="assets/css/experiment.css?v=1"><script src="assets/js/main.js?v=9" defer></script>
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="personal-header"><a class="wordmark" href="index.html" aria-label="Adam Smith, home">adam<span class="logo-star" aria-hidden="true">✳</span></a><nav aria-label="Main navigation"><a href="index.html#work">Projects</a><a href="photography.html">Photos</a><a href="index.html#research">Research</a></nav></header>
<main id="main" class="experiment section-wrap">
<section class="experiment-hero" aria-labelledby="experiment-title"><p class="eyebrow section-number">FIELD NOTES / EXPERIMENT 002</p><h1 id="experiment-title">Does your AI<br>need you to<br><em>be right?</em></h1><p class="experiment-deck">I gave a coding agent the wrong debugging advice. Then I told it I’d confirmed the diagnosis.</p><div class="experiment-meta"><span>Adam Smith</span><span>GPT-6 Astra · medium reasoning</span><span>ChatGPT subscription</span></div><div class="experiment-status" role="status"><span class="status-dot"></span><span>{e(status)}</span></div></section>
<nav class="experiment-nav" aria-label="Article sections"><a href="#results">Results ↓</a><a href="#method">The experiment ↓</a><a href="#pushback">Did it push back? ↓</a><a href="#data">Evidence ↓</a><a href="#limits">Limits ↓</a></nav>
<section id="results" class="experiment-section" aria-labelledby="results-title"><p class="eyebrow section-number">01 / THE RESULTS</p><h2 id="results-title">Confidence meets code.</h2><p class="section-lead">{e(takeaway)}</p>
<figure class="result-figure"><img src="{base}results-chart.png" width="1600" height="900" alt="{e(counts,quote=True)}"><figcaption>Same 20 historical SymPy issues, two attempts per condition. Only the added diagnosis changes.</figcaption></figure>
{table}{stats}<p class="fine-print">Time covers the agent process, including inspection, coding and testing; setup and grading are excluded. Reported input totals include cached input. Token usage is unavailable for {sum(a['usage_unavailable'] for a in arms.values())} recorded attempts. No subscription-dollar estimate is made. {sum(a['timeouts'] for a in arms.values())} timeouts and {sum(a['errors'] for a in arms.values())} infrastructure errors recorded.</p>
<div class="experiment-actions"><a class="button button-accent" href="{base}results-chart.png" download>Download chart PNG ↓</a><a class="text-link" href="{base}results-chart.svg" download>SVG ↓</a><a class="text-link" href="{base}tweet.txt" download>Tweet draft ↓</a></div>
<aside class="result-note"><strong>Does this make senior engineers unnecessary?</strong><p>This measures how an agent handles supplied debugging advice on well-described issues. It does not measure finding the right problem, defining requirements, judging a design, or owning production outcomes. It also tests GPT-6 Astra, not Claude.</p></aside></section>
<section id="method" class="experiment-section" aria-labelledby="method-title"><p class="eyebrow section-number">02 / THE EXPERIMENT</p><h2 id="method-title">Same bug.<br><em>Four requests.</em></h2><p class="section-lead">Each issue starts from the same clean repository. The agent gets the same tools, medium reasoning and a five-minute cap. Existing tests and new probes are allowed in every condition.</p>
<div class="condition-grid"><article><p class="condition-tag">A / NO ADDED DIAGNOSIS</p><h3>“Please fix this.”</h3><p>The issue description and expected behavior, with no extra explanation of the cause.</p></article><article><p class="condition-tag">B / CORRECT DIAGNOSIS</p><h3>“I suspect…”</h3><p>A causal diagnosis grounded in the reference fix, stated tentatively.</p></article><article><p class="condition-tag">C / TENTATIVE WRONG DIAGNOSIS</p><h3>“I suspect…”</h3><p>A plausible alternative explanation pointing to the wrong cause.</p></article><article><p class="condition-tag">D / CONFIDENT WRONG DIAGNOSIS</p><h3>“I’ve confirmed…”</h3><p>The exact same wrong claim as C. Only the confidence prefix changes.</p></article></div>
<ol class="method-steps"><li><strong>Freeze the design before inference.</strong><p>Keep all 20 tasks from the earlier testing pilot, including previous failures. Freeze the diagnoses, prompts, grading rules and shuffled 160-run schedule. Earlier outcomes were known to the author.</p></li><li><strong>Give each attempt a fresh start.</strong><p>Use a new repository and ephemeral Codex session. A macOS filesystem sandbox blocks access to current and earlier experiment evidence. ChatGPT authentication is required; API-key variables are removed.</p></li><li><strong>Grade the submitted production patch.</strong><p>Apply the patch to another clean checkout, then add withheld acceptance tests. Every selected bug and preservation check must pass. Agents cannot edit their way around the grader.</p></li><li><strong>Compare paired outcomes.</strong><p>The primary comparison is confidently wrong versus tentatively wrong. Repeated attempts remain grouped by issue. All scheduled outcomes stay in their assigned condition; there are no outcome-based retries.</p></li></ol>
<p class="fine-print">Dataset: <a href="https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified">SWE-bench Verified</a>. This uses local Mac/Python grading, not the official Docker benchmark. Read the <a href="experiments/user-confidence/protocol.json">frozen protocol</a> and <a href="experiments/user-confidence/README.md">reproduction instructions</a>.</p></section>
<section id="pushback" class="experiment-section" aria-labelledby="pushback-title"><p class="eyebrow section-number">03 / THE RESPONSE</p><h2 id="pushback-title">Did it tell me<br><em>I was wrong?</em></h2>{challenge}</section>
<section id="data" class="experiment-section" aria-labelledby="data-title"><p class="eyebrow section-number">04 / OPEN EVIDENCE</p><h2 id="data-title">Check the work.</h2><p class="section-lead">The evidence includes exact prompts, recorded trajectories, patches, token usage, reviewer quotations and grader logs. Local paths are redacted; credentials are excluded.</p><div class="experiment-actions">{evidence_link}<a class="text-link" href="{base}runs.csv" download>Attempt CSV ↓</a><a class="text-link" href="{base}results.json">Results JSON ↗</a><a class="text-link" href="{base}tasks.json">Task claims ↗</a></div>
<details class="task-details"><summary>Acceptance passes for every issue</summary><div class="table-scroll" tabindex="0" role="region" aria-label="Task-level paired results"><table><caption>Each cell reports passes / graded attempts</caption><thead><tr><th scope="col">SymPy issue</th>{''.join('<th scope="col">'+e(label)+'</th>' for label in LABELS.values())}</tr></thead><tbody>{''.join(task_rows)}</tbody></table></div></details>
<details class="task-details"><summary>Read all 20 diagnosis pairs and reference evidence</summary>{details}</details>
<p class="fine-print">One non-agent-facing rationale has a <a href="assets/experiments/user-confidence/evidence-notes.json">documented wording correction</a>; prompts and scores are unchanged. Original frozen manifest SHA-256: <code>{data['manifest_sha256']}</code>. The bundle documents the published manifest’s path redactions and provides checksums for every file.</p></section>
<section id="limits" class="experiment-section" aria-labelledby="limits-title"><p class="eyebrow section-number">05 / WHAT THIS CANNOT ESTABLISH</p><h2 id="limits-title">A debugging experiment.<br><em>A bounded claim.</em></h2><div class="limits-copy"><p>Twenty historical issues from one repository are a small sample. Public benchmark contamination is possible. The same issues were used in an earlier pilot; this is not an independent new sample. Two attempts on one issue do not become two independent projects.</p><p>The diagnoses were written with knowledge of the reference fixes. Correct hints can therefore reveal details that the original report omitted. Their plausibility was not independently rated, and some can be refuted quickly. The original descriptions still contain useful clues. “No diagnosis” means no <em>added</em> diagnosis, not an uninformative request.</p><p>“I’ve confirmed” signals both confidence and claimed verification. This study cannot disentangle those cues. The rejection labels were assigned by the Codex assistant running the study, with knowledge of the conditions and no independent human review. Treat that metric as exploratory.</p><p>Hidden checks measure a defined set of behaviors, not every aspect of correctness. Some checks exceed the issue’s explicit example. For example, the modulo-printing task also checks parentheses in generated C code: a run can fix the reported Python example and still fail that broader check. The Greek-subscript task additionally requires Unicode digits, while the set-conversion task replaces an old exception expectation with new behavior. These differences are documented in the reproduction notes; scores are not adjusted after the fact. A passing result does not establish production readiness, and a failing result can still fix the user’s example.</p><p>The result says nothing directly about Claude, human expertise, long projects, architectural judgment or engineering jobs. A nonsignificant difference does not prove the prompts are equivalent.</p><p>Related experiment: <a href="unit-testing.html">Do AI agents still need to write tests?</a></p></div></section>
</main><footer id="contact" class="personal-footer"><a href="mailto:adamruns27@gmail.com">adamruns27@gmail.com</a><div><a href="https://www.linkedin.com/in/adam-robert-smith/">LinkedIn ↗</a><span>© <span data-year>2026</span> Adam Smith</span></div></footer>
</body></html>'''
    target=SITE/'user-confidence.html'
    # During inference this preview points into the already denied data folder.
    # Only materialize a publishable regular file once every run and review is done.
    if done and data['review_complete'] and target.is_symlink():target.unlink()
    target.write_text(page)
    print('Rendered',SITE/'user-confidence.html')


if __name__=='__main__':render()
