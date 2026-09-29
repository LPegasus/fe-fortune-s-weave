from research import *
from urllib.parse import urljoin
base='https://game8.jp'
catalog={}
for key,url in [('weapons','https://game8.jp/fe-banshisenko/817514'),('equipment','https://game8.jp/fe-banshisenko/817533'),('items','https://game8.jp/fe-banshisenko/816980')]:
    s=get('game8_'+key,url)
    for a in s.select('a[href]'):
        if '/fe-banshisenko/' in a['href']: catalog[a.get_text(strip=True)]=urljoin(base,a['href'])
shops=json.loads((ROOT/'data/shops.json').read_text(encoding='utf-8'))
needed={i['nameJa'] for l in shops['locations'] for s in l['shops'] for i in s['items'] if i['stockStatus']=='unknown'}
links={n:u for n,u in catalog.items() if n in needed}
(CACHE/'item_links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
print('ITEM links',len(links),'missing',needed-links.keys(),flush=True)
def download(pair):
    n,u=pair
    try:
        get('item_'+u.split('/')[-1],u)
        return n
    except Exception as e: print(n,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(download,links.items()))
print('item collection done',flush=True)
