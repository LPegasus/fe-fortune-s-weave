import copy
import json
import unittest
from pathlib import Path
from gift_rules import enforce_gift_precedence,item_identity

class GiftRulesTests(unittest.TestCase):
    def test_alias_overlap_preserves_like_evidence_without_relabelling_sources(self):
        love={'name':'马匹保养工具','nameJa':'馬のお手入れ道具','sourceIds':['love-source']}
        like={'name':'马匹护理工具','sourceIds':['like-source'],'sourceObservations':[{'sourceId':'like-source','preference':'likes','rawName':'马匹护理工具','sourceUrl':'https://example.com/likes'}]}
        distinct={'name':'马鬃饰品','nameJa':'鬣飾り','sourceIds':['other-source']}
        gifts={'characters':[{'id':'one','loves':[love],'likes':[like,distinct]},{'id':'two','loves':[],'likes':[copy.deepcopy(like)]}]}
        self.assertEqual(enforce_gift_precedence(gifts),1)
        self.assertEqual(gifts['characters'][0]['likes'],[distinct])
        self.assertEqual(gifts['characters'][1]['likes'],[like],'Other characters are independent')
        self.assertEqual(love['sourceIds'],['love-source'])
        self.assertEqual(love['sourceObservations'],like['sourceObservations'])
        self.assertEqual(love['preferenceResolution']['removedLikeSourceIds'],['like-source'])
        before=copy.deepcopy(gifts);self.assertEqual(enforce_gift_precedence(gifts),0);self.assertEqual(gifts,before)

    def test_different_japanese_spelling_alias_is_the_same_gift(self):
        gifts={'characters':[{'loves':[{'name':'马鬃饰品','nameJa':'鬣飾り','sourceIds':[]}],'likes':[{'name':'别站译名','nameJa':'髭飾り','sourceIds':['old'] }]}]}
        self.assertEqual(enforce_gift_precedence(gifts),1)
        self.assertEqual(gifts['characters'][0]['likes'],[])
        self.assertEqual(gifts['characters'][0]['loves'][0]['sourceObservations'][0]['preference'],'likes')

    def test_current_data_and_bundle_never_overlap(self):
        root=Path(__file__).resolve().parent
        data=json.loads((root/'data/gifts.json').read_text(encoding='utf8'))
        bundle=(root/'data.js').read_text(encoding='utf8').removeprefix('window.GUIDE_DATA = ').strip().removesuffix(';')
        self.assertEqual(json.loads(bundle)['gifts'],data)
        for c in data['characters']:
            self.assertFalse({item_identity(i) for i in c['loves']}&{item_identity(i) for i in c['likes']},c['name'])
            self.assertFalse(any('按并集保留在两栏' in n for n in c['notes']))

if __name__=='__main__':unittest.main()
