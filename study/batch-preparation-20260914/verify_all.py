"""Verify old seals read-only and all 8,832 prepared requests/retrieval traces."""
import json, sys, platform
from pathlib import Path
from collections import Counter
from prepare import ROOT, sha, dump, digest, BM25, make_context, SEED, chunks_for
from batch_state import verify

def main():
    report={'python':platform.python_version(),'sealed':{},'network_calls':0}
    for name in ('pilot-expanded-20260910','extension-20260913','confirmatory-design-20260914'):
        p=ROOT.parent/name
        m=json.loads((p/'sha256.json').read_text(encoding='utf-8-sig'))
        for rel,h in m.items():
            f=(p/rel).resolve()
            assert f.is_relative_to(p.resolve()) and sha(f)==h,(name,rel)
        report['sealed'][name]=len(m)
    d=ROOT/'data';report['manifest_files']=verify(d)
    design=json.loads((d/'design.json').read_text(encoding='utf-8'))
    assets={}
    for v in design['identities']:
        for cell in design['cells_SLT']:
            assets[v['vendor_id'],cell]={p.name:p.read_text(encoding='utf-8') for p in (d/'corpus'/v['vendor_id']/cell).iterdir()}
    editorials=json.loads((d/'editorials.json').read_text(encoding='utf-8'))
    indexes={i['assignment_id']:i for i in map(json.loads,(d/'indexes.jsonl').read_text(encoding='utf-8').splitlines())}
    for a in design['assignments']:
        assert chunks_for(a,design['identities'],assets,editorials)==indexes[a['assignment_id']]['chunks']
        for t in range(4):
            assert Counter(a['conditions'][v['vendor_id']] for v in design['identities'] if v['template']==t)==Counter(design['cells_SLT'])
    bm={a:BM25(x['chunks']) for a,x in indexes.items()}
    for a,b in bm.items():
        assert dict(b.df)==indexes[a]['df'] and b.lengths==indexes[a]['lengths'] and b.average==indexes[a]['average']
    traces={t['key']:t for t in map(json.loads,(d/'traces.jsonl').read_text(encoding='utf-8').splitlines())}
    links={x['key']:x for x in json.loads((d/'request-links.json').read_text(encoding='utf-8'))}
    keys=[]
    for p in (d/'requests').glob('*.jsonl'):
        rows=list(map(json.loads,p.read_text(encoding='utf-8').splitlines()))
        for r in rows:
            k=r['key'];keys.append(k);t=traces[k]
            assert digest(r)==t['request_sha256']==links[k]['request_sha256']
            assert digest(t)==links[k]['trace_sha256']
            assert r['request']['contents'][0]['parts'][0]['text']==t['prompt']
            if t['role']=='confirmatory':
                ranked=bm[t['assignment_id']].search(t['query']['text'],5,SEED,1)
                assert ranked==t['retrieved']
                context,shown=make_context(ranked,700)
                assert shown==t['shown']
                assert t['prompt']=='FONTI:\n'+context+'\n\nRICHIESTA:\n'+t['query']['text']
    assert len(keys)==len(set(keys))==8832
    assert len(indexes)==367
    report.update(assignments=367,requests=8832,retrievals_recomputed=8808,controls=24,status='PASS')
    dump(ROOT/'verification.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
