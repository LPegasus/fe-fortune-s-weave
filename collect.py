from research import *
cn=get('cn',urls['cn'])
pages={1:urls['cn']}
for a in cn.select('a[href]'):
    m=re.match(r'第(\d+)页：',a.get_text(strip=True))
    if m: pages[int(m[1])]=a['href']
def load_cn(pair):
    i,u=pair
    s=get('cn'+str(i),u)
    article=s.select_one('.Mid2L_con')
    text=article.get_text('\n',strip=True).split('更多相关内容')[0]
    (CACHE/('cn'+str(i)+'.txt')).write_text(text,encoding='utf-8')
    return {'page':i,'url':u,'text':text}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    chars=list(pool.map(load_cn,pages.items()))
(CACHE/'cn_pages.json').write_text(json.dumps(chars,ensure_ascii=False,indent=2),encoding='utf-8')
print('CN pages',len(chars),flush=True)
s=get('app_world','https://appmedia.jp/fe_banshisenkou/80369863')
places=set()
g=get('game8',urls['game8'])
for row in g.find_all('table')[1].select('tr')[1:]:
    places.add(row.find('td').get_text(strip=True))
links={}
for a in s.select('a[href]'):
    name=a.get_text(strip=True)
    if any(p in name for p in places): links[name]=a['href']
(CACHE/'app_links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
print('APP links',links,flush=True)
def app(pair):
    name,u=pair
    key='app_'+u.rstrip('/').split('/')[-1]
    s=get(key,u)
    (CACHE/(key+'.txt')).write_text(s.get_text('\n',strip=True),encoding='utf-8')
    print(name, len([t for t in s.find_all('table') if '在庫' in t.get_text()]),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    list(pool.map(app,links.items()))
