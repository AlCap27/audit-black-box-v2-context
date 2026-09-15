"""Offline only. Deterministic factorial materials; no network or credentials."""
import argparse, hashlib, itertools, json, math, random, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'source'))
from common import digest
from corpus import FACTS, PHRASES, vendor_files, BUNDLES
from rag import Extractor, BM25, make_context
from experiment import SYSTEM

MODEL = 'gemini-3.1-flash-lite'
SEED = 202609140367
CELLS = [''.join(map(str, x)) for x in itertools.product((0,1), repeat=3)]
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8', newline='\n')
def line(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':'))+'\n'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def fixtures(v, cell):
    s,l,t = map(int,cell)
    # Existing renderer, independently select schema and llms; sitemap constant.
    label = 'D' if s else 'B'
    f = vendor_files(v,label,f"https://{v['vendor_id']}.audit.invalid")
    prose = PHRASES[v['template']].format(name=v['name'])
    if l: f['llms.txt'] = f"# {v['name']}\n\n{prose}\n"
    else: f.pop('llms.txt',None)
    if t:
        from html import escape
        p = '<p>'+escape(prose)+'</p>'
        f['index.html'] = f['index.html'].replace(p,p+p)
    return f

def extract(content, filename):
    if filename == 'index.html':
        p=Extractor(); p.feed(content)
        structured=' '.join(json.dumps(json.loads(x),ensure_ascii=False,sort_keys=True) for x in p.schema)
        return ('html+schema' if structured else 'html', ' '.join(p.plain)+('\n'+structured if structured else ''))
    if filename=='llms.txt': return 'llms',content
    if filename.endswith('.txt') and filename.startswith('e'): return 'editorial',content
    return None

def chunks_for(a, identities, assets, editorials):
    items=[]
    for v in identities:
        vid=v['vendor_id']; cell=a['conditions'][vid]
        for filename,content in assets[vid,cell].items():
            items.append((vid,filename,content,f"sites/{a['assignment_id']}/{vid}/{filename}",f"https://{vid}.audit.invalid"+('/' if filename=='index.html' else '/'+filename)))
    for i,content in enumerate(editorials):
        items.append((None,f'e{i:03}.txt',content,f"editorial/{a['assignment_id']}/e{i:03}.txt",f'https://e{i:03}.editorial.invalid/'))
    chunks=[]
    for vid,fn,content,path,url in items:
        ext=extract(content,fn)
        if ext is None: continue
        source,text=ext; words=text.split()
        for start in range(0,len(words),100):
            c={'chunk_id':f'{path}:{source}:{start}','vendor_id':vid,'url':url,'source':source,'text':' '.join(words[start:start+100]),'word_start':start,'word_end':min(start+100,len(words))}
            c['sha256']=digest(c); chunks.append(c)
    return chunks

def discovery_benchmarks():
    # Explicit finite BFS graphs; target /product not secretly seeded.
    graphs={'direct':{'/':['/product']},'chain':{'/':['/category'],'/category':['/product']},'orphan':{'/':[]},'cycle':{'/':['/category'],'/category':['/','/product']}}
    results=[]
    for topology,g in graphs.items():
        for sitemap in (False,True):
            for reverse in (False,True):
                queue=['/']; queue+=['/product'] if sitemap else []; seen=[]
                while queue:
                    u=queue.pop(0)
                    if u in seen: continue
                    seen.append(u); queue+=sorted(g.get(u,[]),reverse=reverse)
                results.append({'topology':topology,'sitemap':sitemap,'reverse':reverse,'edges':g,'seeds':['/'],'visited':seen,'discovered':'/product' in seen})
    return results

def build(out,n=367):
    if out.exists(): raise ValueError('New output directory required; no overwrite')
    out.mkdir(parents=True)
    old=json.loads((ROOT/'source/identity-source.json').read_text(encoding='utf-8-sig'))
    identities,queries=old['identities'],old['queries']
    assert len(identities)==32 and len(queries)==24
    assets={}; asset_manifest=[]
    for v in identities:
        for cell in CELLS:
            f=fixtures(v,cell); assets[v['vendor_id'],cell]=f
            for fn,content in f.items():
                path=out/'corpus'/v['vendor_id']/cell/fn
                path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding='utf-8',newline='\n')
                asset_manifest.append({'path':path.relative_to(out).as_posix(),'sha256':sha(path),'vendor_id':v['vendor_id'],'cell':cell})
    from corpus import QUERY_BASES
    editorials=[f"Guida editoriale {i+1}. "+QUERY_BASES[i%12]+'. Una bottiglia di vino rosso italiano si può valutare per stile, prezzo e abbinamenti. Questa guida non identifica venditori o negozi.' for i in range(32)]
    dump(out/'editorials.json',editorials); dump(out/'assets.json',asset_manifest)
    dump(out/'discovery-benchmarks.json',discovery_benchmarks())
    assignments=[]
    for i in range(n):
        aid=f'c{i:04}'; conditions={}
        # Distinct RNG per independent cluster, seed never searched against outcomes.
        rng=random.Random(digest([SEED,aid,'allocation']))
        for template in range(4):
            labels=CELLS.copy(); rng.shuffle(labels)
            conditions.update(zip([v['vendor_id'] for v in identities if v['template']==template],labels))
        assignments.append({'assignment_id':aid,'conditions':conditions})
    dump(out/'design.json',{'model':MODEL,'seed':SEED,'cells_SLT':CELLS,'identities':identities,'queries':queries,'assignments':assignments,'replicates':1,'scope':'local controlled discovery, fixed identities and queries','state':'PREPARED_NOT_FROZEN'})
    requests=[]; links=[]; retrieval_counts=Counter()
    with (out/'indexes.jsonl').open('w',encoding='utf-8',newline='\n') as ix, (out/'traces.jsonl').open('w',encoding='utf-8',newline='\n') as tr:
        def add(key,role,prompt,shown,trace):
            req={'key':key,'request':{'systemInstruction':{'parts':[{'text':SYSTEM}]},'contents':[{'role':'user','parts':[{'text':prompt}]}],'generationConfig':{'temperature':0.7,'maxOutputTokens':1200,'responseMimeType':'application/json','thinkingConfig':{'thinkingLevel':'minimal'}}}}
            trace.update(key=key,role=role,prompt=prompt,shown=shown,request_sha256=digest(req),context_sha256=digest(shown))
            tr.write(line(trace)); requests.append(req)
            links.append({'key':key,'role':role,'assignment_id':trace.get('assignment_id'),'query_id':trace.get('query',{}).get('query_id'),'request_sha256':digest(req),'trace_sha256':digest(trace),'prompt_utf8_bytes':len((SYSTEM+prompt).encode()),'input_tokens_local_proxy':math.ceil(len((SYSTEM+prompt).encode())/3),'input_token_reservation_provisional':len((SYSTEM+prompt).encode())+256})
        for a in assignments:
            chunks=chunks_for(a,identities,assets,editorials); bm=BM25(chunks)
            ix.write(line({'assignment_id':a['assignment_id'],'chunks':chunks,'df':dict(bm.df),'lengths':bm.lengths,'average':bm.average,'k1':bm.k1,'b':bm.b,'discovery':{'policy':'enumerate local manifest homepages and optional llms','W':{v['vendor_id']:True for v in identities}}}))
            for q in queries:
                ranked=bm.search(q['text'],5,SEED,1); context,shown=make_context(ranked,700)
                for c in ranked:
                    if c['vendor_id']: retrieval_counts[a['conditions'][c['vendor_id']]]+=1
                add(f"abbv2-{a['assignment_id']}-{q['query_id']}-r0-a0",'confirmatory','FONTI:\n'+context+'\n\nRICHIESTA:\n'+q['text'],shown,{'assignment_id':a['assignment_id'],'query':q,'retrieved':ranked})
        for i in range(24):
            positive=i<12; v=identities[i%12]
            text=PHRASES[v['template']].format(name=v['name']) if positive else editorials[i%32]
            c={'vendor_id':v['vendor_id'] if positive else None,'url':f"https://{v['vendor_id']}.audit.invalid/" if positive else 'https://control.editorial.invalid/','text':text}
            context,shown=make_context([c],700); q=queries[i%12]
            add(f'abbv2-control-{i:02}-a0','control','FONTI:\n'+context+'\n\nRICHIESTA:\n'+q['text'],shown,{'query':q,'expected_decision':'recommend' if positive else 'abstain','expected_vendor':v['vendor_id'] if positive else None})
    # One 24-control job, then 12 query-balanced shards. Each main job contains
    # two queries from every assignment: no assignment assigned to a unique job.
    shards={'controls':[]}
    for i in range(12): shards[f'main-{i:02}']=[]
    for req in requests:
        if 'control' in req['key']: shards['controls'].append(req)
        else:
            q=int(req['key'].split('-')[2][1:])-1
            shards[f'main-{q%12:02}'].append(req)
    shard_manifest=[]
    for name,rows in shards.items():
        random.Random(digest([SEED,name,'schedule'])).shuffle(rows)
        path=out/'requests'/(name+'.jsonl'); path.parent.mkdir(exist_ok=True)
        path.write_text(''.join(map(line,rows)),encoding='utf-8',newline='\n')
        shard_manifest.append({'name':name,'path':path.relative_to(out).as_posix(),'sha256':sha(path),'requests':len(rows),'keys':[r['key'] for r in rows]})
    dump(out/'request-links.json',links); dump(out/'shards.json',shard_manifest)
    estimate={'currency':'USD','budget_total':30,'model':MODEL,'pricing_checked':'2026-09-14','batch_input_per_million':0.125,'batch_output_per_million':0.75,'requests':len(links),'confirmatory_requests':24*n,'controls':24,'input_tokens_proxy':sum(x['input_tokens_local_proxy'] for x in links),'input_tokens_provisional_reservation':sum(x['input_token_reservation_provisional'] for x in links),'output_tokens_cap':1200*len(links),'tokens_counted_by_google':False,'project_quota_verified':False,'billing_enabled_by_this_package':False,'spent_by_this_preparation':0}
    estimate['estimate_at_150_output_tokens']=round((estimate['input_tokens_proxy']*.125+150*len(links)*.75)/1e6,6)
    estimate['provisional_max_cost']=round((estimate['input_tokens_provisional_reservation']*.125+estimate['output_tokens_cap']*.75)/1e6,6)
    dump(out/'estimate.json',estimate); dump(out/'retrieval-descriptive.json',dict(retrieval_counts))
    dump(out/'manifest.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    return estimate

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--assignments',type=int,default=367)
    a=p.parse_args();print(json.dumps(build(a.output,a.assignments),indent=2))
