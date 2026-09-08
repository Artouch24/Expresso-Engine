const fs=require('node:fs'),path=require('node:path'),engine=require('./load-engine.cjs');
async function main(){
  const [input,output]=process.argv.slice(2);
  if(!input||!output)throw Error('Usage: npm run solve -- examples/3max-10bb.json calculations/result.json');
  if(fs.existsSync(output))throw Error('Le fichier de sortie existe déjà. Choisissez un autre nom.');
  const options=JSON.parse(fs.readFileSync(input,'utf8'));
  let last=0;
  const result=await engine.run(options,p=>{if(Date.now()-last>1000){console.log(p.phase+' '+p.done+'/'+p.total);last=Date.now()}},()=>new Promise(resolve=>setImmediate(resolve)));
  fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(result),'utf8');
  console.log('Terminé : '+result.decisionNodes+' situations · '+result.trained+' apprentissages · '+result.evaluated+' évaluations · '+result.elapsedMs+' ms');
  console.log('Modèle simplifié, aucun équilibre GTO certifié. Résultat : '+path.resolve(output));
}
main().catch(e=>{console.error(e.message);process.exitCode=1});
