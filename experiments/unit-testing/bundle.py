#!/usr/bin/env python3
"""Package experiment evidence after every run has a policy audit. Never copy auth."""
import argparse,hashlib,json,re,tempfile,zipfile
from pathlib import Path
import report
HERE=Path(__file__).resolve().parent

def scrub(text,data):
    text=report.redact_local_paths(text,data)
    if re.search(r'\bsk-[A-Za-z0-9_-]{24,}|"(?:access_token|refresh_token)"\s*:\s*"[^"\s]+',text):
        raise ValueError('Potential credential detected; refusing export')
    return text

def bundle(data):
    paths=sorted((data/'runs').glob('*/result.json'))
    if len(paths)!=80:raise SystemExit('Only a complete 80-attempt pilot may be bundled for publication.')
    if any('compliance_review' not in json.loads(p.read_text()) for p in paths):raise SystemExit('Review policy compliance for every run before publishing trajectories.')
    output=report.OUT;target=output/'reproducibility.zip'
    with tempfile.NamedTemporaryFile(dir=output,suffix='.zip',delete=False) as f:temp=Path(f.name)
    checksums={}
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        def add(name,text):
            cleaned=scrub(text,data)
            if name.endswith('.xml'):
                for placeholder in ['PYTHON','TRIAL','HOME','EXPERIMENT_DATA']:
                    cleaned=cleaned.replace('<'+placeholder+'>','&lt;'+placeholder+'&gt;')
            content=cleaned.encode();z.writestr(name,content);checksums[name]=hashlib.sha256(content).hexdigest()
        for p in sorted(HERE.iterdir()):
            if p.is_file() and p.suffix in ['.py','.json','.md','.txt']:add('experiments/unit-testing/'+p.name,p.read_text())
        for name in ['manifest.json','selection-audit.json','environment.json']:add('data/'+name,(data/name).read_text())
        for logfile in sorted((data/'preflight').glob('*/*')):
            if logfile.suffix in ['.log','.xml']:
                add('data/preflight/'+logfile.parent.name+'/'+logfile.name,logfile.read_text())
        for root in sorted((data/'runs').iterdir()):
            if not (root/'result.json').exists():continue
            for name in ['result.json','started.json','prompt.txt','production.patch','all.patch','test_agent_regression.py','trajectory.jsonl']:
                p=root/name
                if p.exists():add('data/runs/'+root.name+'/'+name,p.read_text())
            for p in sorted(root.iterdir()):
                if p.suffix in ['.log','.xml'] and p.name!='stderr.log':
                    add('data/runs/'+root.name+'/'+p.name,p.read_text())
        for name in ['results.json','runs.csv','tasks.json','tweet.txt','findings.json']:
            p=output/name
            if p.exists():add('public/'+name,p.read_text())
        add('REPRODUCE.txt','Public experiment evidence. Local paths are redacted as <PYTHON>, <TRIAL>, <HOME>, and <EXPERIMENT_DATA>. Credentials are not included.\n\nCheck the recorded results without inference:\npython3 experiments/unit-testing/verify_results.py --data data --public public\n\nFollow experiments/unit-testing/README.md to run new attempts. Preserve this evidence and use a fresh data directory. Reference patches and evaluation tests are included here for independent review; agents were denied access during inference. Dataset: SWE-bench Verified. Upstream SymPy license included. Public benchmark pass rates are not a universal measure of patch quality.\n')
        z.writestr('SHA256SUMS.json',json.dumps(checksums,indent=2)+'\n')
    temp.replace(target);report.build(data)
    print('Bundle:',target,'bytes',target.stat().st_size)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args();bundle(a.data.resolve())
