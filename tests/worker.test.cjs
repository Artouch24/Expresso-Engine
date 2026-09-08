const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {Worker}=require('node:worker_threads');
const html=fs.readFileSync('dist/index.html','utf8');
const scripts=Object.fromEntries([...html.matchAll(/<script id="([^"]+)">([\s\S]*?)<\/script>/g)].map(m=>[m[1],m[2]]));
// Execute precisely the worker text assembled by the shipping UI, in a real Node
// worker with only the browser message API adapted. This is not a browser smoke test.
const expression=scripts['poker-ui'].match(/const workerCode=(.*);\n/)[1];
const source=vm.runInNewContext(expression,{$:id=>({textContent:scripts[id]})});
const adapter='const {parentPort}=require("node:worker_threads");const self={postMessage:m=>parentPort.postMessage(m)};\n'+source+'\nparentPort.on("message",data=>self.onmessage({data}));';
const config={players:3,hero:'BTN',stacks:{BTN:10,SB:10,BB:10},sb:.5,ante:0,anteMode:'each',objective:'chipEV',payouts:[1,0,0],rake:0};
async function run(options){
  const worker=new Worker(adapter,{eval:true});
  try{return await new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>reject(Error('Worker timeout')),20000),progress=[];
    worker.on('error',e=>{clearTimeout(timeout);reject(e)});
    worker.on('message',m=>{if(m.kind==='progress')progress.push(m.progress);else {clearTimeout(timeout);resolve({message:m,progress})}});
    worker.postMessage(options);
  })}finally{await worker.terminate()}
}
(async()=>{
  const options={config,model:'extended',openSize:2,iterations:500,evaluationDeals:300,seed:200};
  const {message,progress}=await run(options);
  assert.equal(message.kind,'result');assert.equal(message.result.trained,500);assert.equal(message.result.decisionNodes,198);
  assert.ok(progress.some(p=>p.phase==='train'));assert.ok(progress.some(p=>p.phase==='evaluate'));
  console.log('OK serialized UI worker completes training and independent evaluation');
  const invalid=await run({...options,config:{...config,ante:.1}});
  assert.equal(invalid.message.kind,'error');assert.match(invalid.message.message,/sans ante/);
  console.log('OK serialized UI worker reports unsupported parameters without publishing a result');
})().catch(e=>{console.error(e);process.exitCode=1});
