const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const inject=(text,token,value)=>{
  const marker='/* @'+token+'@ */';
  if(text.split(marker).length!==2)throw Error('Expected exactly one marker '+marker);
  return text.replace(marker,()=>value.trim());
};
let app=read('src/app.js');
app=inject(app,'REFERENCE_CHARTS',JSON.stringify(JSON.parse(read('data/reference-charts.json'))));
app=inject(app,'SOLVER_EXAMPLE',JSON.stringify(read('data/example.deflate.b64').trim()));
app=inject(app,'SOLVER_UI',read('src/solver-ui.js'));
let html=read('src/index.template.html');
html=inject(html,'RULES',read('src/rules.js'));
html=inject(html,'SOLVER',read('src/solver.js'));
html=inject(html,'APP',app);
if(/\/\* @[A-Z_]+@ \*\//.test(html))throw Error('Unresolved build marker');
fs.mkdirSync(path.join(root,'dist'),{recursive:true});
fs.writeFileSync(path.join(root,'dist/index.html'),html);
console.log('Built dist/index.html · '+Buffer.byteLength(html)+' bytes · no external runtime dependencies');
