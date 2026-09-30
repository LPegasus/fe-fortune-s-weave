'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=__dirname;
const data={};
for(const name of ['gifts','shops','sources']) data[name]=JSON.parse(fs.readFileSync(path.join(root,'data',name+'.json'),'utf8').replace(/^\uFEFF/,''));
data.nameAliases=JSON.parse(fs.readFileSync(path.join(root,'data','name-aliases.json'),'utf8').replace(/^\uFEFF/,''));
// Never publish overlapping preference lists from hand-edited JSON.
const identities=new Map();
for(const item of data.nameAliases.items)for(const name of [item.nameJa,item.canonicalName,...item.aliases])if(name)identities.set(name,item.nameJa||item.canonicalName);
const identity=item=>identities.get(item.nameJa)||identities.get(item.name)||item.nameJa||item.name;
for(const character of data.gifts.characters){
  const loves=new Set(character.loves.map(identity));
  if(character.likes.some(item=>loves.has(identity(item))))throw new Error(`${character.name} 的两类喜好存在重复物品，请先运行 python normalize_names.py 应用“非常喜欢优先”规则。`);
}
fs.writeFileSync(path.join(root,'data.js'),'window.GUIDE_DATA = '+JSON.stringify(data)+';\n','utf8');
console.log('Offline data synchronized.');
