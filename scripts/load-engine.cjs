const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const context=vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../src/rules.js'),'utf8')+'\nglobalThis.rules=Poker;',context);
module.exports=require('../src/solver.js')(context.rules);
