"""Offline sensitivity checks; never calls a generator or edits sealed campaigns."""
import sys, hashlib, statistics
from pathlib import Path
from collections import Counter, defaultdict
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
from common import read_json, save_json, digest
from experiment import prepare, default_config
from rag import tokens

def main():
    result={}
    for campaign in ('pilot-expanded-20260910','extension-20260913'):
        c=P/campaign
        seal=read_json(c/'sha256.json')
        for name,h in seal.items():
            assert hashlib.sha256((c/name).read_bytes()).hexdigest()==h
        variants={}
        for label,schema,llms in [('full',True,True),('no_schema',False,True),('no_llms',True,False),('plain_only',False,False)]:
            cfg=default_config('gemini');cfg.update(schema_in_index=schema,llms_in_index=llms)
            spec,traces,indexes=prepare(c/'corpus',cfg)
            hits=Counter();sources=Counter();lengths=defaultdict(list);no_vendor=0
            for a in spec['assignments']:
                for ch in indexes[a['assignment_id']]:
                    if ch['vendor_id']:lengths[a['bundles'][ch['vendor_id']]].append(len(tokens(ch['text'])))
                for q in spec['queries']:
                    tr=traces[a['assignment_id']+':'+q['query_id']]
                    if label=='full':assert digest(tr)==digest(read_json(c/'run/retrieval'/f"{a['assignment_id']}-{q['query_id']}.json"))
                    selected=[ch for ch in tr['retrieved'] if ch['vendor_id']]
                    no_vendor+=not selected
                    for ch in selected:
                        b=a['bundles'][ch['vendor_id']];hits[b]+=1;sources[b+':'+ch['source']]+=1
            denominator=len(traces)*8
            variants[label]={'queries':len(traces),'retrieval_counts':{b:hits[b] for b in 'ABCD'},
                'per_vendor_probability':{b:hits[b]/denominator for b in 'ABCD'},
                'retrieved_source_counts':dict(sources),'queries_without_vendor':no_vendor,
                'mean_chunk_tokens':{b:statistics.mean(lengths[b]) for b in 'ABCD'}}
        result[campaign]={'seal_files_verified':len(seal),'variants':variants}
    result['interpretation']='Global index sensitivity, including changed document frequencies and length normalization. Not natural mediation and not generator outcomes under changed retrieval.'
    save_json(Path(__file__).with_name('bm25-checks.json'),result)
    print(result)
if __name__=='__main__':main()
