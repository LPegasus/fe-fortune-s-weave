from research import *
import struct
assets=ROOT/'assets'/'portraits';assets.mkdir(parents=True,exist_ok=True)
page=get('gamewith',urls['gamewith'])
lookup={}
for box in page.select('._item'):
    head=box.select_one('._head');img=box.select_one('img[data-original]')
    if head and img: lookup[head.get_text(strip=True)]={'url':img['data-original'],'page':urls['gamewith']}
listurl='https://gamewith.jp/fefw/573109'
page=get('portraits_characters',listurl)
for img in page.select('img[data-original]'):
    name=img.get('alt','')
    if name=='救世主':lookup[name]={'url':img['data-original'],'page':listurl}
gifts=json.loads((ROOT/'data/gifts.json').read_text(encoding='utf-8-sig'))
def download(c):
    info=lookup[c['nameJa']]
    dest=assets/(c['id']+'.png')
    if not dest.exists():
        for attempt in range(3):
            try:
                r=requests.get(info['url'],timeout=25);r.raise_for_status()
                if not r.content.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Not PNG '+info['url'])
                dest.write_bytes(r.content);break
            except Exception:
                if attempt==2:raise
    w,h=struct.unpack('>II',dest.read_bytes()[16:24])
    return c['id'],{'src':'assets/portraits/'+dest.name,'alt':c['name']+'的人物头像','sourceUrl':info['url'],'sourcePage':info['page'],'width':w,'height':h,'rights':'Nintendo / INTELLIGENT SYSTEMS; image hosted by GameWith'}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    portraits=dict(pool.map(download,gifts['characters']))
(ROOT/'data/portraits.json').write_text(json.dumps(portraits,ensure_ascii=False,indent=2),encoding='utf-8')
for c in gifts['characters']:c['portrait']=portraits[c['id']]
(ROOT/'data/gifts.json').write_text(json.dumps(gifts,ensure_ascii=False,indent=2),encoding='utf-8')
sourcepath=ROOT/'data/sources.json';sources=json.loads(sourcepath.read_text(encoding='utf-8-sig'))
if not any(s['id']=='gamewith-portraits' for s in sources):sources.append({'id':'gamewith-portraits','language':'ja','title':'GameWith · 人物头像图鉴','url':listurl,'note':'头像按日文姓名逐一匹配，使用原始游戏角色图；图片归 Nintendo / INTELLIGENT SYSTEMS 所有，本地缓存供页面离线显示。','accessed':'2026-09-30'})
sourcepath.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved',len(portraits),'portraits; sizes:',sorted(set((p['width'],p['height']) for p in portraits.values())))
