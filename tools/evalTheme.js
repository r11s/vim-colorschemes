// node evalTheme.js theme.json jobs.json [verbose]
// jobs: [{lang, scope, src, cols}], cols: line\tstart\tend\tgroup\ttrans\tcolor
const fs=require('fs'),path=require('path');
const vsctm=require('vscode-textmate'),onig=require('vscode-oniguruma');
const wasm=fs.readFileSync(path.join(__dirname,'node_modules/vscode-oniguruma/release/onig.wasm')).buffer;
const lib=onig.loadWASM(wasm).then(()=>({createOnigScanner:s=>new onig.OnigScanner(s),createOnigString:s=>new onig.OnigString(s)}));
const gdir=path.join(__dirname,'node_modules/tm-grammars/grammars');
const idx={}; for(const f of fs.readdirSync(gdir)){ if(!f.endsWith('.json'))continue; try{const j=JSON.parse(fs.readFileSync(path.join(gdir,f),'utf8')); idx[j.scopeName]=path.join(gdir,f);}catch(e){} }
const [,,themeF,jobsF,verbose]=process.argv;
const theme=JSON.parse(fs.readFileSync(themeF,'utf8'));
const fgDef=(theme.colors&&theme.colors['editor.foreground'])||'#000000';
const raw={name:'t',settings:[{settings:{foreground:fgDef,background:(theme.colors&&theme.colors['editor.background'])||'#000000'}},...theme.tokenColors.map(t=>({name:t.name,scope:t.scope,settings:t.settings}))]};
const INJ=process.env.INJ; const injIdx=INJ?JSON.parse(fs.readFileSync(path.join(INJ,'index.json'),'utf8')):{};
const injByName={}; for(const [sc,names] of Object.entries(injIdx)) for(const name of names) injByName[name]=path.join(INJ,name.split('.').slice(2).join('.')+'.json');
const reg=new vsctm.Registry({onigLib:lib,theme:raw,getInjections:s=>injIdx[s],
 loadGrammar:async s=>injByName[s]?vsctm.parseRawGrammar(fs.readFileSync(injByName[s],'utf8'),injByName[s]):(idx[s]?vsctm.parseRawGrammar(fs.readFileSync(idx[s],'utf8'),idx[s]):null)});
(async()=>{
 const jobs=JSON.parse(fs.readFileSync(jobsF,'utf8')); const cm=reg.getColorMap(); let TT=0,TO=0;
 for(const j of jobs){
  const g=await reg.loadGrammar(j.scope); const lines=fs.readFileSync(j.src,'utf8').split('\n'); if(lines[lines.length-1]==='')lines.pop();
  const col=[]; let st=vsctm.INITIAL;
  for(const l of lines){ const r=g.tokenizeLine2(l,st); const m=r.tokens; const arr=new Array(l.length);
    for(let q=0;q<m.length/2;q++){ const s=m[2*q], e=q+1<m.length/2?m[2*q+2]:l.length; const c=cm[(m[2*q+1]>>>15)&511].toLowerCase(); for(let i=s;i<e&&i<l.length;i++)arr[i]=c; }
    st=g.tokenizeLine(l,st).ruleStack; col.push(arr); }
  let tot=0,ok=0; const bad=new Map();
  for(const row of fs.readFileSync(j.cols,'utf8').split('\n')){ if(!row)continue; const f=row.split('\t'); const L=+f[0]-1; if(f[3]==='#END'||!lines[L])continue;
   const s=+f[1],e=+f[2]; const b=Buffer.from(lines[L]); const pre=b.slice(0,s-1).toString().length; const body=b.slice(s-1,e).toString(); const exp=(f[5]||'').toLowerCase();
   for(let i=0;i<body.length;i++){ if(/\s/.test(body[i]))continue; tot++; const got=(col[L]||[])[pre+i];
     if(got===exp)ok++; else { const k=(f[3]||'-')+'|'+f[4]+' '+body.slice(0,14).replace(/\n/g,' ')+' | '+got+' statt '+exp; bad.set(k,(bad.get(k)||0)+1); } } }
  TT+=tot; TO+=ok;
  console.log(j.lang.padEnd(11), String(tot).padStart(5), (100*ok/tot).toFixed(1).padStart(6)+' %', ' falsch:', tot-ok);
  if(verbose){ [...bad.entries()].sort((a,b)=>b[1]-a[1]).slice(0,+verbose).forEach(([k,v])=>console.log('   ',v,k)); }
 }
 console.log('gesamt'.padEnd(11), String(TT).padStart(5), (100*TO/TT).toFixed(1).padStart(6)+' %');
})();
