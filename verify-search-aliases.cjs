const assert=require('node:assert/strict'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'}),errors=[];
 try{
  for(const base of ['http://127.0.0.1:4175/',pathToFileURL(path.join(__dirname,'index.html')).href]){
   const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base+'#gifts');await page.waitForSelector('.character');
   const giftSearch=page.locator('#gift-search');
   const ids=selector=>page.locator(selector).evaluateAll(es=>es.map(e=>e.dataset.character||e.dataset.overviewRow||e.dataset.place));
   let expected;
   for(const name of ['艾丝梅拉尔达','埃斯梅拉达','エスメラルダ','eSmErAlDa']){
    await giftSearch.fill(name);assert.deepEqual(await ids('.character'),['character-10']);assert.equal(await page.locator('#character-detail h2').innerText(),'艾丝梅拉尔达');
   }
   for(const preference of ['all','loves','likes']){
    await page.locator('#preference').selectOption(preference);
    await giftSearch.fill('巨型鱼的眼珠');expected=await ids('.character');assert(expected.length>0);
    await giftSearch.fill('巨鱼眼球');assert.deepEqual(await ids('.character'),expected);
    await page.reload();await page.waitForSelector('.character');assert.deepEqual(await ids('.character'),expected);assert.equal(await giftSearch.inputValue(),'巨鱼眼球');
    assert.equal(await page.locator('#preference').inputValue(),preference);
   }
   await page.locator('[data-view="overview"]').click();
   await page.locator('#overview-search').fill('马匹保养工具');expected=await ids('[data-overview-row]');assert(expected.length>0);
   await page.locator('#overview-search').fill('马匹护理工具');assert.deepEqual(await ids('[data-overview-row]'),expected);
   await page.locator('[data-view="shops"]').click();
   const search=page.locator('#shop-search');
   for(const [current,alias] of [['莱伊·欧港','莱奥港'],['阿奇纽村','阿吉尼奥村'],['马匹保养工具','马匹护理工具'],['木剑','木制剑']]){
    await search.fill(current);expected=await ids('.place-button');assert(expected.length>0,current);
    await search.fill(alias);assert.deepEqual(await ids('.place-button'),expected,alias);
    if(!['莱伊·欧港','阿奇纽村'].includes(current))assert(await page.locator('#shop-detail tbody tr').count()>0,'Matching product alias must also keep product rows');
   }
   await page.locator('#place-kind').selectOption('地图商会');await search.fill('银吉');
   assert(await page.locator('.place-button').count()>0,'Material alias finds exchanges');
   assert((await page.locator('#shop-detail').innerText()).includes('津吉'));
   await page.locator('#place-kind').selectOption('旅行商人观测地点');
   assert.equal(await page.locator('.place-button').count(),0,'Location type still restricts alias matches');
   await page.locator('#place-kind').selectOption('all');await search.fill('不存在的别名000');assert.equal(await page.locator('.place-button').count(),0);
   await page.close();
  }
  assert.deepEqual(errors,[]);console.log('Alias search verified on HTTP and file: renamed character and gift, Japanese/English, preference filters, overview, location/product/material aliases, matching shop rows, URL reload and empty results.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
