/* A finite preflop game solved by chance-sampled counterfactual regret minimization.
 * All public action branches are traversed on every sampled deal. Both opponents'
 * reaches weight 3-player counterfactual regret. Average policies use own reach.
 * No betting after the preflop round. This is NOT a full Hold'em GTO solver.
 */
function createPreflopSolver(Poker) {
  const EPS=1e-10, ranks='AKQJT98765432';
  function rng(seed){let t=seed>>>0;return ()=>{t+=0x6D2B79F5;let x=Math.imul(t^(t>>>15),t|1);x^=x+Math.imul(x^(x>>>7),x|61);return ((x^(x>>>14))>>>0)/4294967296}}
  function score(category,kickers){let v=category;for(let i=0;i<5;i++)v=v*15+(kickers[i]||0);return v}
  function straight(mask){if(mask&(1<<14))mask|=1<<1;for(let high=14;high>=5;high--){let need=31<<(high-4);if((mask&need)===need)return high}return 0}
  function top(mask,n){let out=[];for(let r=14;r>=2&&out.length<n;r--)if(mask&(1<<r))out.push(r);return out}
  function evaluate7(cards){
    const counts=new Uint8Array(15),suits=new Uint8Array(4),suitMasks=new Uint16Array(4);let mask=0;
    for(const card of cards){const r=(card>>2)+2,s=card&3;counts[r]++;suits[s]++;mask|=1<<r;suitMasks[s]|=1<<r}
    let flushMask=0;for(let s=0;s<4;s++)if(suits[s]>=5){flushMask=suitMasks[s];const sf=straight(flushMask);if(sf)return score(8,[sf])}
    let quad=0,trips=[],pairs=[];for(let r=14;r>=2;r--){if(counts[r]===4)quad=r;else if(counts[r]===3)trips.push(r);else if(counts[r]===2)pairs.push(r)}
    if(quad)return score(7,[quad,...top(mask&~(1<<quad),1)]);
    if(trips.length&&(pairs.length||trips.length>1))return score(6,[trips[0],Math.max(pairs[0]||0,trips[1]||0)]);
    if(flushMask)return score(5,top(flushMask,5));const st=straight(mask);if(st)return score(4,[st]);
    if(trips.length)return score(3,[trips[0],...top(mask&~(1<<trips[0]),2)]);
    if(pairs.length>=2)return score(2,[pairs[0],pairs[1],...top(mask&~((1<<pairs[0])|(1<<pairs[1])),1)]);
    if(pairs.length)return score(1,[pairs[0],...top(mask&~(1<<pairs[0]),3)]);return score(0,top(mask,5));
  }
  function handIndex(a,b){const i=12-(a>>2),j=12-(b>>2);return i===j?i*13+j:(a&3)===(b&3)?Math.min(i,j)*13+Math.max(i,j):Math.max(i,j)*13+Math.min(i,j)}
  function deal(n,random){const deck=Array.from({length:52},(_,i)=>i),k=n*2+5;for(let i=0;i<k;i++){let j=i+Math.floor(random()*(52-i));[deck[i],deck[j]]=[deck[j],deck[i]]}const board=deck.slice(n*2,k),holes=[],indices=[],scores=[];for(let p=0;p<n;p++){let h=[deck[p*2],deck[p*2+1]];holes.push(h);indices.push(handIndex(...h));scores.push(evaluate7([...h,...board]))}return {holes,board,indices,scores}}
  function validateOptions(raw){
    const c=Poker.config(raw.config);if(c.ante!==0||c.objective!=='chipEV'||c.payouts.slice(1).some(x=>x!==0)||c.rake!==0)throw Error('Ce moteur calcule uniquement en chip EV, sans ante ni rake par pot et avec gains winner-take-all.');
    if(Object.values(c.stacks).some(v=>v<1||v>25))throw Error('Les tapis de cette version doivent être compris entre 1 et 25 BB.');
    if(!['extended','pushfold'].includes(raw.model))throw Error('Modèle inconnu.');
    if(![2,2.5,3].includes(raw.openSize))throw Error('Ouverture attendue : 2, 2,5 ou 3 BB.');
    for(const k of ['iterations','evaluationDeals'])if(!Number.isInteger(raw[k])||raw[k]<1||raw[k]>1000000)throw Error('Nombre de simulations invalide.');
    if(!Number.isInteger(raw.seed)||raw.seed<0||raw.seed>0xffffffff)throw Error('Graine aléatoire invalide.');
    return {config:c,model:raw.model,openSize:raw.openSize,iterations:raw.iterations,evaluationDeals:raw.evaluationDeals,seed:raw.seed};
  }
  function legalActions(s,options){const o=Poker.options(s);if(!o)return [];let actions=[];const add=(type,to)=>{try{const ns=Poker.apply(s,{player:o.p,type,...(to===undefined?{}:{to})}),a=ns.history.at(-1);if(!actions.some(x=>Poker.actionKey(x)===Poker.actionKey(a)))actions.push(a)}catch(e){throw Error('Construction des actions : '+e.message)}};
    if(o.owed>0)add('fold');
    if(options.model==='extended'||o.owed===0||s.history.some(a=>a.type==='allin'))add(o.passive,o.owed?o.callTo:undefined);
    if(options.model==='extended'&&o.canFullRaise&&s.history.filter(a=>a.type==='raise').length<2){const sizes=s.raises===0?[Math.max(o.min,options.openSize)]:[o.min,Math.max(o.min,Poker.round(s.bet*3))];for(let to of sizes)if(to<o.max-Poker.EPS)add('raise',to)}
    if(o.canJam)add('allin',o.max);if(!actions.length)throw Error('Aucune action dans le modèle.');return actions;
  }
  function poolsFor(s){const contribution=s.ps.map(p=>s.seats[p].paid),levels=[...new Set(contribution.filter(x=>x>0))].sort((a,b)=>a-b),pools=[];let prev=0;for(const level of levels){const contributors=s.ps.map((p,i)=>i).filter(i=>contribution[i]>=level-Poker.EPS),eligible=contributors.filter(i=>!s.seats[s.ps[i]].folded);if(!eligible.length)throw Error('Pot sans bénéficiaire.');pools.push({amount:Poker.round((level-prev)*contributors.length),eligible});prev=level}return {contribution,pools}}
  function payoff(terminal,scores,out=new Float64Array(scores.length)){for(let p=0;p<scores.length;p++)out[p]=-terminal.contribution[p];for(const pot of terminal.pools){let best=-1,winners=[];for(const p of pot.eligible){if(scores[p]>best){best=scores[p];winners=[p]}else if(scores[p]===best)winners.push(p)}for(const p of winners)out[p]+=pot.amount/winners.length}return out}
  function build(raw){const options=validateOptions(raw),nodes=[],decisions=[],n=options.config.players;
    function visit(s){if(nodes.length>15000)throw Error('Arbre trop grand pour cette version.');const node={id:nodes.length,u:new Float64Array(n),history:s.history};nodes.push(node);const p=Poker.next(s);if(!p){node.terminal=poolsFor(s);return node.id}
      node.actor=s.ps.indexOf(p);node.position=p;node.actions=legalActions(s,options);node.state=s;const size=node.actions.length*169;node.regrets=new Float64Array(size);node.sums=new Float64Array(size);node.frozen=new Float64Array(size);node.values=new Float64Array(size);node.valueSquares=new Float64Array(size);node.prob=new Float64Array(node.actions.length);node.childValues=new Float64Array(node.actions.length);node.visits=new Uint32Array(169);node.ownW=new Float64Array(169);node.ownW2=new Float64Array(169);node.evW=new Float64Array(169);node.evW2=new Float64Array(169);node.evalVisits=new Uint32Array(169);decisions.push(node);node.children=node.actions.map(a=>visit(Poker.apply(s,a)));return node.id;
    }visit(Poker.initial(options.config));return {options,nodes,decisions,n,trained:0,evaluated:0,rootChanges:[],previousRoot:null};
  }
  function strategy(node,h,phase){const k=node.actions.length,base=h*k,p=node.prob;let denom=0;for(let a=0;a<k;a++){p[a]=phase==='train'?Math.max(0,node.regrets[base+a]):node.frozen[base+a];denom+=p[a]}for(let a=0;a<k;a++)p[a]=denom>EPS?p[a]/denom:1/k;return p}
  function walk(game,id,d,r0,r1,r2,phase,average){const node=game.nodes[id];if(node.terminal)return payoff(node.terminal,d.scores,node.u);
    const actor=node.actor,h=d.indices[actor],k=node.actions.length,base=h*k,prob=strategy(node,h,phase),own=actor===0?r0:actor===1?r1:r2,other=actor===0?r1*r2:actor===1?r0*r2:r0*r1;
    node.u.fill(0);for(let a=0;a<k;a++){const v=walk(game,node.children[a],d,actor===0?r0*prob[a]:r0,actor===1?r1*prob[a]:r1,actor===2?r2*prob[a]:r2,phase,average);node.childValues[a]=v[actor];for(let p=0;p<game.n;p++)node.u[p]+=prob[a]*v[p]}
    if(phase==='train'){node.visits[h]++;for(let a=0;a<k;a++)node.regrets[base+a]+=other*(node.childValues[a]-node.u[actor]);if(average){node.ownW[h]+=own;node.ownW2[h]+=own*own;for(let a=0;a<k;a++)node.sums[base+a]+=own*prob[a]}}
    else{node.evalVisits[h]++;node.evW[h]+=other;node.evW2[h]+=other*other;for(let a=0;a<k;a++){const v=node.childValues[a];node.values[base+a]+=other*v;node.valueSquares[base+a]+=other*v*v}}
    return node.u;
  }
  function freeze(game){for(const node of game.decisions){const k=node.actions.length;for(let h=0;h<169;h++){const base=h*k;let denom=0;for(let a=0;a<k;a++)denom+=node.sums[base+a];for(let a=0;a<k;a++)node.frozen[base+a]=denom>EPS?node.sums[base+a]/denom:1/k}}}
  function checkpoint(game){freeze(game);const root=game.nodes[0];if(root.terminal)return;const policy=root.frozen;if(game.previousRoot){let delta=0;for(let i=0;i<policy.length;i++)delta+=Math.abs(policy[i]-game.previousRoot[i]);game.rootChanges.push({iteration:game.trained,meanTotalVariation:delta/(2*169)})}game.previousRoot=new Float64Array(policy)}
  function trainStep(game,random){const d=deal(game.n,random);walk(game,0,d,1,1,1,'train',game.trained>=Math.floor(game.options.iterations/10));game.trained++}
  function evaluateStep(game,random){const d=deal(game.n,random),u=walk(game,0,d,1,1,1,'eval',false);game.evaluated++;return u}
  function ess(w,w2){return w2>EPS?w*w/w2:0}
  function result(game){const handNames=Poker.allHands();const nodes=game.decisions.map(node=>{const k=node.actions.length,hands={};for(let h=0;h<169;h++){if(node.ownW[h]<=EPS)continue;const actions=node.actions.map((a,i)=>{const {player,...action}=a,idx=h*k+i,w=node.evW[h],effective=ess(w,node.evW2[h]);let row={...action,frequency:node.frozen[idx]};if(effective>=30){const mean=node.values[idx]/w,variance=Math.max(0,node.valueSquares[idx]/w-mean*mean);row.ev=mean;row.ci95=1.96*Math.sqrt(variance/Math.max(1,effective-1))}return row});hands[handNames[h]]={actions,trainingDeals:node.visits[h],strategyEss:ess(node.ownW[h],node.ownW2[h]),evaluationEss:ess(node.evW[h],node.evW2[h])}}
      return {id:node.id,position:node.position,history:node.history,actions:node.actions.map(({player,...a})=>a),hands};});
    return {version:1,engine:'Expresso Lab CFR v1',options:game.options,trained:game.trained,evaluated:game.evaluated,treeNodes:game.nodes.length,decisionNodes:nodes.length,rootChanges:game.rootChanges,nodes};
  }
  async function run(raw,onProgress=()=>{},yieldFn=()=>new Promise(r=>setTimeout(r,0))){const game=build(raw),random=rng(game.options.seed),evalRandom=rng(game.options.seed^0x9e3779b9),started=Date.now(),batch=100,checkEvery=Math.max(100,Math.floor(game.options.iterations/5));onProgress({phase:'build',done:0,total:game.options.iterations,decisionNodes:game.decisions.length,treeNodes:game.nodes.length});
    for(let i=0;i<game.options.iterations;i++){trainStep(game,random);if((i+1)%checkEvery===0||i+1===game.options.iterations)checkpoint(game);if((i+1)%batch===0){onProgress({phase:'train',done:i+1,total:game.options.iterations,elapsedMs:Date.now()-started});await yieldFn()}}
    freeze(game);for(let i=0;i<game.options.evaluationDeals;i++){evaluateStep(game,evalRandom);if((i+1)%batch===0){onProgress({phase:'evaluate',done:i+1,total:game.options.evaluationDeals,elapsedMs:Date.now()-started});await yieldFn()}}
    const output=result(game);output.elapsedMs=Date.now()-started;return output;
  }
  return {rng,score,straight,evaluate7,handIndex,deal,validateOptions,legalActions,poolsFor,payoff,build,strategy,walk,freeze,checkpoint,trainStep,evaluateStep,result,run,ess};
}
if(typeof module!=='undefined'&&module.exports)module.exports=createPreflopSolver;
