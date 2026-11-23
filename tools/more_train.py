import json, glob, os, sys
R='/tmp/vd/lang/repos/'
SPEC=json.load(open('spec.json')); P=json.load(open('picked.json'))
def repo(f): return f[len(R):].split('/')[0] if f.startswith(R) else f.split('/')[1]
for lang,(ext,vim,scope,globs) in SPEC.items():
    if lang=='make' or lang not in P: continue
    train,test=P[lang]
    c=[]
    for g in globs:
        for f in glob.glob(g,recursive=True):
            if not os.path.isfile(f) or f in (train,test): continue
            try: t=open(f,encoding='utf-8').read()
            except Exception: continue
            L=t.split('\n')
            if len(L)<30 or max(len(l) for l in L[:900])>600: continue
            if any(x in f for x in ('/node_modules/','.min.','/vendor/','_generated')): continue
            if os.path.basename(f)==os.path.basename(test): continue
            c.append((min(len(L),700),f))
    LOC={'cpp':['/usr/include/**/*.hpp'],'ts':[],'ruby':['/usr/lib/ruby/**/*.rb'],'sh':['/usr/share/**/*.sh','/usr/lib/**/*.sh','/etc/**/*.sh'],'markdown':['/usr/share/doc/**/*.md','/opt/npm-tools/node_modules/*/README.md'],'sql':['/usr/share/**/*.sql'],'lua':['/usr/share/**/*.lua'],'vim':['/usr/share/vim/**/*.vim'],'perl':['/usr/share/perl/**/*.pm'],'dosini':['/usr/share/**/*.ini','/etc/**/*.conf'],'scss':['/usr/lib/**/*.scss'],'xml':['/usr/share/**/*.xml'],'typescript':['/opt/npm-tools/node_modules/**/*.ts'],'diff':['/usr/share/**/*.diff','/usr/share/**/*.patch']}
    for g in LOC.get(lang,[]):
        for f in glob.glob(g,recursive=True)[:3000]:
            if not os.path.isfile(f) or f in (train,test) or '.d.ts' in f: continue
            try: t=open(f,encoding='utf-8').read()
            except Exception: continue
            L=t.split('\n')
            if len(L)<60 or max(len(l) for l in L[:900])>300 or '\0' in t: continue
            if lang=='vim' and sum(1 for l in L[:700] if l.lstrip().startswith('\\'))>20: continue
            c.append((min(len(L),700),f))
    c.sort(key=lambda x:(-x[0],x[1]))
    add=[];seen={os.path.basename(train)}
    for n,f in c:
        if lang in('dockerfile','vim') or os.path.basename(f) not in seen:
            add.append(f);seen.add(os.path.basename(f))
        if len(add)==2:break
    base=f'files/{lang}.train.{ext}'
    if not os.path.exists(base+'.orig'): open(base+'.orig','w').write(open(base).read())
    txt=open(base+'.orig').read()
    for f in add:
        txt+=''.join(open(f,encoding='utf-8').read().split('\n')[0:700] and '\n'.join(open(f,encoding='utf-8').read().split('\n')[:700]).rstrip('\n')+'\n')
    open(base,'w').write(txt)
    print(lang,len(add),[os.path.relpath(f,R) for f in add])
