const assert=require('node:assert/strict'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
const params=async p=>new URL(await p.evaluate(()=>location.href)).searchParams;
async function snapshot(page){return page.evaluate(()=>({
  fields:['gift-search','preference','overview-search','shop-search','place-kind'].map(id=>document.getElementById(id).value),
  view:document.querySelector('.view:not([hidden])').id,
  people:[...document.querySelectorAll('.view:not([hidden]) .character')].map(e=>e.dataset.character),
  places:[...document.querySelectorAll('.view:not([hidden]) .place-button')].map(e=>e.dataset.place),
  selectedPlace:document.querySelector('.view:not([hidden]) .place-button.selected')?.dataset.place,
  selectedShop:document.querySelector('.view:not([hidden]) .shop-tab.selected')?.dataset.shop,
  selectedCharacter:document.querySelector('.view:not([hidden]) .character.selected')?.dataset.character
}))}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  for(const base of ['http://127.0.0.1:4175/',pathToFileURL(path.join(__dirname,'index.html')).href]){
   const page=await browser.newPage(),errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.message)});
   await page.goto(base+'?ref=share#shops');await page.waitForSelector('.place-button');
   await page.locator('#shop-search').fill('手斧');await page.locator('#place-kind').selectOption('据点');
   assert.equal((await params(page)).get('shopSearch'),'手斧');assert.equal((await params(page)).get('placeKind'),'据点');assert.equal((await params(page)).get('ref'),'share');
   await page.locator('.place-button').last().click();
   const expected=await snapshot(page),shared=await page.evaluate(()=>location.href);
   await page.reload();await page.waitForSelector('.place-button');
   assert.deepEqual(await snapshot(page),expected,'Reload must restore all shop filters and selection');
   const recipient=await browser.newPage();await recipient.goto(shared);await recipient.waitForSelector('.place-button');
   assert.deepEqual(await snapshot(recipient),expected,'Fresh shared link must restore state');await recipient.close();
   await page.locator('[data-view="gifts"]').click();await page.locator('#gift-search').fill('Cai');await page.locator('#preference').selectOption('likes');
   assert.equal((await params(page)).get('giftSearch'),'Cai');assert.equal((await params(page)).get('preference'),'likes');
   await page.goBack();await page.waitForSelector('#shops-view:not([hidden])');assert.deepEqual(await snapshot(page),expected);
   await page.goForward();await page.waitForSelector('#gifts-view:not([hidden])');assert.equal(await page.locator('#gift-search').inputValue(),'Cai');assert.equal(await page.locator('#preference').inputValue(),'likes');
   await page.locator('[data-view="overview"]').click();await page.locator('#overview-search').fill('Cai');
   assert.equal((await params(page)).get('overviewSearch'),'Cai');await page.reload();await page.waitForSelector('[data-overview-row]');assert.equal(await page.locator('[data-overview-row]').count(),1);
   await page.locator('[data-overview-character="character-2"]').click();assert.equal((await params(page)).get('giftSearch'),null);assert.equal((await params(page)).get('preference'),null);
   await page.locator('.gift-tag').filter({hasText:'马匹保养工具'}).click();await page.locator('[data-jump-place]').last().click();
   assert.equal((await params(page)).get('shopSearch'),null);assert.equal((await params(page)).get('placeKind'),null);
   const chosen=await page.locator('.place-button.selected').getAttribute('data-place'),shop=await page.locator('.shop-tab.selected').getAttribute('data-shop');
   await page.reload();await page.waitForSelector('.place-button');assert.equal(await page.locator('.place-button.selected').getAttribute('data-place'),chosen);assert.equal(await page.locator('.shop-tab.selected').getAttribute('data-shop'),shop);
   const special='中文 & + / ? # % 日文「魚」';await page.locator('#shop-search').fill(special);assert.equal((await params(page)).get('shopSearch'),special);
   await page.reload();await page.waitForSelector('#shops-view:not([hidden])');assert.equal(await page.locator('#shop-search').inputValue(),special);assert.equal(await page.locator('.place-button').count(),0);
   await page.locator('#shop-search').fill('');assert.equal((await params(page)).get('shopSearch'),null);await page.locator('#place-kind').selectOption('all');assert.equal((await params(page)).get('placeKind'),null);
   await page.goto(base+'?placeKind=invalid&preference=invalid&place=bad&shop=constructor#shops');await page.waitForSelector('.place-button');assert.equal(await page.locator('#place-kind').inputValue(),'all');assert.equal(await page.locator('#preference').inputValue(),'all');assert.equal(await page.locator('.place-button.selected').getAttribute('data-place'),'place-1');
   assert.deepEqual(errors,[]);await page.close();
  }
  console.log('URL state verified on HTTP and file: shared links, reload, all filters, selection, history, cross-view jumps, special characters, clearing and invalid parameters.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
