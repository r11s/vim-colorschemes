// node tokcol.js theme.json scope file  (INJ optional) -> Farbe je Token
const fs=require('fs'),path=require('path');
const vsctm=require('vscode-textmate'),onig=require('vscode-oniguruma');
const wasm=fs.readFileSync(path.join(__dirname,'node_modules/vscode-oniguruma/release/onig.wasm')).buffer;
const lib=onig.loadWASM(wasm).then(()=>({createOnigScanner:s=>new onig.OnigScanner(s),createOnigString:s=>new onig.OnigString(s)}));
const gdir=path.join(__dirname,'node_modules/tm-grammars/grammars');const idx={};
for(const f of fs.readdirSync(gdir)){if(!f.endsWith('.json'))continue;try{const j=JSON.parse(fs.readFileSync(path.join(gdir,f),'utf8'));idx[j.scopeName]=path.join(gdir,f);}catch(e){}}
const [,,themeF,scope,src]=process.argv; const theme=JSON.parse(fs.readFileSync(themeF,'utf8'));
const INJ=process.env.INJ; const injIdx=INJ?JSON.parse(fs.readFileSync(path.join(INJ,'index.json'),'utf8')):{}; const injBy={};
for(const names of Object.values(injIdx)) for(const n of names) injBy[n]=path.join(INJ,n.split('.').slice(2).join('.')+'.json');
const raw={name:'t',settings:[{settings:{foreground:theme.colors['editor.foreground'],background:'#000000'}},...theme.tokenColors]};
const reg=new vsctm.Registry({onigLib:lib,theme:raw,getInjections:s=>injIdx[s],loadGrammar:async s=>injBy[s]?vsctm.parseRawGrammar(fs.readFileSync(injBy[s],'utf8'),injBy[s]):(idx[s]?vsctm.parseRawGrammar(fs.readFileSync(idx[s],'utf8'),idx[s]):null)});
(async()=>{const g=await reg.loadGrammar(scope);const cm=reg.getColorMap();let st=vsctm.INITIAL;
 for(const l of fs.readFileSync(src,'utf8').split('\n')){if(!l)continue;const r2=g.tokenizeLine2(l,st);const r=g.tokenizeLine(l,st);st=r.ruleStack;const m=r2.tokens;
  const out=[];for(let q=0;q<m.length/2;q++){const s=m[2*q],e=q+1<m.length/2?m[2*q+2]:l.length;if(l.slice(s,e).trim())out.push(JSON.stringify(l.slice(s,e))+' '+cm[(m[2*q+1]>>>15)&511]);}
  console.log(out.join('  '));}})();
