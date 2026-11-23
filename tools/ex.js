const fs=require('fs'),path=require('path');
const vsctm=require('vscode-textmate'),onig=require('vscode-oniguruma');
const wasm=fs.readFileSync(path.join(__dirname,'node_modules/vscode-oniguruma/release/onig.wasm')).buffer;
const lib=onig.loadWASM(wasm).then(()=>({createOnigScanner:s=>new onig.OnigScanner(s),createOnigString:s=>new onig.OnigString(s)}));
const gdir=path.join(__dirname,'node_modules/tm-grammars/grammars');
const idx={}; for(const f of fs.readdirSync(gdir)){ if(!f.endsWith('.json'))continue; try{const j=JSON.parse(fs.readFileSync(path.join(gdir,f),'utf8')); idx[j.scopeName]=path.join(gdir,f);}catch(e){} }
const reg=new vsctm.Registry({onigLib:lib,loadGrammar:async s=>idx[s]?vsctm.parseRawGrammar(fs.readFileSync(idx[s],'utf8'),idx[s]):null});
const [,,scope,src,runs,want]=process.argv; // want: "scope|trans"
(async()=>{
 const g=await reg.loadGrammar(scope); const lines=fs.readFileSync(src,'utf8').split('\n'); const sc=[]; let st=vsctm.INITIAL;
 for(const l of lines){const r=g.tokenizeLine(l,st);st=r.ruleStack;const a=new Array(l.length);for(const t of r.tokens)for(let c=t.startIndex;c<t.endIndex&&c<l.length;c++)a[c]=t.scopes;sc.push(a);}
 const [ws,wt]=want.split('|'); const seen={};
 for(const row of fs.readFileSync(runs,'utf8').split('\n')){ if(!row)continue; const f=row.split('\t'); const L=+f[0]-1; if(!lines[L])continue;
  const s=+f[1]; const pre=Buffer.from(lines[L]).slice(0,s-1).toString().length; const sp=(sc[L]||[])[pre]; if(!sp)continue;
  if(sp[sp.length-1]===ws && (f[4]||'None')===wt){ const k=f[5]; seen[k]=(seen[k]||0)+1; } }
 console.log(want, Object.entries(seen).slice(0,14).map(([k,v])=>k+'×'+v).join('  '));
})();
