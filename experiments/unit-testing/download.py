#!/usr/bin/env python3
"""Fetch the public SWE-bench Verified dataset; contains gold, keep private during runs."""
import argparse,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
a.data.mkdir(parents=True,exist_ok=True);path=a.data/'swebench-verified.json'
if path.exists():raise SystemExit('Dataset already exists; refusing to overwrite.')
rows=[]
for offset in range(0,500,100):
    url=f'https://datasets-server.huggingface.co/rows?dataset=princeton-nlp/SWE-bench_Verified&config=default&split=test&offset={offset}&length=100'
    with urllib.request.urlopen(url,timeout=60) as r:page=json.load(r)
    if page['num_rows_total']!=500:raise SystemExit('Dataset size changed; review selection protocol.')
    rows.extend(r['row'] for r in page['rows'])
if len(rows)!=500:raise SystemExit('Incomplete dataset download.')
path.write_text(json.dumps(rows,indent=2)+'\n');print('Downloaded 500 benchmark records.')
