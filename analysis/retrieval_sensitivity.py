"""Offline global retrieval ablations. Never reuse LLM outcomes for new contexts."""
import json
from pathlib import Path
import sys
import socket
from collections import defaultdict
from analyze import ROOT, wire, o, dump, counts, point
import prepare as p


def run(out):
    if out.exists(): raise ValueError('Do not overwrite analysis')
    def denied(*a,**k): raise AssertionError('NETWORK FORBIDDEN')
    socket.socket.connect=denied;socket.create_connection=denied
    data=wire.BASE/'data'; design=o.read(data/'design.json'); editorials=o.read(data/'editorials.json')
    assets={(v['vendor_id'],cell):{f.name:f.read_text(encoding='utf-8')
            for f in (data/'corpus'/v['vendor_id']/cell).iterdir()}
            for v in design['identities'] for cell in design['cells_SLT']}
    original=p.extract
    def no_schema(content,filename):
        if filename!='index.html':return original(content,filename)
        parser=p.Extractor();parser.feed(content)
        return 'html',' '.join(parser.plain)
    conditions={a['assignment_id']:a['conditions'] for a in design['assignments']}
    vids=[v['vendor_id'] for v in design['identities']]
    baseline={r['key']:set(r['Z']) for r in map(json.loads,(out.parent/'observations.jsonl').read_text(encoding='utf-8').splitlines())}
    results={}
    for mode in ('no-schema','no-llms','canonical-text'):
        p.extract=no_schema if mode in ('no-schema','canonical-text') else original
        modified={}
        for (vid,cell),files in assets.items():
            src=assets[vid,cell[:2]+'0'] if mode=='canonical-text' else files
            modified[vid,cell]={k:v for k,v in src.items() if not (k=='llms.txt' and mode in ('no-llms','canonical-text'))}
        rows=[];changed=0
        for a in design['assignments']:
            bm=p.BM25(p.chunks_for(a,design['identities'],modified,editorials))
            for q in design['queries']:
                ranked=bm.search(q['text'],5,p.SEED,1)
                z=sorted({r['vendor_id'] for r in ranked if r['vendor_id']})
                key=f"abbv2-{a['assignment_id']}-{q['query_id']}-r0-a0"
                changed+=set(z)!=baseline[key]
                rows.append({'assignment_id':a['assignment_id'],'Z':z,'Y':[],'X':[]})
        c=counts(rows,conditions,vids)
        results[mode]={'requests':len(rows),'changed_vendor_sets':changed,
            'vendor_retrievals':sum(len(r['Z']) for r in rows),
            'retrieval_effects':{f:point(v)['R'] for f,v in c.items()},
            'recommendation_outcomes_reused':False}
        print(json.dumps({'completed':mode,**results[mode]}),flush=True)
    p.extract=original
    dump(out,{'label':'Global pipeline sensitivity, descriptive only',
        'canonical_text_definition':'One canonical body copy; schema and llms excluded; fixed identity/template markup retained',
        'implementation_timing':'Adapter and exact canonical-text implementation authored after collection; not a new confirmatory test',
        'results':results})

if __name__=='__main__':run(Path(sys.argv[1]).resolve())
