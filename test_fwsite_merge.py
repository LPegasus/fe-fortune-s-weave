import copy
import json
import unittest
from pathlib import Path
from merge_fwsite import merge_gifts,merge_shops,identity

ROOT=Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf8'))

class MergeTests(unittest.TestCase):
    def setUp(self):
        self.gifts=read('gifts.json');self.shops=read('shops.json');self.sources=read('sources.json')

    def test_all_source_preferences_preserved_and_user_corrections_win(self):
        chars={c['id']:c for c in self.gifts['characters']}
        corrections={(c['characterId'],identity({'name':c.get('itemName'),'nameJa':c.get('itemNameJa')})):c for c in read('gift-corrections.json')}
        for row in read('imports/fwsite-gifts.json')['characters']:
            c=chars[row['characterId']]
            for pref in ['loves','likes']:
                for incoming in row[pref]:
                    jp=identity(incoming);override=corrections.get((c['id'],jp));target=override['to'] if override else pref
                    match=next(i for i in c[target] if identity(i)==jp)
                    self.assertTrue(any(o['rawName']==incoming['rawName'] and o['preference']==pref for o in match['sourceObservations']))
        for (cid,jp),correction in corrections.items():
            self.assertTrue(any(identity(i)==jp for i in chars[cid][correction['to']]))
            self.assertFalse(any(identity(i)==jp for i in chars[cid]['likes' if correction['to']=='loves' else 'loves']))

    def test_all_exchange_alternatives_and_snapshot_quantities_preserved(self):
        for row in read('imports/fwsite-shops.json')['locations']:
            loc=next(l for l in self.shops['locations'] if l['id']==row['locationId'])
            shop=next(s for s in loc['shops'] if s['type']==row['type'])
            for incoming in row['items']:
                match=next(i for i in shop['items'] if identity(i)==identity(incoming))
                self.assertTrue(any(o['stock']==incoming['stock'] and o['exchange']==incoming['exchange'] and o['price']==incoming['price'] for o in match['sourceObservations']))

    def test_reimport_is_idempotent(self):
        before=copy.deepcopy((self.gifts,self.shops,self.sources))
        merge_gifts(self.gifts,self.sources);merge_shops(self.shops,self.sources)
        self.assertEqual((self.gifts,self.shops,self.sources),before)

    def test_similar_materials_and_masks_have_distinct_identities(self):
        mapping=read('fwsite-mapping.json')['shopItems']
        for raw,jp in [('迷人面具','可憐の仮面'),('魅惑面具','魅了の仮面'),('疯狂面具','酔狂の仮面'),('尼内亚卡','ニネイアッカ'),('赤金拜','アカキンバイ')]:
            self.assertEqual(mapping[raw]['nameJa'],jp)

    def test_baseline_preserved_when_local_research_backup_available(self):
        path=ROOT/'.research/pre-fw-gifts.json'
        if not path.exists():self.skipTest('Local baseline not available')
        old=json.loads(path.read_text(encoding='utf8'))
        for c in old['characters']:
            new=next(n for n in self.gifts['characters'] if n['id']==c['id'])
            for pref in ['loves','likes']:
                for i in c[pref]:self.assertTrue(any(identity(i)==identity(n) for n in new[pref]),(c['name'],pref,i['name']))
        old=json.loads((ROOT/'.research/pre-fw-shops.json').read_text(encoding='utf8'))
        for loc in old['locations']:
            newloc=next(n for n in self.shops['locations'] if n['id']==loc['id'])
            for shop in loc['shops']:
                newshop=next(n for n in newloc['shops'] if n['type']==shop['type'])
                for i in shop['items']:
                    n=next(n for n in newshop['items'] if identity(i)==identity(n))
                    self.assertEqual((i['stock'],i['stockStatus']),(n['stock'],n['stockStatus']))
                    if i['exchange']:self.assertEqual([(identity(m),m['quantity']) for m in i['exchange']],[(identity(m),m['quantity']) for m in n['exchange']])

if __name__=='__main__':unittest.main()
