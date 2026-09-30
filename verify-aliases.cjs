const assert=require('node:assert/strict'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const errors=[];
 try{
  for(const base of ['http://127.0.0.1:4175/',pathToFileURL(path.join(__dirname,'index.html')).href]){
   const page=await browser.newPage({viewport:{width:1378,height:1000}});page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base+'?shopSearch=莱伊·欧港#shops');
   const place=page.locator('#shop-detail h2 .alias-trigger'),popover=page.locator('#alias-popover');
   await place.hover();await popover.waitFor({state:'visible'});assert((await popover.innerText()).includes('莱奥港'));
   assert.equal(await popover.locator('li').count(),new Set(JSON.parse(await place.getAttribute('data-aliases'))).size);
   await popover.hover();await page.waitForTimeout(200);assert(await popover.isVisible(),'Popover remains open when hovered');
   await page.keyboard.press('Escape');assert(await popover.isHidden());
   await place.focus();assert(await popover.isVisible(),'Keyboard focus shows aliases');assert.equal(await place.getAttribute('aria-describedby'),'alias-popover');
   await page.keyboard.press('Escape');assert.equal(await place.getAttribute('aria-describedby'),null);
   await page.locator('#shop-search').fill('混合药');
   const medicine=page.locator('.name-cell .alias-trigger').filter({hasText:'混合药'}).first();
   await medicine.hover();assert((await popover.innerText()).includes('调合药'));
   await page.locator('#shop-search').fill('帝都达格席翁');await page.locator('[data-shop="vandhal"]').click();
   const material=page.locator('.material [data-alias-name="津吉"]').first();await material.hover();assert((await popover.innerText()).includes('银吉'));
   await page.locator('[data-view="gifts"]').click();await page.locator('#gift-search').fill('Cai');
   const gift=page.locator('.gift-tag .alias-trigger').filter({hasText:'马匹保养工具'});
   await gift.hover();assert((await popover.innerText()).includes('马匹护理工具'));
   await gift.click();await page.waitForSelector('[data-jump-place]');assert(await popover.isHidden(),'Existing gift click still opens purchase locations');
   await page.locator('#gift-search').fill('Ursula');const person=page.locator('#character-detail h2 .alias-trigger');await person.hover();assert((await popover.innerText()).includes('厄休拉'));
   await page.locator('[data-view="overview"]').click();await page.locator('#overview-search').fill('香醇的苍烧');
   const overview=page.locator('.overview-gifts .alias-trigger').filter({hasText:'香醇的苍烧'}).first();await overview.hover();
   const aliases=JSON.parse(await overview.getAttribute('data-aliases'));assert(aliases.length>1);assert.deepEqual(await popover.locator('li').allTextContents(),aliases);
   assert(await popover.evaluate(e=>e.parentElement===document.body));await page.screenshot({path:path.join(__dirname,'preview-aliases.png')});
   await page.locator('#overview-search').fill('不存在000');assert(await popover.isHidden(),'Rendering dismisses stale popover');
   await page.close();
  }
  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});mobile.on('pageerror',e=>errors.push(e.message));
  await mobile.goto(pathToFileURL(path.join(__dirname,'index.html')).href+'?giftSearch=Cai#gifts');
  const gift=mobile.locator('.gift-tag .alias-trigger').filter({hasText:'马匹保养工具'}),popover=mobile.locator('#alias-popover');
  await gift.tap();assert(await popover.isVisible(),'First touch displays aliases');assert.equal(await mobile.locator('[data-jump-place]').count(),0);
  const rect=await popover.boundingBox();assert(rect.x>=0&&rect.x+rect.width<=390&&rect.y>=0&&rect.y+rect.height<=844,'Popover fits mobile viewport');
  await mobile.screenshot({path:path.join(__dirname,'preview-aliases-mobile.png')});
  await gift.tap();await mobile.waitForSelector('[data-jump-place]');assert(await popover.isHidden(),'Second touch follows existing gift action');
  await mobile.close();assert.deepEqual(errors,[]);
  console.log('Alias popovers verified: character, location, item, gift and overview; complete deduplicated aliases; hover persistence, Escape, keyboard, mobile touch, viewport bounds, normal actions and offline loading.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
