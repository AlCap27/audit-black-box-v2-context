"""Package only this nonsensitive offline directory; verify every archive member."""
import hashlib, json, zipfile
from prepare import ROOT, dump, sha

def main():
    files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='package-sha256.json']
    manifest={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    dump(ROOT/'package-sha256.json',manifest)
    archive=ROOT.parents[1]/'audit-black-box-v2-batch-offline-20260914.zip'
    if archive.exists():raise ValueError('Archive already exists: do not overwrite')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files+[ROOT/'package-sha256.json']:
            z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for rel,h in manifest.items():assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==h
    receipt={'archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'verified_members':len(files)+1}
    dump(archive.with_suffix('.sha256.json'),receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
