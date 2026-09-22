"""Offline analysis of completed Audit V2, using the frozen interval functions.

No provider calls, missing-outcome imputation, exclusions, or primary selection.
New output directory required. All recommendation rows are reparsed from raw.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'preflight'))
import orchestration as o
import transport as wire
sys.path.insert(0, str(wire.BASE/'source-protocol'))
from bounded_inference import mean_interval, conditional_difference
from experiment import parse_answer, response_text


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n',
                    encoding='utf-8', newline='\n')


def counts(rows, conditions, vendors):
    result = {f: [[0]*5, [0]*5] for f in 'SLT'}
    for row in rows:
        for vid in vendors:
            y, z, x = (int(vid in row[v]) for v in ('Y', 'Z', 'X'))
            cell = conditions[row['assignment_id']][vid]
            for index, factor in enumerate('SLT'):
                acc = result[factor][int(cell[index])]
                for k, value in enumerate((y, z, y*z, x, 1)):
                    acc[k] += value
    return result


def point(c):
    a, b = c  # 0, 1. Columns Y,Z,YZ,X,slots.
    return {'Y':b[0]/b[4]-a[0]/a[4], 'R':b[1]/b[4]-a[1]/a[4],
            'C':None if not a[1] or not b[1] else b[2]/b[1]-a[2]/a[1],
            'rates_0':{'Y':a[0]/a[4], 'Z':a[1]/a[4], 'Y_given_Z':a[2]/a[1] if a[1] else None},
            'rates_1':{'Y':b[0]/b[4], 'Z':b[1]/b[4], 'Y_given_Z':b[2]/b[1] if b[1] else None}}


def inference(cluster_counts):
    results=[]
    for f in 'LST':
        clusters=[c[f] for c in cluster_counts]
        assert all(c[0][4]==c[1][4]==384 for c in clusters)
        totals=[[sum(c[level][k] for c in clusters) for k in range(5)] for level in (0,1)]
        estimates=point(totals)
        for outcome in ('Y','R','C'):
            alpha=.025 if (f,outcome)==('L','Y') else .003125
            if outcome in ('Y','R'):
                k=0 if outcome=='Y' else 1
                support=3/16 if outcome=='Y' else 5/16
                ds=[(c[1][k]-c[0][k])/384 for c in clusters]
                interval=mean_interval([(v,v) for v in ds],-support,support,alpha)
            else:
                arrays=[[(c[level][k]/384,c[level][k]/384) for c in clusters]
                        for level,k in ((1,2),(1,1),(0,2),(0,1))]
                interval=conditional_difference(*arrays,alpha)
            results.append({'factor':f,'outcome':outcome,'alpha':alpha,
                'estimate':estimates[outcome], 'interval':interval,
                'reject_zero':interval[0]>0 or interval[1]<0,
                'exceeds_5pp_supported':interval[0]>.05 or interval[1]<-.05,
                'rates_0':estimates['rates_0'],'rates_1':estimates['rates_1']})
    return results


def run(out):
    if out.exists(): raise ValueError('New analysis output directory required')
    def denied(*args,**kwargs): raise AssertionError('NETWORK FORBIDDEN')
    socket.socket.connect=denied; socket.create_connection=denied
    data=wire.BASE/'data'; state=ROOT/'runtime/audit-v2'
    integrity={}
    for path in list((ROOT/'study').glob('*/sha256.json'))+[
            wire.BASE/'source-protocol/sha256.json',wire.BASE/'package-sha256.json',data/'manifest.json']:
        manifest=o.read(path)
        for rel,h in manifest.items():
            p=(path.parent/rel).resolve()
            assert p.is_relative_to(path.parent.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==h
        integrity[path.relative_to(ROOT).as_posix()]=len(manifest)
    freeze=o.read(wire.ROOT/'freeze-20260921-v2.json')
    for rel,h in freeze['operational_snapshot']['files'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h
    design=o.read(data/'design.json')
    traces={r['key']:r for r in map(json.loads,(data/'traces.jsonl').read_text(encoding='utf-8').splitlines())}
    conditions={a['assignment_id']:a['conditions'] for a in design['assignments']}
    vendors=[v['vendor_id'] for v in design['identities']]
    assert len(conditions)==367 and len(vendors)==32
    journal=o.read(state/'operations.json')
    assert not journal['halted'] and len(journal['attempts'])==13
    rows=[]; seen=set(); provenance={}; qc=Counter(); timing=[]; audit=[]
    for item in journal['attempts'].values():
        assert item['phase']=='RECONCILED' and not item['recovery_pending']
        report=o._archived(state,item['report'],'report')
        assert report['provider_state']=='SUCCEEDED' and report['operational_approval']
        assert o.report_allows(report,o._keys(data,item['shard']),journal['version'],item['shard']=='controls')
        snapshots=[o._archived(state,ref,'get') for ref in item['observations']]
        terminal=[s for s in snapshots if s.get('done') is True and s.get('response')]
        assert terminal
        raw=terminal[-1]
        assert raw['name']==item['job'] and o._job_state(raw)=='SUCCEEDED'
        provenance[item['shard']]={'job':item['job'],'report':item['report'],'get':item['observations'][-1]}
        timing.append({'shard':item['shard'],'metadata':{k:v for k,v in raw['metadata'].items()
                      if k in ('createTime','updateTime','endTime','model','state')}})
        rawrows={}
        for r in wire.normalize_inline(raw):
            assert r['key'] not in rawrows, 'Duplicate terminal key'
            rawrows[r['key']]=r
        assert set(rawrows)==set(report['records'])
        for key,rec in report['records'].items():
            tr=traces[key]; response=rawrows[key]['response']
            parsed=parse_answer(response_text(response,'gemini'),tr['shown'],design['identities'])
            assert parsed==rec['answer'], 'Reparse differs from reconciliation'
            if item['shard']=='controls': continue
            assert key not in seen; seen.add(key)
            z={x['vendor_id'] for x in tr['retrieved'] if x['vendor_id'] is not None}
            x={x['vendor_id'] for x in tr['shown'] if x['vendor_id'] is not None}
            y=set(parsed['recommended'])
            assert len(y)<=3 and len(z)<=5 and y<=set(vendors)
            row={'key':key,'assignment_id':tr['assignment_id'],'query_id':tr['query']['query_id'],
                 'intent':tr['query']['intent'],'job':item['shard'],
                 'Y':sorted(y),'Z':sorted(z),'X':sorted(x),'decision':parsed['decision']}
            rows.append(row)
            qc['abstentions']+=parsed['decision']=='abstain'
            qc['recommendations']+=len(y); qc['Y_outside_Z']+=len(y-z); qc['Y_outside_X']+=len(y-x)
            qc['Z_not_X']+=len(z-x); qc['unknown_names']+=len(parsed['unknown_names'])
            qc['unsupported_recommendations']+=len(parsed['unsupported_recommendations'])
            qc['truncated_context_chunks']+=sum(bool(c.get('truncated')) for c in tr['shown'])
            if parsed['unknown_names'] or parsed['unsupported_recommendations'] or y-z or y-x:
                audit.append({'key':key,'parsed':parsed,'Z':sorted(z),'X':sorted(x)})
    assert len(rows)==8808 and seen=={k for k,t in traces.items() if t['role']=='confirmatory'}
    by_cluster=defaultdict(list)
    for row in rows: by_cluster[row['assignment_id']].append(row)
    assert set(by_cluster)==set(conditions)
    assert all(len(v)==24 and len({r['query_id'] for r in v})==24 for v in by_cluster.values())
    clusters={aid:counts(rs,conditions,vendors) for aid,rs in sorted(by_cluster.items())}
    results=inference(list(clusters.values()))
    descriptive={}
    for group in ('job','query_id','intent'):
        grouped=defaultdict(list)
        for row in rows: grouped[row[group]].append(row)
        descriptive[group]={name:{'requests':len(rs),'effects':{f:point(c) for f,c in counts(rs,conditions,vendors).items()}}
                            for name,rs in sorted(grouped.items())}
    descriptive['template']={str(i):{f:point(c) for f,c in counts(rows,conditions,
        [v['vendor_id'] for v in design['identities'] if v['template']==i]).items()} for i in range(4)}
    cells={cell:Counter() for cell in design['cells_SLT']}
    for r in rows:
        for vid in vendors:
            c=cells[conditions[r['assignment_id']][vid]]
            c['slots']+=1; c['Y']+=vid in r['Y']; c['Z']+=vid in r['Z']; c['YZ']+=vid in r['Y'] and vid in r['Z']
    sensitivity=[]
    for job in sorted(descriptive['job']):
        rs=[r for r in rows if r['job']!=job]
        sensitivity.append({'omitted_job':job,'L_total':point(counts(rs,conditions,vendors)['L'])['Y'],
                            'label':'descriptive leave-one-job-out; no alternative test'})
    out.mkdir(parents=True)
    dump(out/'results.json',{'n_clusters':367,'main_requests':8808,'controls_excluded':24,
        'tests':results,'quality':dict(qc),'cell_counts':{k:dict(v) for k,v in cells.items()},
        'model_version':journal['version'],'inference_requires_independent_clusters':True})
    dump(out/'cluster-counts.json',{'columns':['Y','Z','YZ','X','slots'],'clusters':clusters})
    dump(out/'descriptive.json',descriptive); dump(out/'leave-one-job-out.json',sensitivity)
    dump(out/'parser-ambiguous.json',audit); dump(out/'job-times.json',timing)
    dump(out/'provenance.json',{'integrity':integrity,'raw_reparsed':8832,'shards':provenance,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'freeze_sha256':hashlib.sha256((wire.ROOT/'freeze-20260921-v2.json').read_bytes()).hexdigest(),
        'network_calls':0,'note':'Analysis adapter authored after collection; frozen inference functions unchanged'})
    with (out/'observations.jsonl').open('w',encoding='utf-8',newline='\n') as f:
        for row in sorted(rows,key=lambda r:r['key']): f.write(json.dumps(row,sort_keys=True)+'\n')
    print(json.dumps({'results':results,'quality':dict(qc),'output':str(out)},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    run(parser.parse_args().output.resolve())
