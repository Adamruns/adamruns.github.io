#!/usr/bin/env python3
"""Publish only reviewed experiment evidence, with path redactions and checksums."""
import argparse, hashlib, json, re, tempfile, zipfile
from pathlib import Path
import report
import verify_results
HERE=Path(__file__).resolve().parent


def bundle(data, output):
    verify_results.verify(data,output)
    sums={}
    def cleaned(text, name):
        text=report.redact(text,data)
        if re.search(r'\bsk-[A-Za-z0-9_-]{24,}|"(?:access_token|refresh_token)"\s*:\s*"[^"\s]+',text):
            raise ValueError('Potential credential; refusing export')
        if name.endswith('.xml'):
            for word in ('PYTHON','TRIAL','HOME','EXPERIMENT_DATA'):text=text.replace('<'+word+'>','&lt;'+word+'&gt;')
        return text
    with tempfile.NamedTemporaryFile(dir=output,suffix='.zip',delete=False) as f:temp=Path(f.name)
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        def add(name,text):
            content=cleaned(text,name).encode();z.writestr(name,content);sums[name]=hashlib.sha256(content).hexdigest()
        for path in sorted(HERE.iterdir()):
            if path.suffix in ('.py','.json','.md','.txt'):add('experiments/user-confidence/'+path.name,path.read_text())
        for name in ('manifest.json','preflight.json','environment.json','sandbox-audit.json'):add('data/'+name,(data/name).read_text())
        original=hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest()
        add('data/manifest-redaction.json',json.dumps(dict(original_sha256=original,published_sha256=sums['data/manifest.json'],note='Absolute local paths in manifest prompts and interpreter location were replaced before publication; launch records retain the original frozen digest.'),indent=2)+'\n')
        for path in sorted((data/'preflight').glob('*/*')):
            if path.suffix in ('.xml','.log'):add('data/preflight/'+path.parent.name+'/'+path.name,path.read_text())
        for root in sorted((data/'runs').iterdir()):
            if not (root/'result.json').exists():continue
            for name in ('result.json','started.json','prompt.txt','trajectory.jsonl','production.patch','all.patch','acceptance.xml','acceptance.log'):
                # Keep CRLF in the recorded prompt identical to its manifest value.
                add('data/runs/'+root.name+'/'+name,(root/name).read_bytes().decode('utf-8'))
        for name in ('results.json','runs.csv','tasks.json','tweet.txt','evidence-notes.json'):add('public/'+name,(output/name).read_text())
        add('REPRODUCE.txt','This bundle contains recorded evidence, not new inference. Local paths are redacted. No credentials or auth files are included.\n\nVerify checksums in SHA256SUMS.json, then run:\npython3 experiments/user-confidence/verify_results.py --data data --public public\n\nRead experiments/user-confidence/README.md for methodology and re-execution. Raw trajectories, patches, grader logs/XML, task claims and reference/test patches are included. Agents could not read these during inference. Manifest path redactions are documented in data/manifest-redaction.json. No Claude model or human engineer is evaluated.\n')
        z.writestr('SHA256SUMS.json',json.dumps(sums,indent=2)+'\n')
    temp.replace(output/'reproducibility.zip');print('Bundled',len(sums),'files,', (output/'reproducibility.zip').stat().st_size,'bytes')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,default=report.OUT);a=p.parse_args();bundle(a.data.resolve(),a.output.resolve())
