#!/usr/bin/env python3
"""Surface trajectory actions for review; never infer verbal rejection from success."""
import argparse, json
from pathlib import Path
from common import save


def inspect(path):
    r=json.loads(path.read_text());events=[json.loads(l) for l in (path.parent/'trajectory.jsonl').read_text().splitlines() if l.startswith('{')]
    changes=[];external=[];types=set()
    for ev in events:
        if ev.get('type')!='item.completed':continue
        item=ev.get('item',{});kind=item.get('type','');types.add(kind)
        if kind=='file_change':changes.extend(item.get('changes',[]))
        if kind in ('web_search','mcp_tool_call') or 'collab' in kind:external.append(kind)
    r['trajectory_audit']=dict(file_changes=changes,external_tools=external,item_types=sorted(types))
    save(path,r)
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',required=True,type=Path);p.add_argument('--limit',type=int,default=4);p.add_argument('--summary',action='store_true');a=p.parse_args();n=0
    for path in sorted((a.data/'runs').glob('*/result.json'),key=lambda path:json.loads(path.read_text())['started_at']):
        r=inspect(path)
        if a.summary:
            print(r['run_id'],'reviewed',bool(r.get('compliance_review')),'external',r['trajectory_audit']['external_tools']);continue
        if 'compliance_review' in r:continue
        print('\nRUN',r['run_id']);print('ARTIFACTS',json.dumps({k:r.get(k) for k in ('changed','untracked','excluded_changes','trajectory_audit')}))
        for c in r['commands']:print('COMMAND',c)
        if 'wrong' in r['condition']:print('MESSAGES',json.dumps(r['messages'],ensure_ascii=False))
        n+=1
        if n>=a.limit:break
