import sys, pathlib, json, re, concurrent.futures
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / '.tools'))
import requests
from bs4 import BeautifulSoup
CACHE = ROOT / '.research'
CACHE.mkdir(exist_ok=True)
def get(key,url):
    p=CACHE/(key+'.html')
    if not p.exists():

        error=None
        for attempt in range(3):
            try:
                r=requests.get(url,timeout=25); r.raise_for_status(); error=None; break
            except requests.RequestException as e: error=e
        if error: raise error
        r.encoding=r.apparent_encoding
        p.write_text(r.text,encoding='utf-8')
    return BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
urls={
 'game8':'https://game8.jp/fe-banshisenko/818736',
 'gamewith':'https://gamewith.jp/fefw/577115',
 'cn':'https://www.gamersky.com/handbook/202609/2217606.shtml',
 'gamecap':'https://gamecap.jp/fe_fw/shop.html',
 'en':'https://www.keengamer.com/articles/guides/fire-emblem-fortunes-weave-best-gifts-guide/',
 'vandhal':'https://raiderking.com/fe-fortunes-weave-vandhal-trading-co-all-trader-locations-items-exchange-and-resources/'
}
def fetch(pair):
    k,u=pair
    try:
        s=get(k,u)
        (CACHE/(k+'.txt')).write_text(s.get_text('\n',strip=True),encoding='utf-8')
        print(k,len(str(s)), 'tables',len(s.find_all('table')),flush=True)
    except Exception as e: print(k,str(e),flush=True)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch,urls.items()))
