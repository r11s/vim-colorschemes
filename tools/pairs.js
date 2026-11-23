// Aufruf: node pairs.js jobs.json out.tsv
// jobs: [{lang, scope, src, runs}]  runs: line\tstart\tend\tgroup\ttrans\ttext (1-basiert, Bytespalten)
const fs=require('fs'),path=require('path');
const vsctm=require('vscode-textmate'),onig=require('vscode-oniguruma');
const wasm=fs.readFileSync(path.join(__dirname,'node_modules/vscode-oniguruma/release/onig.wasm')).buffer;
const lib=onig.loadWASM(wasm).then(()=>({createOnigScanner:s=>new onig.OnigScanner(s),createOnigString:s=>new onig.OnigString(s)}));
const gdir=path.join(__dirname,'node_modules/tm-grammars/grammars');
const idx={}; for(const f of fs.readdirSync(gdir)){ if(!f.endsWith('.json'))continue; try{const j=JSON.parse(fs.readFileSync(path.join(gdir,f),'utf8')); idx[j.scopeName]=path.join(gdir,f);}catch(e){} }
const INJ=process.env.INJ; const injIdx=INJ?JSON.parse(fs.readFileSync(path.join(INJ,'index.json'),'utf8')):{};
const injByName={}; for(const [sc,names] of Object.entries(injIdx)) for(const name of names) injByName[name]=path.join(INJ,name.split('.').slice(2).join('.')+'.json');
const reg=new vsctm.Registry({onigLib:lib,getInjections:s=>injIdx[s],
 loadGrammar:async s=>injByName[s]?vsctm.parseRawGrammar(fs.readFileSync(injByName[s],'utf8'),injByName[s]):(idx[s]?vsctm.parseRawGrammar(fs.readFileSync(idx[s],'utf8'),idx[s]):null)});
const [,,jobsF,outF]=process.argv; const jobs=JSON.parse(fs.readFileSync(jobsF,'utf8'));
(async()=>{
 const out=[];
 for(const j of jobs){
  const g=await reg.loadGrammar(j.scope); if(!g){console.error('keine Grammatik',j.scope);continue;}
  const text=fs.readFileSync(j.src,'utf8'); const lines=text.split('\n'); if(lines[lines.length-1]==='')lines.pop();
  // Zeichen -> Scopes
  const sc=[]; let st=vsctm.INITIAL;
  for(const l of lines){ if(j.isolate) st=vsctm.INITIAL; const r=g.tokenizeLine(l,st); st=r.ruleStack; const arr=new Array(l.length);
    for(const t of r.tokens) for(let c=t.startIndex;c<t.endIndex&&c<l.length;c++) arr[c]=t.scopes; sc.push(arr); }
  const agg=new Map();
  for(const row of fs.readFileSync(j.runs,'utf8').split('\n')){ if(!row)continue; const f=row.split('\t'); const L=+f[0]-1; const s=+f[1], e=+f[2]; const grp=f[3], tr=f[4];
    if(grp==='#END'||!lines[L])continue;
    const lineBuf=Buffer.from(lines[L]); // Vim-Spalten sind Bytes
    const pre=lineBuf.slice(0,s-1).toString().length; const body=lineBuf.slice(s-1,e).toString();
    for(let i=0;i<body.length;i++){ const ch=body[i]; if(/\s/.test(ch))continue; const sp=(sc[L]&&sc[L][pre+i])||['?'];
      const key=[j.lang,grp,tr,sp.join(' ')].join('\t'); agg.set(key,(agg.get(key)||0)+1); }
  }
  for(const [k,v] of agg) out.push(k+'\t'+v);
  console.log(j.lang, j.src, 'ok');
 }
 fs.writeFileSync(outF,'lang\tvim_group\tvim_trans\ttm_scopes\tchars\n'+out.join('\n')+'\n');
})();
