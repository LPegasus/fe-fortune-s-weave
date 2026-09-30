'use strict';
let D=window.GUIDE_DATA;
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function portraitMarkup(c){return c.portrait?`<span class="monogram portrait"><img src="${esc(c.portrait.src)}" alt="${esc(c.portrait.alt)}" width="${c.portrait.width}" height="${c.portrait.height}" decoding="async"></span>`:`<span class="monogram" aria-hidden="true">◇</span>`;}
function itemRef(i){const s=D.sources.find(s=>s.id===(i.quantitySourceId||i.sourceIds[0]));return s?` <a class="item-ref" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer" title="${esc(s.title)}" aria-label="查阅${esc(i.name)}的来源">↗</a>`:'';}
const types={items:'道具店',weapons:'武器店',market:'市场',vandhal:'旺达尔商会',gifts:'礼物店',travel:'旅行商人'};
let view='gifts',characterId='character-2',placeId='place-1',shopType='items';
let ready=false;
// Each view keeps its own filters when switching sections or sharing a URL.
const urlFields=[
  {id:'gift-search',param:'giftSearch',defaultValue:''},
  {id:'preference',param:'preference',defaultValue:'all'},
  {id:'overview-search',param:'overviewSearch',defaultValue:''},
  {id:'shop-search',param:'shopSearch',defaultValue:''},
  {id:'place-kind',param:'placeKind',defaultValue:'all'}
];
function restoreUrlState(){
  if(!ready)return;
  const params=new URLSearchParams(location.search);
  for(const field of urlFields){
    const control=$(field.id),value=params.get(field.param)??field.defaultValue;
    control.value=control.tagName==='SELECT'&&![...control.options].some(o=>o.value===value)?field.defaultValue:value;
  }
  characterId=D.gifts.characters.some(c=>c.id===params.get('character'))?params.get('character'):'character-2';
  placeId=D.shops.locations.some(l=>l.id===params.get('place'))?params.get('place'):'place-1';
  shopType=Object.hasOwn(types,params.get('shop'))?params.get('shop'):'items';
  setView(['gifts','overview','shops','sources'].includes(location.hash.slice(1))?location.hash.slice(1):'gifts');
}
function syncUrlState(mode='replace'){
  const url=new URL(location.href);
  const put=(name,value,defaultValue)=>{if(value&&value!==defaultValue)url.searchParams.set(name,value);else url.searchParams.delete(name)};
  for(const field of urlFields)put(field.param,$(field.id).value,field.defaultValue);
  put('character',characterId,'character-2');put('place',placeId,'place-1');put('shop',shopType,'items');
  url.hash=view;
  if(url.href!==location.href)history[mode==='push'?'pushState':'replaceState'](null,'',url.href);
}
function navigate(v){setView(v);syncUrlState('push');}
const canonical=s=>({'髭飾り':'鬣飾り','鰣飾り':'鬣飾り','間接保護用長手袋':'関節保護用長手袋','魚の内蔵の塩漬け':'魚の内臓の塩漬け','栄養満点お菓子本':'栄養満点のお菓子本'}[s]||s);
const includes=(s,q)=>s.toLocaleLowerCase().includes(q.toLocaleLowerCase());
function ref(ids){return [...new Set(ids)].map(id=>{const s=D.sources.find(x=>x.id===id);return s?`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title.split(' · ')[0])} · ${s.language==='zh'?'中':s.language==='en'?'EN':'日'}</a>`:''}).join('');}
function num(i){return i.stockStatus==='unlimited'?'<span class="unlimited" aria-label="无限库存">∞</span>':i.stockStatus==='unknown'?'<span class="unknown">待确认</span>':i.stock;}
function stat(n,label,en){return `<div class="stat"><strong>${n}</strong><span>${label}<small>${en}</small></span></div>`;}
function setView(v){hideAliasPopover();view=v;document.querySelectorAll('.view').forEach(x=>x.hidden=x.id!==v+'-view');document.querySelectorAll('.nav').forEach(x=>{x.classList.toggle('active',x.dataset.view===v);x.setAttribute('aria-current',x.dataset.view===v?'page':'false')});
const copy={overview:['GIFT PREFERENCES AT A GLANCE','送礼总览','所有人物的礼物偏好，放在一起轻松对照。','gifts.json'],gifts:['THE GIFT COMPANION','一份礼物，一段羁绊','查询每位人物非常喜欢与喜欢的礼物，出发前准备一份恰好的心意。','gifts.json'],shops:['THE TRAVELER’S MARKET','下一站，需要买什么','据点与准据点的商店清单，商品、库存与商会兑换材料一览。','shops.json'],sources:['RESEARCH & REFERENCES','沿着线索，查到出处','查阅资料覆盖范围、已知差异，以及中文、英文、日文来源。','sources.json']}[v];
$('eyebrow').textContent=copy[0];$('page-title').innerHTML=esc(copy[1])+'<span>。</span>';$('subtitle').textContent=copy[2];$('download').href='data/'+copy[3];
const items=D.shops.locations.flatMap(l=>l.shops.flatMap(s=>s.items));
$('stats').innerHTML=(v==='gifts'||v==='overview')?stat(D.gifts.characters.length,'人物已收录','CHARACTERS')+stat(D.gifts.characters.filter(c=>c.loves.length||c.likes.length).length,'人物有明确偏好','DOCUMENTED')+stat(new Set(D.gifts.characters.flatMap(c=>[...c.loves,...c.likes].map(x=>x.nameJa||x.name))).size,'礼物 / 类别记录','GIFT INDEX'):v==='shops'?stat(D.shops.locations.length,'地点已收录','LOCATIONS')+stat(items.length,'商品销售记录','SHOP RECORDS')+stat(items.filter(x=>x.stockStatus!=='unknown').length,'记录有明确库存','QUANTITY KNOWN'):stat(3,'来源语言','LANGUAGES')+stat(D.sources.length,'参考页面','REFERENCES')+stat('10.01','2026 年资料快照','LAST COLLECTED');
if(v==='overview')renderOverview();if(v==='gifts')renderCharacters();if(v==='shops')renderPlaces();if(v==='sources')renderSources();}

function giftFlags(g){return g.preferenceConflict?'<small class="conflict-badge" title="不同来源分别记为非常喜欢和喜欢，按并集保留；请以游戏实测为准">来源分歧</small>':g.preferenceConflicts?.length?'<small class="correction-badge" title="来源等级不同，以用户确认记录为准">用户确认</small>':'';}
function giftEvidence(c){
const rows=['loves','likes'].flatMap(k=>c[k].map(g=>({k,g})));
if(!rows.some(({g})=>g.sourceObservations?.length))return '';
return `<details class="gift-evidence"><summary>查看礼物来源与译名对照</summary><p>新增中文资料主要转译 Game8；来源分歧保留在两栏，用户确认记录优先。类别推测未展开成具体礼物。</p><div class="table-wrap"><table><thead><tr><th>礼物 / 当前等级</th><th>来源记录</th></tr></thead><tbody>${rows.map(({k,g})=>`<tr><td>${nameWithAliases('items',g)}<small>${esc(g.nameJa)}</small><small>${k==='loves'?'非常喜欢':'喜欢'}</small></td><td><div class="source-links">${ref(g.sourceIds)}</div>${(g.sourceObservations||[]).map(o=>`<p><a href="${esc(o.sourceUrl)}" target="_blank" rel="noopener noreferrer">中文站</a>：${esc(o.rawName)} · ${o.preference==='loves'?'非常喜欢':'喜欢'}</p>`).join('')}${g.preferenceCorrection?`<p>${esc(g.preferenceCorrection.note)}</p>`:''}</td></tr>`).join('')}</tbody></table></div></details>`;
}
function shopEvidence(i){return i.sourceObservations?.length?`<details class="shop-observations"><summary>中文站记录 · ${i.sourceObservations.length}</summary>${i.sourceObservations.map(o=>`<div><a href="${esc(o.sourceUrl)}" target="_blank" rel="noopener noreferrer">${esc(o.rawName)}</a><p>${esc(o.context)}</p><p>${o.stock===null?'未列库存':`截图剩余 ${o.stock} 件`}${o.price===null?'':` · ${o.price.toLocaleString()} G`}</p>${o.exchange.length?`<p>兑换：${o.exchange.map(m=>`${nameWithAliases('items',m)} × ${m.quantity}${m.rawName!==m.name?`（原文：${esc(m.rawName)}）`:''}`).join(' + ')}</p>`:''}</div>`).join('')}</details>`:'';}

function renderOverview(){hideAliasPopover();
const q=$('overview-search').value.trim();
const characters=D.gifts.characters.filter(c=>!q||includes([c.name,c.nameJa,c.nameEn,...[...c.loves,...c.likes].flatMap(g=>[g.name,g.nameJa||''])].join(' '),q));
$('overview-count').textContent=`${characters.length} / ${D.gifts.characters.length}`;
const gifts=(items,key)=>items.length?`<ul class="overview-gifts ${key}">${items.map(g=>`<li aria-label="${esc([g.name,g.nameJa,g.preferenceCorrection?.note].filter(Boolean).join(' · '))}">${nameWithAliases('items',g)}${g.kind==='category'?'<small>类别</small>':''}${giftFlags(g)}</li>`).join('')}</ul>`:'<span class="overview-empty">暂无记录</span>';
$('overview-rows').innerHTML=characters.length?characters.map(c=>`<tr data-overview-row="${c.id}"><th scope="row"><a class="overview-person" href="#gifts" data-overview-character="${c.id}" aria-label="查看${esc(c.name)}的送礼详情">${portraitMarkup(c)}<span><strong>${nameWithAliases('characters',c,true)}</strong><small>${esc(c.nameEn)}</small></span></a></th><td>${gifts(c.loves,'loves')}</td><td>${gifts(c.likes,'likes')}</td></tr>`).join(''):'<tr><td colspan="3" class="overview-no-results">没有找到匹配人物或礼物，试试其他关键词。</td></tr>';
}
function renderCharacters(){hideAliasPopover();const q=$('gift-search').value.trim(),pref=$('preference').value;
const filtered=D.gifts.characters.filter(c=>{if(pref==='unknown'&&(c.loves.length||c.likes.length))return false;const lists=pref==='loves'?c.loves:pref==='likes'?c.likes:[...c.loves,...c.likes];if((pref==='loves'||pref==='likes')&&!lists.length)return false;return !q||includes([c.name,c.nameJa,c.nameEn,...lists.map(i=>i.name+' '+(i.nameJa||''))].join(' '),q)});
$('character-count').textContent=filtered.length;if(!filtered.some(c=>c.id===characterId))characterId=filtered[0]?.id;
$('characters').innerHTML=filtered.length?filtered.map(c=>`<button class="character ${c.id===characterId?'selected':''}" data-character="${c.id}" aria-pressed="${c.id===characterId}">${portraitMarkup(c)}<span><strong>${nameWithAliases('characters',c,true)}</strong><small>${esc(c.nameEn)}</small></span><em>${c.loves.length+c.likes.length||'待确认'}</em></button>`).join(''):'<div class="result-empty">没有找到匹配人物。<br>试试更短的关键词。</div>';
if(characterId)renderCharacter();else $('character-detail').innerHTML='<div class="blank">没有符合条件的记录。</div>';}
function renderCharacter(){hideAliasPopover();const c=D.gifts.characters.find(c=>c.id===characterId);if(!c)return;
$('character-detail').innerHTML=`<div class="detail-head">${portraitMarkup(c)}<div><h2>${nameWithAliases('characters',c)}</h2><div class="aliases">${esc(c.nameEn)} <span> / </span> ${esc(c.nameJa)}</div></div><span class="record-no">NO. ${c.id.split('-')[1].padStart(2,'0')}</span></div><div class="detail-body">${['loves','likes'].map(k=>`<section class="gift-section ${k}"><div class="gift-heading"><span class="heart ${k==='likes'?'like-heart':''}">${k==='loves'?'♥':'♡'}</span><h3>${k==='loves'?'非常喜欢':'喜欢'}</h3><span class="count">${c[k].length} 项记录</span></div><div class="gift-tags">${c[k].length?c[k].map((g,i)=>`<button class="gift-tag" data-gift-key="${k}" data-gift-index="${i}" aria-label="查看${esc(g.name)}的销售地点"><span>${nameWithAliases('items',g,true)}</span>${g.nameJa&&g.name!==g.nameJa?`<small>${esc(g.nameJa)}</small>`:''}${g.kind==='category'?'<small>类别推荐</small>':''}${giftFlags(g)}</button>`).join(''):'<div class="empty-note">来源尚未列出明确礼物，不代表没有喜好。</div>'}</div></section>`).join('')}<div id="purchase"></div>${giftEvidence(c)}<div class="record-note">礼物名称保留日文以便对照。点击礼物可查看已收录的销售地点。${(c.notes||[]).map(n=>`<p>${esc(n)}</p>`).join('')}<div class="source-links">${ref(c.sourceIds)}</div></div></div>`;}
function showPurchase(key,index){hideAliasPopover();const c=D.gifts.characters.find(c=>c.id===characterId),g=c[key][index];const hits=[];for(const l of D.shops.locations)for(const s of l.shops)for(const i of s.items)if(g.nameJa&&canonical(i.nameJa)===canonical(g.nameJa))hits.push({l,s,i});$('purchase').innerHTML=`<section class="purchase"><button class="close" id="close-purchase" aria-label="关闭销售地点">×</button><h4>${nameWithAliases('items',g)} · 在哪里买</h4>${hits.length?hits.map(({l,s,i})=>`<a href="#shops" data-jump-place="${l.id}" data-jump-shop="${s.type}">${nameWithAliases('locations',l,true)} / ${types[s.type]} · 库存 ${i.stockStatus==='unlimited'?'∞':i.stockStatus==='unknown'?'待确认':i.stock}</a>`).join(''):'当前商店资料未找到销售记录；可按原名查阅来源，不能据此判断无法购买。'}</section>`;}
function renderPlaces(){hideAliasPopover();const q=$('shop-search').value.trim(),kind=$('place-kind').value;const rows=D.shops.locations.filter(l=>(kind==='all'||l.type===kind)&&(!q||includes([l.name,l.nameJa,...(l.aliases||[])].join(' '),q)||l.shops.some(s=>s.items.some(i=>includes(i.name+' '+(i.nameJa||''),q)))));if(!rows.some(l=>l.id===placeId))placeId=rows[0]?.id;
$('places').innerHTML=rows.length?rows.map(l=>`<button class="place-button ${l.id===placeId?'selected':''}" data-place="${l.id}" aria-pressed="${l.id===placeId}"><strong>${nameWithAliases('locations',l,true)}</strong><small>${l.nameJa&&l.name!==l.nameJa?esc(l.nameJa)+' · ':''}${esc(l.type)}</small></button>`).join(''):'<div class="result-empty">没有找到匹配地点或商品。</div>';if(placeId)renderShop();else $('shop-detail').innerHTML='<div class="blank">没有符合条件的商店记录。</div>';}
function renderShop(){hideAliasPopover();const l=D.shops.locations.find(l=>l.id===placeId);if(!l)return;const q=$('shop-search').value.trim();let shop=l.shops.find(s=>s.type===shopType);if(!shop)shop=l.shops[0];
const locationMatches=!q||includes([l.name,l.nameJa,...(l.aliases||[])].join(' '),q);if(!locationMatches&&!shop.items.some(i=>includes(i.name+' '+(i.nameJa||''),q)))shop=l.shops.find(s=>s.items.some(i=>includes(i.name+' '+(i.nameJa||''),q)))||shop;shopType=shop.type;
const items=shop.items.filter(i=>locationMatches||includes(i.name+' '+(i.nameJa||''),q));
$('shop-detail').innerHTML=`<div class="detail-head shop-head"><div class="eyebrow">${esc(l.type)} · WORLD MAP</div><h2>${nameWithAliases('locations',l)}</h2><div class="aliases">${esc(l.nameJa)}</div></div><div class="shop-tabs" role="tablist" aria-label="店铺类型">${Object.keys(types).filter(k=>l.shops.some(s=>s.type===k)).map(k=>{const s=l.shops.find(s=>s.type===k);return `<button class="shop-tab ${k===shopType?'selected':''}" role="tab" aria-selected="${k===shopType}" data-shop="${k}">${types[k]}<small>${s.items.length||'—'}</small></button>`}).join('')}</div>${items.length?`<div class="table-wrap"><table><thead><tr><th scope="col">商品</th><th scope="col">库存</th><th scope="col">${shopType==='vandhal'?'兑换材料 / 每次':'价格 / G'}</th></tr></thead><tbody>${items.map(i=>`<tr><td class="name-cell">${nameWithAliases('items',i)}${itemRef(i)}${i.nameJa&&i.name!==i.nameJa?`<small>${esc(i.nameJa)}</small>`:''}${shopEvidence(i)}</td><td class="quantity">${num(i)}${i.stockMeaning==='observed_remaining'?'<small>截图剩余</small>':''}</td><td class="cost">${shopType==='vandhal'?(i.exchange.length?i.exchange.map(m=>`<span class="material">${nameWithAliases('items',{...m,name:m.name||m.nameJa})} × ${m.quantity}</span>`).join(''):'<span class="unknown">待确认</span>'):(i.price===null?'<span class="unknown">待确认</span>':i.price.toLocaleString())}${i.alternativePrices?.length?'<span class="alternative" title="不同来源的价格可能受章节或折扣影响，见 JSON 中的 alternativePrices">有不同来源价格</span>':''}</td></tr>`).join('')}</tbody></table></div>`:`<div class="blank">${shop.status==='not_listed'?'参考资料未列出此类店铺。<br>这不等同于已确认店铺不存在。':'没有匹配的商品。'}</div>`}<div class="table-note">${items.length?`已列出 ${items.length} 种商品。`:''}库存与价格为来源快照；展开商品的“中文站记录”可对照截图剩余库存及不同兑换方案。${(shop.notes||[]).map(n=>`<p>${esc(n)}</p>`).join('')}${(l.notes||[]).map(n=>`<p>${esc(n)}</p>`).join('')}<div class="source-links">${ref(l.sourceIds)}</div>${shopType==='vandhal'?englishEvidence(l):''}</div>`;}
function englishEvidence(l){const map={'帝都ダグシオン':'Dagsion','海都アレクトー':'Alecto (Saveilon)','ライ・オーの港':'Raivo Port (Melias)','マオン城郭':'Mahon Castle Town (Solidus)','ゴーラ草原帯':'Gaura Grassland (Amalthea)','黒翼の谷':'Valley of Black Wings (Idya)','フィーナの岩礁':'Fina Reef (Castalia)','サンタナ橋':'Santana Bridge (Amalthea)','ペルーサ岬':'Peluza Cape (Elektra)','笑み岩':'Smiling Stone (Lambath)','ゾトー湖':'Zeet Lake (Thaleia)'};const en=D.shops.englishExchangeObservations.find(x=>x.locationEn===map[l.nameJa]);return en?`<details class="evidence"><summary>查看英文站兑换记录（可能与日文资料不同）</summary><p>英文来源未列商品库存；这里的数字为所需材料数量，保留原文对照。</p><table class="en-table"><thead><tr><th>Item</th><th>Materials</th></tr></thead><tbody>${en.items.map(i=>`<tr><td>${esc(i.nameEn)}</td><td>${esc(i.exchangeEn)}</td></tr>`).join('')}</tbody></table><div class="source-links">${ref(en.sourceIds)}</div></details>`:'';}
function renderSources(){const unknown=D.gifts.characters.filter(c=>!c.loves.length&&!c.likes.length);const missing=D.shops.locations.flatMap(l=>l.shops.flatMap(s=>s.items.filter(i=>i.stockStatus==='unknown').map(i=>l.name+' / '+types[s.type]+' / '+i.name)));
$('coverage').innerHTML=`<div class="coverage"><strong>当前资料缺口</strong><p>${unknown.length} 位人物尚无明确礼物记录：${unknown.map(c=>esc(c.name)).join('、')||'无'}。</p><p>${missing.length} 条商店商品记录缺少库存数量；已用“待确认”显示。未列明的章节、路线和解锁条件保持未确认状态。</p><details><summary>展开缺少库存的商品</summary><ul>${missing.map(s=>`<li>${esc(s)}</li>`).join('')}</ul></details></div>`;
const langs={ja:'日本語 · 日文',zh:'中文',en:'English · 英文'};$('sources').innerHTML=Object.entries(langs).map(([lang,name])=>{const sources=D.sources.filter(s=>s.language===lang);const card=s=>`<div class="source-card"><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a><small>${esc(s.note)}</small></div>`;return `<section class="source-group"><h3>${name} <span class="place-type">${sources.length} 页</span></h3>${sources.slice(0,3).map(card).join('')}${sources.length>3?`<details><summary>查看其余 ${sources.length-3} 个参考页面</summary>${sources.slice(3).map(card).join('')}</details>`:''}</section>`}).join('');}
document.addEventListener('click',e=>{
  const button=e.target.closest('button,a');if(!button||!ready)return;
  if(button.dataset.overviewCharacter){e.preventDefault();characterId=button.dataset.overviewCharacter;$('gift-search').value='';$('preference').value='all';navigate('gifts');return}
  if(button.dataset.view){e.preventDefault();navigate(button.dataset.view);return}
  if(button.dataset.character){characterId=button.dataset.character;renderCharacters();syncUrlState()}
  if(button.dataset.place){placeId=button.dataset.place;renderPlaces();syncUrlState()}
  if(button.dataset.shop){shopType=button.dataset.shop;renderShop();syncUrlState()}
  if(button.dataset.giftKey)showPurchase(button.dataset.giftKey,Number(button.dataset.giftIndex));
  if(button.id==='close-purchase')$('purchase').innerHTML='';
  if(button.dataset.jumpPlace){e.preventDefault();placeId=button.dataset.jumpPlace;shopType=button.dataset.jumpShop;$('shop-search').value='';$('place-kind').value='all';navigate('shops')}
});
for(const field of urlFields){
  const control=$(field.id);
  control.addEventListener(control.tagName==='SELECT'?'change':'input',()=>{if(!ready)return;setView(view);syncUrlState()});
}
window.addEventListener('hashchange',e=>{if(e.newURL===location.href)restoreUrlState()});
window.addEventListener('popstate',restoreUrlState);
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','SELECT','TEXTAREA'].includes(document.activeElement.tagName)){e.preventDefault();$({gifts:'gift-search',overview:'overview-search',shops:'shop-search'}[view])?.focus()}});
async function init(){if(location.protocol!=='file:'){try{const data=await Promise.all(['gifts','shops','sources','name-aliases'].map(n=>fetch('data/'+n+'.json').then(r=>{if(!r.ok)throw new Error(n);return r.json()})));D={gifts:data[0],shops:data[1],sources:data[2],nameAliases:data[3]};}catch(e){console.warn('Using bundled JSON snapshot',e)}}if(!D){$('stats').innerHTML='<p class="error">数据未能载入，请保持 HTML 与 data.js 位于同一目录。</p>';return}indexAliases();ready=true;restoreUrlState()}
init();
