'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=__dirname;
const data={};
for(const name of ['gifts','shops','sources']) data[name]=JSON.parse(fs.readFileSync(path.join(root,'data',name+'.json'),'utf8').replace(/^\uFEFF/,''));
fs.writeFileSync(path.join(root,'data.js'),'window.GUIDE_DATA = '+JSON.stringify(data)+';\n','utf8');
console.log('Offline data synchronized.');
