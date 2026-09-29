from research import *
s=get('app_world','https://appmedia.jp/fe_banshisenkou/80369863')
markers={}
for script in s.select('script'):
    for m in re.finditer(r'var markers\s*=\s*',script.get_text()):
        data,_=json.JSONDecoder().raw_decode(script.get_text()[m.end():])
        for icon,rows in data.items():
            for row in rows:
                a=BeautifulSoup(row['content'],'html.parser').find('a')
                if a:
                    markers[row['label']]={'url':a['href'],'icon':icon}
(CACHE/'map_markers.json').write_text(json.dumps(markers,ensure_ascii=False,indent=2),encoding='utf-8')
g=get('game8',urls['game8'])
places={row.find('td').get_text(strip=True) for row in g.find_all('table')[1].select('tr')[1:]}
extra=['ゴーラ草原帯','サンタナ大橋','黒翼の谷','フィーナの岩礁','ペルーザ岬','ゼート湖','笑う石']
links={n:v['url'] for n,v in markers.items() if v['icon'] in ['i11','i12'] or n in places or n in extra}
(CACHE/'app_links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
print('maps',len(links),'missing',places-links.keys(),flush=True)
def fetchmap(pair):
    n,u=pair
    try:
        s=get('app_'+u.rstrip('/').split('/')[-1],u)
        print(n,len([t for t in s.find_all('table') if '在庫' in t.get_text()]),flush=True)
    except Exception as e: print(n,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(fetchmap,links.items()))
