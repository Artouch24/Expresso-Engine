const fs=require('node:fs'),zlib=require('node:zlib'),assert=require('node:assert/strict'),engine=require('./load-engine.cjs');
async function main(){
  const saved=JSON.parse(zlib.inflateSync(Buffer.from(fs.readFileSync('data/example.deflate.b64','utf8').trim(),'base64')));
  const options=JSON.parse(fs.readFileSync('examples/3max-10bb.json','utf8'));
  const calculated=await engine.run(options,()=>{},async()=>{});
  assert.deepEqual(JSON.parse(JSON.stringify(calculated.nodes)),saved.nodes);
  assert.deepEqual(JSON.parse(JSON.stringify(calculated.rootChanges)),saved.rootChanges);
  console.log('Exemple intégré reproduit exactement : '+saved.decisionNodes+' situations. Durée volontairement exclue de la comparaison.');
}
main().catch(e=>{console.error(e);process.exitCode=1});
