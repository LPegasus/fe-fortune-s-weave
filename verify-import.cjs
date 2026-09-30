const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
const read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,'data',n+'.json'),'utf8'));
(async()=>{
 const data=read('gifts'),shops=read('shops'),browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],failed=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/data/')&&!r.ok())failed.push(r.url())});
  await page.goto('http://127.0.0.1:4175/#gifts');await page.waitForSelector('.gift-tag');
  const character=data.characters.find(c=>c.loves.some(g=>g.preferenceConflict));
  await page.locator('#gift-search').fill(character.nameEn);await page.locator(`[data-character="${character.id}"]`).click();
  assert(await page.locator('.conflict-badge').count()>0);
  await page.locator('.gift-evidence summary').click();assert((await page.locator('.gift-evidence').innerText()).includes('中文站'));
  await page.locator('.gift-evidence summary').click();await page.screenshot({path:path.join(__dirname,'preview-import-gifts.png')});
  await page.locator('#gift-search').fill('Catania');assert((await page.locator('#character-detail').innerText()).includes('用户确认'));
  await page.locator('[data-view="shops"]').click();await page.locator('#place-kind').selectOption('旅行商人观测地点');
  assert.equal(await page.locator('.place-button').count(),9);assert((await page.locator('#shop-detail').innerText()).includes('截图剩余'));
  await page.locator('.shop-observations summary').first().click();assert((await page.locator('.shop-observations').first().innerText()).includes('第 10 章'));
  await page.locator('#place-kind').selectOption('all');await page.locator('#shop-search').fill('黑翼之谷');
  await page.locator('[data-shop="vandhal"]').click();
  assert((await page.locator('#shop-detail').innerText()).includes('可怜面具'));
  const loc=shops.locations.find(l=>l.nameJa==='黒翼の谷');const masks=loc.shops.find(s=>s.type==='vandhal').items.filter(i=>i.nameJa.includes('仮面'));
  assert.equal(masks.length,3,'Three distinct masks must not be merged');
  await page.locator('#shop-search').fill('帝都达格席翁');await page.locator('[data-shop="vandhal"]').click();
  const box=page.locator('tbody tr').filter({has:page.locator('.name-cell', {hasText:'朴素武具箱'})});
  await box.locator('summary').click();assert((await box.innerText()).includes('中文站记录 · 2'));
  for(const width of [3440,1378,390,320]){await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow ${width}`)}
  await page.screenshot({path:path.join(__dirname,'preview-import-shops-mobile.png')});
  await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href+'#shops');await page.waitForSelector('.place-button');
  assert.equal(await page.locator('.place-button').count(),46);assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
  console.log('Verified source conflicts, user overrides, travel snapshots, separate masks, alternative exchanges, responsive widths, HTTP JSON loading and offline data.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
