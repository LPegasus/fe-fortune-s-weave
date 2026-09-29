from research import *
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
sources=[]
def source(id,lang,title,url,note=''):
    if not any(s['id']==id for s in sources): sources.append(dict(id=id,language=lang,title=title,url=url,note=note,accessed='2026-09-29'))
source('gamewith','ja','GameWith · 人物送礼偏好',urls['gamewith'],'展开网页内的礼物分类提示，逐项提取；未把整个类别扩展为所有同类物品。')
source('game8','ja','Game8 · 据点与商店目录',urls['game8'],'用于补全未在 AppMedia 收录的商品；此总表不含库存数，缺少值保留 null。')
source('gamecap','ja','Gamecap · 商店资料',urls['gamecap'],'对照商品与价格，不把价格误记为库存。')
source('raiderking','en','Raider King · 旺达尔商会兑换',urls['vandhal'],'英文兑换清单；原站标注仍在更新。材料个数不等于商品库存。')
source('keengamer','en','KeenGamer · 送礼推荐',urls['en'],'通过搜索与网页阅读检索；推荐类别不直接列为已确认偏好。')
cn=json.loads((CACHE/'cn_pages.json').read_text(encoding='utf-8'))
translations={}
chars=[]
for c in cn:
    source('cn-'+str(c['page']),'zh','游民星空 · '+c['text'].splitlines()[0].split('：')[-1].replace('厄休拉','乌修拉').replace('西蒙','希蒙').replace('奈丁','努蒂奴').replace('洛蕾塔','罗蕾塔').replace('妮娜','妮涅'),c['url'],'中文译名及偏好对照。该文引用 GameWith，不计为独立实测。')
    lines=c['text'].splitlines()
    head=next(x for x in lines if '·' in x)
    left,jp=[x.strip() for x in head.split('·',1)]
    match=re.match(r'(.+?)\s+([A-Za-z].*)',left)
    zh,en=match.groups()
    # Character name corrected by the user.
    zh={'厄休拉':'乌修拉','西蒙':'希蒙','奈丁':'努蒂奴','洛蕾塔':'罗蕾塔','妮娜':'妮涅'}.get(zh,zh)
    for a,b in re.findall(r'([^（）、：\n]+)（([^（）]+)）',c['text']):
        a=re.sub(r'^(非常喜欢|喜欢|训练装备|英文攻略补充)\s*','',a).strip()
        if re.search(r'[ぁ-ヿ]',b) or b in ['天露水','南洋冒険奇譚']:
            translations[b]=a
    chars.append(dict(id='character-'+str(c['page']),name=zh,nameJa=jp,nameEn=en,loves=[],likes=[],sourceIds=['cn-'+str(c['page'])],status='unknown'))
byja={c['nameJa']:c for c in chars}
g=get('gamewith',urls['gamewith'])
for box in g.select('._item'):
    h=box.select_one('._head')
    if not h: continue
    jp=h.get_text(strip=True)
    if jp not in byja:
        print('UNMATCHED CHARACTER',jp); continue
    c=byja[jp]; c['sourceIds'].insert(0,'gamewith')
    for section in box.select('._section'):
        label=section.find('div').get_text(strip=True)
        if label not in ['大好き','好き']: continue
        key='loves' if label=='大好き' else 'likes'
        body=section.find_all('div',recursive=False)[1]
        for card in body.select('card[data-txt]'):
            card.replace_with(BeautifulSoup(card['data-txt'],'html.parser'))
        for br in body.find_all('br'): br.replace_with('\n')
        values=[x.strip() for x in body.get_text('',strip=False).split('\n')]
        values=[re.sub(r'^.+?系\((.+?)(?:など)?\)$',r'\1',x).removesuffix('など') for x in values]
        for v in values:
            if v in ['調査中','なし','-',''] or v in c[key]: continue
            c[key].append(v)
    c['status']='documented' if c['loves'] or c['likes'] else 'unknown'
    c['notes']=[]
    # Categories without tooltip lists remain explicitly marked as categories.
    for key in ['loves','likes']:
        c[key]=[dict(nameJa=v,name=translations.get(v,v),kind='category' if '系(' in v else 'item',sourceIds=['gamewith']) for v in c[key]]
    old=next(x for x in cn if 'cn-'+str(x['page']) in c['sourceIds'])
    olditems=set(re.findall(r'（([^（）]+)）',old['text'].split('英文攻略补充')[0]))
    newitems={v['nameJa'] for k in ['loves','likes'] for v in c[k]}
    c['sourceDifference']=sorted(olditems-newitems-{c['nameJa'],'伊修玛尔','奥谢尔','爱娜特莉亚','诺克裘拉'})
    if '调查中' in old['text'] and newitems: c['notes'].append('日文站已有明确礼物记录；中文旧版仍为调查中。')
    if c['sourceDifference']: c['notes'].append('中日清单存在差异；当前偏好采用采集到的 GameWith 列表，中文独有项保存在 JSON 供核对。')

shop_types={'道具屋':'items','武器屋':'weapons','武具屋':'weapons','市場':'market','ヴァンダル商会':'vandhal','贈り物屋':'gifts'}
locations=[]
game8=get('game8',urls['game8'])
for row in game8.find_all('table')[1].select('tr')[1:]:
    cells=row.find_all('td',recursive=False)
    if len(cells)!=2: continue
    name=cells[0].get_text(strip=True)
    if any(x['nameJa']==name for x in locations): continue
    loc=dict(id='place-'+str(len(locations)+1),nameJa=name,name=name,type='据点 / 准据点',shops=[],sourceIds=['game8'])
    for span in cells[1].select('span.js-detail-tooltip'):
        template=span.find('template')
        if not template: continue
        label=span.contents[0].strip()
        typ=shop_types[label]
        items=[]
        for raw in template.get_text('\n',strip=True).splitlines():
            raw=raw.lstrip('・').strip()
            if not raw: continue
            m=re.match(r'(.+?)\(価格[：:](\d+)\)',raw)
            jp,price=(m[1],int(m[2])) if m else (raw,None)
            items.append(dict(nameJa=jp,name=translations.get(jp,jp),stock=None,stockStatus='unknown',price=price,exchange=[],sourceIds=['game8'],phase=None))
        loc['shops'].append(dict(type=typ,items=items,status='documented'))
    locations.append(loc)

links=json.loads((CACHE/'app_links.json').read_text(encoding='utf-8'))
markers=json.loads((CACHE/'map_markers.json').read_text(encoding='utf-8'))
for name,u in links.items():
    p=CACHE/('app_'+u.split('/')[-1]+'.html')
    if not p.exists(): continue
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    sid='app-'+u.split('/')[-1]
    source(sid,'ja','AppMedia · '+name,u,'库存与价格来自同一张表；来源未逐项注明章节，不能视作所有路线、所有章节均相同。')
    loc=next((x for x in locations if x['nameJa']==name),None)
    if not loc:
        loc=dict(id='place-'+str(len(locations)+1),nameJa=name,name=name,type='地图商会',shops=[],sourceIds=[])
        locations.append(loc)
    icon=markers.get(name,{}).get('icon')
    if icon in ['i11','i12']: loc['type']='据点' if icon=='i11' else '准据点'
    loc['sourceIds'].append(sid)
    for table in s.find_all('table'):
        rows=table.find_all('tr')
        if not rows: continue
        header=rows[0].get_text(' ',strip=True)
        if '在庫' not in header: continue
        heading=table.find_previous(['h2','h3','h4']).get_text(strip=True)
        if heading not in shop_types: print('UNKNOWN SHOP',name,heading); continue
        typ=shop_types[heading]; items=[]
        if name=='カリアネイラの港' and '太陽のゴーシュ' in table.get_text(): typ='market'
        for row in rows[1:]:
            cells=row.find_all(['td','th'],recursive=False)
            if len(cells)<3: continue
            jp=cells[0].get_text(strip=True)
            q=cells[1].get_text(strip=True)
            stock=int(q) if q.isdigit() else None
            status='unlimited' if q in ['∞','無限'] else 'known' if stock is not None else 'unknown'
            cost=cells[2].get_text('\n',strip=True)
            price=int(cost.replace(',','')) if '価格' in header and cost.replace(',','').isdigit() else None
            exchange=[]
            if '必要素材' in header:
                for material,amount in re.findall(r'([^×\n]+)×\s*(\d+)',cost):
                    exchange.append(dict(nameJa=material.strip(),quantity=int(amount)))
            items.append(dict(nameJa=jp,name=translations.get(jp,jp),stock=stock,stockStatus=status,price=price,exchange=exchange,sourceIds=[sid],phase=None))
        previous=next((x for x in loc['shops'] if x['type']==typ),None)
        if previous:
            prev={i['nameJa']:i for i in previous['items']}
            for it in items:
                old=prev.pop(it['nameJa'],None)
                if old:
                    if old['price']!=it['price'] and old['price'] is not None:
                        it['alternativePrices']=[dict(price=old['price'],sourceIds=old['sourceIds'],note='来源不同，折扣或阶段未说明')]
                    it['sourceIds']+=old['sourceIds']
                    if it['price'] is None and old['price'] is not None:
                        it['price']=old['price']; it['priceSourceId']='game8'
                    if it.get('stockStatus')!='unknown': it['quantitySourceId']=sid
            # preserve only real missing items, excluding spelling variants
            aliases={'関節保護用長手袋':'間接保護用長手袋','栄養満点お菓子本':'栄養満点のお菓子本','バシテア地図':'パシテア地図','パスク地図':'バスク地図','ブラクシテア地図':'プラクシテア地図','ランバス地図':'ランパス地図','身蹱しの籠手':'身躱しの籠手'}
            for jp,item in prev.items():
                if not any(aliases.get(jp,jp)==i['nameJa'] for i in items): items.append(item)
            previous['items']=items
        else: loc['shops'].append(dict(type=typ,items=items,status='documented'))


# AppMedia labels the port market table as a second item shop. Game8 and
# Gamecap agree these gift products belong to the market; preserve that correction.
port=next(l for l in locations if l['nameJa']=='カリアネイラの港')
port['notes']=['AppMedia 专页把市场表格标题重复写成道具店；按 Game8 与 Gamecap 的一致归属，将这组礼物记在市场。该表库存为空，仍保留待确认。']
locations[0]['type']='据点'

# Fill missing quantities from individual Game8 item pages; each observation
# retains its own source. Never infer inventory from price or exchange materials.
if (CACHE/'item_links.json').exists():
    for itemName,u in json.loads((CACHE/'item_links.json').read_text(encoding='utf-8')).items():
        p=CACHE/('item_'+u.split('/')[-1]+'.html')
        if not p.exists(): continue
        s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
        sid='game8-item-'+u.split('/')[-1]
        for table in s.find_all('table'):
            if '在庫' not in table.get_text(): continue
            for row in table.find_all('tr')[1:]:
                cells=row.find_all('td',recursive=False)
                if len(cells)!=2: continue
                text=cells[1].get_text(' ',strip=True)
                q=re.search(r'在庫[：:]\s*(∞|[0-9]+)',text)
                if not q: continue
                name=cells[0].get_text(' ',strip=True).replace('拡大','').strip()
                loc=next((l for l in locations if l['nameJa']==name),None)
                if not loc: continue
                label=cells[1].select_one('.a-label-tag')
                if not label: continue
                typ=shop_types.get(label.get_text(strip=True))
                shop=next((a for a in loc['shops'] if a['type']==typ),None)
                if not shop: continue
                item=next((i for i in shop['items'] if i['nameJa']==itemName),None)
                if not item: continue
                source(sid,'ja','Game8 · '+itemName,u,'单品入手页面，补全已有商品的库存；保留与主表不同的观察。')
                status='unlimited' if q[1]=='∞' else 'known'
                stock=None if q[1]=='∞' else int(q[1])
                if item['stockStatus']=='unknown':
                    item.update(stock=stock,stockStatus=status)
                    item['sourceIds'].append(sid)
                    item['quantitySourceId']=sid
                    if '交換素材' in text:
                        cost=text.split('交換素材',1)[1]
                        item['exchange']=[dict(nameJa=a.strip(),quantity=int(b)) for a,b in re.findall(r'(\S+)\s*×\s*(\d+)',cost)]
                elif item['stockStatus']!=status or item['stock']!=stock:
                    item.setdefault('alternativeStocks',[]).append(dict(stock=stock,stockStatus=status,sourceIds=[sid]))

# Independent English records are kept as separate observations to avoid merging
# incompatible exchange costs from different source snapshots.
english=[]
en=get('vandhal',urls['vandhal'])
for h in en.select('h3'):
    t=h.find_next_sibling('figure') or h.find_next_sibling('table')
    if t and t.name!='table': t=t.find('table')
    if not t: continue
    entries=[]
    for r in t.select('tr')[1:]:
        cells=r.find_all('td')
        if len(cells)<2: continue
        entries.append(dict(nameEn=cells[0].get_text(strip=True),exchangeEn=cells[1].get_text('; ',strip=True),stock=None,stockStatus='unknown'))
    if entries: english.append(dict(locationEn=h.get_text(strip=True),items=entries,sourceIds=['raiderking']))

if (ROOT/'translations.json').exists():
    manual=json.loads((ROOT/'translations.json').read_text(encoding='utf-8-sig'))
else: manual={'items':{},'locations':{}}
translations.update(manual['items'])
translations.update({'必聖の宝珠':'必圣宝珠','精霊の宝珠':'精灵宝珠','絶風の宝珠':'绝风宝珠','高級野菜箱':'高级蔬菜箱'})
for c in chars:
    for key in ['loves','likes']:
        for i in c[key]: i['name']=translations.get(i['nameJa'],i['nameJa'])
for loc in locations:
    loc['name']=manual['locations'].get(loc['nameJa'],loc['nameJa'])
    for shop in loc['shops']:
        for i in shop['items']:
            i['name']=translations.get(i['nameJa'],i['nameJa'])
            for material in i['exchange']: material['name']=translations.get(material['nameJa'],material['nameJa'])
    for typ in ['items','weapons','market','vandhal']:
        if not any(x['type']==typ for x in loc['shops']): loc['shops'].append(dict(type=typ,status='not_listed',items=[]))

meta=dict(coverage='公开来源已收录记录；并非所有章节及全部隐藏货品的穷尽清单',schemaVersion=1,updated='2026-09-29',game='Fire Emblem 万紫千红 / 万缕千丝',notes=['本站整理公开攻略，不代表游戏内逐项实测。','库存为来源记录快照；未注明具体路线、章节、名声和折扣的条目不作统一假设。','stockStatus=unlimited 表示来源明确记载无限；unknown 表示缺少资料，不是售罄。','未收录店铺表示参考资料没有列出，不能断言游戏中不存在。'])
# Keep local character portraits when rebuilding the researched gift data.
portrait_file=DATA/'portraits.json'
if portrait_file.exists():
    portraits=json.loads(portrait_file.read_text(encoding='utf-8-sig'))
    for character in chars:
        if character['id'] in portraits: character['portrait']=portraits[character['id']]
    source('gamewith-portraits','ja','GameWith · 人物头像图鉴','https://gamewith.jp/fefw/573109','人物头像按姓名匹配并本地缓存；图片归 Nintendo / INTELLIGENT SYSTEMS 所有。')

# Apply user-tested corrections after importing public sources.
correction_file=DATA/'gift-corrections.json'
if correction_file.exists():
    for correction in json.loads(correction_file.read_text(encoding='utf-8-sig')):
        character=next(c for c in chars if c['id']==correction['characterId'])
        matches=[i for key in ['loves','likes'] for i in character[key] if i['nameJa']==correction['itemNameJa']]
        if not matches: raise ValueError('Correction gift missing: '+correction['itemNameJa'])
        item=matches[0]
        item['preferenceCorrection']=correction.copy()
        for key in ['loves','likes']:
            character[key]=[i for i in character[key] if i['nameJa']!=correction['itemNameJa']]
        character[correction['to']].append(item)
        if correction['note'] not in character.setdefault('notes',[]): character['notes'].append(correction['note'])

gifts={**meta,'characters':chars}
shops={**meta,'locations':locations,'englishExchangeObservations':english}
for filename,value in [('gifts.json',gifts),('shops.json',shops),('sources.json',sources)]:
    (DATA/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
payload=dict(gifts=gifts,shops=shops,sources=sources)
(ROOT/'data.js').write_text('window.GUIDE_DATA = '+json.dumps(payload,ensure_ascii=False)+';\n',encoding='utf-8')
untranslated=sorted({i['nameJa'] for loc in locations for s in loc['shops'] for i in s['items'] if i['name']==i['nameJa']}|{i['nameJa'] for c in chars for key in ['loves','likes'] for i in c[key] if i['name']==i['nameJa']})
(CACHE/'untranslated.json').write_text(json.dumps(untranslated,ensure_ascii=False,indent=2),encoding='utf-8')
print('Characters',len(chars),'documented',sum(c['status']=='documented' for c in chars),'locations',len(locations),'items',sum(len(s['items']) for l in locations for s in l['shops']),'EN tables',len(english),'untranslated',len(untranslated))
