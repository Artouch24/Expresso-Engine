/* Rules: pure preflop state machine. No strategy or UI dependency. */
const Poker = (() => {
  const EPS=1e-7, ranks='AKQJT98765432';
  const near=(a,b)=>Math.abs(a-b)<EPS, round=x=>Math.round(x*1e6)/1e6;
  const fail=m=>{throw new Error(m)};
  const num=(x,name,min=0,max=10000)=>{if(typeof x!=='number'||!Number.isFinite(x)||x<min||x>max||!near(x*1000,Math.round(x*1000)))fail(name+' : nombre valide, avec au plus 3 décimales, attendu.');return x};
  const positions=n=>n===3?['BTN','SB','BB']:['SB','BB'];
  const hand=x=>{if(typeof x!=='string')fail('Main invalide.');let v=x.trim().replace(/10/g,'T');if(!/^[AKQJT2-9]{2}[so]?$/i.test(v))fail('Utilisez AKo, AQs ou 77.');let a=v[0].toUpperCase(),b=v[1].toUpperCase(),s=v.slice(2).toLowerCase();if(a===b){if(s)fail('Une paire ne porte ni s ni o.');return a+b}if(!s)fail('Précisez s (suited) ou o (offsuit).');if(ranks.indexOf(a)>ranks.indexOf(b))[a,b]=[b,a];return a+b+s};
  const allHands=()=>[...ranks].flatMap((a,i)=>[...ranks].map((b,j)=>i===j?a+b:i<j?a+b+'s':b+a+'o'));
  function config(c){
    if(!c||![2,3].includes(c.players))fail('Le format doit être 2 ou 3 joueurs.');const ps=positions(c.players);
    if(!ps.includes(c.hero))fail('Position du héros invalide.');if(!c.stacks||typeof c.stacks!=='object'||Object.keys(c.stacks).sort().join()!==[...ps].sort().join())fail('Un tapis est requis pour chaque position, sans position supplémentaire.');
    const stacks={};ps.forEach(p=>stacks[p]=num(c.stacks[p],'Tapis '+p,.001));
    const sb=num(c.sb,'Petite blinde',.001,1),ante=num(c.ante,'Ante'),rake=num(c.rake,'Rake',0,100);
    if(!['each','bb'].includes(c.anteMode))fail('Convention d’ante invalide.');if(!['chipEV','payoutEV'].includes(c.objective))fail('Objectif invalide.');
    if(!Array.isArray(c.payouts)||c.payouts.length!==c.players)fail('Indiquez un gain par place, séparé par une virgule.');const payouts=c.payouts.map(v=>num(v,'Gain',0,1e9));if(payouts.reduce((a,b)=>a+b,0)<=0||payouts.some((v,i)=>i&&v>payouts[i-1]))fail('Les gains doivent décroître et leur somme être positive.');
    return {players:c.players,hero:c.hero,stacks,sb,ante,anteMode:c.anteMode,objective:c.objective,payouts,rake};
  }
  function initial(c){c=config(c);let ps=positions(c.players);let seats={};for(let p of ps){let blind=p==='BB'?1:p==='SB'?c.sb:0,paid=Math.min(blind,c.stacks[p]);let ante=Math.min((c.anteMode==='each'||p==='BB')?c.ante:0,c.stacks[p]-paid);seats[p]={p,paid:round(paid),ante:round(ante),cap:round(c.stacks[p]-ante),folded:false,lastFaced:null,lastIncrement:1}}return {config:c,ps,seats,bet:1,increment:1,raises:0,cursor:-1,history:[]}}
  const remaining=(s,p)=>round(s.seats[p].cap-s.seats[p].paid);
  const live=s=>s.ps.filter(p=>!s.seats[p].folded);
  function target(s,p){const others=live(s).filter(q=>q!==p);return others.every(q=>remaining(s,q)<=EPS)?Math.min(s.bet,Math.max(0,...others.map(q=>s.seats[q].paid))):s.bet}
  function next(s){const alive=live(s);if(alive.length<2)return null;const can=alive.filter(p=>remaining(s,p)>EPS);if(!can.length)return null;if(can.length===1&&s.seats[can[0]].paid>=target(s,can[0])-EPS)return null;for(let k=1;k<=s.ps.length;k++){const p=s.ps[(s.cursor+k)%s.ps.length],v=s.seats[p];if(!v.folded&&remaining(s,p)>EPS&&(v.lastFaced===null||v.paid<target(s,p)-EPS))return p}return null}
  function options(s){const p=next(s);if(!p)return null;const v=s.seats[p],t=target(s,p),owed=round(Math.max(0,Math.min(t,v.cap)-v.paid));const reopened=v.lastFaced===null||s.bet-v.lastFaced>=v.lastIncrement-EPS;const responders=live(s).some(q=>q!==p&&remaining(s,q)>EPS);const min=round(s.bet+s.increment),canRaise=reopened&&responders&&v.cap>s.bet+EPS;return {p,owed,callTo:round(v.paid+owed),min,max:v.cap,canRaise,reopened,responders,canFullRaise:canRaise&&v.cap>=min-EPS,canJam:(owed>EPS&&v.cap<=t+EPS)||canRaise,passive:owed<=EPS?'check':near(v.cap,v.paid+owed)?'allin':s.raises===0&&near(t,1)?'limp':'call'}}
  function apply(s,action){if(!action||typeof action!=='object')fail('Action invalide.');let o=options(s);if(!o)fail('Le tour préflop est terminé.');if(action.player!==o.p)fail('C’est à '+o.p+' de parler.');let v=s.seats[o.p],type=action.type,to=v.paid;const allowed=['fold','check','limp','call','raise','3bet','allin'];if(!allowed.includes(type))fail('Type d’action inconnu.');if(type==='3bet'){if(s.raises!==1)fail('Un 3-bet doit suivre une seule relance.');type='raise'}
    if(type==='fold'){if(o.owed<=EPS)fail('Vous pouvez checker gratuitement.');}
    else if(type==='check'){if(o.owed>EPS)fail('Impossible de checker : une mise reste à payer.');}
    else if(type==='call'||type==='limp'){if(o.owed<=EPS)fail('Aucune mise à suivre.');if(type==='limp'&&(s.raises!==0||!near(target(s,o.p),1)))fail('Un limp est impossible après une relance.');to=o.callTo;type=o.passive;}
    else if(type==='allin'){if(!o.canJam)fail('L’all-in ne peut pas relancer : action non rouverte ou aucun adversaire avec des jetons.');to=v.cap;}
    else if(type==='raise'){if(!o.canFullRaise)fail('Relance complète impossible dans cette situation.');to=num(action.to,'Total de relance',.001);if(to<o.min-EPS)fail('Relance minimale à '+o.min+' BB au total.');if(to>v.cap+EPS)fail('La relance dépasse le tapis disponible.');if(near(to,v.cap))type='allin'}
    if(['fold','check'].includes(type)){if(action.to!==undefined)fail('Fold et check ne prennent pas de montant.');}else if(action.to!==undefined&&!near(num(action.to,'Total engagé'),to))fail('Le montant doit être '+to+' BB au total pour cette action.');
    const out=JSON.parse(JSON.stringify(s)),a=out.seats[o.p];if(type==='fold')a.folded=true;else a.paid=round(to);
    if(to>s.bet+EPS){let delta=round(to-s.bet);out.bet=round(to);out.raises++;if(delta>=s.increment-EPS)out.increment=delta;}
    a.lastFaced=out.bet;a.lastIncrement=out.increment;out.cursor=out.ps.indexOf(o.p);
    const normalized={player:o.p,type};if(!['fold','check'].includes(type))normalized.to=round(to);out.history.push(normalized);return out;
  }
  function replay(c,h=[]){if(!Array.isArray(h)||h.length>100)fail('Historique invalide ou trop long.');let s=initial(c);h.forEach((a,i)=>{try{s=apply(s,a)}catch(e){fail('Action '+(i+1)+' : '+e.message)}});return s}
  const key=(c,h)=>{const s=replay(c,h);return JSON.stringify({config:s.config,history:s.history})};
  const actionKey=a=>JSON.stringify({type:a.type,...(a.to!==undefined?{to:a.to}:{})});
  return {EPS,near,round,fail,num,positions,hand,allHands,config,initial,remaining,live,next,options,apply,replay,key,actionKey};
})();
/* Ranges: exact matching and atomic, untrusted JSON validation. */
const RangeData=(()=>{
  const kinds={reference:'Range de référence déclarée',computed:'Calcul documenté déclaré',heuristic:'Approximation pédagogique',demo:'DÉMO FICTIVE'};
  const txt=(x,n)=>{if(typeof x!=='string'||!x.trim()||x.length>12000)Poker.fail(n+' : texte non vide requis.');return x.trim()};
  function validate(raw){if(!raw||raw.schemaVersion!==1)Poker.fail('schemaVersion doit valoir 1.');const p=raw.provenance;if(!p||!Object.hasOwn(kinds,p.kind))Poker.fail('Provenance manquante ou invalide.');const provenance={kind:p.kind,title:txt(p.title,'Titre de la source'),reference:txt(p.reference,'Référence'),assumptions:txt(p.assumptions,'Hypothèses'),postflop:txt(p.postflop,'Modèle postflop')};if(p.evUnit!==undefined)provenance.evUnit=txt(p.evUnit,'Unité d’EV');
    if(!Array.isArray(raw.spots)||!raw.spots.length||raw.spots.length>3000)Poker.fail('La bibliothèque doit contenir de 1 à 3 000 situations.');let seen=new Set();
    const spots=raw.spots.map((spot,i)=>{try{const state=Poker.replay(spot.config,spot.history);if(Poker.next(state)!==state.config.hero)Poker.fail('La situation doit s’arrêter au tour du héros.');const key=Poker.key(state.config,state.history);if(seen.has(key))Poker.fail('Situation en doublon.');seen.add(key);if(!spot.hands||typeof spot.hands!=='object'||Array.isArray(spot.hands)||Object.keys(spot.hands).length>169)Poker.fail('Dictionnaire hands invalide.');const hands={};for(const [h,v] of Object.entries(spot.hands)){if(Poker.hand(h)!==h)Poker.fail('Main non canonique : '+h);if(!v||!Array.isArray(v.actions)||!v.actions.length||v.actions.length>30)Poker.fail(h+' : actions manquantes ou trop nombreuses.');let sum=0,keys=new Set();const actions=v.actions.map(a=>{if(!a||typeof a.frequency!=='number'||!Number.isFinite(a.frequency)||a.frequency<0||a.frequency>1)Poker.fail(h+' : fréquence attendue entre 0 et 1.');sum+=a.frequency;const ns=Poker.apply(state,{player:state.config.hero,type:a.type,...(a.to!==undefined?{to:a.to}:{})});const {player,...norm}=ns.history.at(-1);let ak=Poker.actionKey(norm);if(keys.has(ak))Poker.fail(h+' : action en doublon.');keys.add(ak);let normalized={...norm,frequency:a.frequency};if(a.ev!==undefined){if(!['reference','computed'].includes(p.kind)||!provenance.evUnit||typeof a.ev!=='number'||!Number.isFinite(a.ev))Poker.fail(h+' : EV réservée aux sources documentées, avec une unité.');normalized.ev=a.ev}return normalized});if(!Poker.near(sum,1))Poker.fail(h+' : la somme des fréquences doit valoir 1.');hands[h]={actions,explanation:txt(v.explanation,h+' : explication')}}return {label:txt(spot.label,'Libellé'),config:state.config,history:state.history,hands};}catch(e){Poker.fail('Situation '+(i+1)+' : '+e.message)}});
    return {schemaVersion:1,name:txt(raw.name,'Nom de bibliothèque'),provenance,spots};
  }
  const indexes=new WeakMap();
  const match=(pack,c,h)=>{if(!pack)return null;let index=indexes.get(pack);if(!index){index=new Map(pack.spots.map(s=>[Poker.key(s.config,s.history),s]));indexes.set(pack,index)}return index.get(Poker.key(c,h))||null};
  return {kinds,validate,match};
})();
