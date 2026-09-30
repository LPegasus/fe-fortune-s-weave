import copy
import json
import unittest
from pathlib import Path

from normalize_names import ALIASES, normalize_name, normalize_payloads

ROOT = Path(__file__).resolve().parent


class NameAliasesTests(unittest.TestCase):
    def test_all_original_names_and_old_aliases(self):
        for scope in ('characters', 'items', 'locations'):
            for entry in ALIASES[scope]:
                for name in [entry['canonicalName'], entry.get('nameJa'), entry.get('nameEn'), *entry['aliases']]:
                    if name:
                        with self.subTest(scope=scope, name=name):
                            self.assertEqual(normalize_name(scope, name), entry['canonicalName'])

    def test_priority_scope_and_general_rules(self):
        self.assertEqual(normalize_name('items', '旧站未知译名', '芳醇なソウシュ'), '香醇的苍烧')
        self.assertEqual(normalize_name('items', '醇香苏修发酵酒'), '香醇的苍烧')
        self.assertEqual(normalize_name('items', '新配方戈修发酵酒'), '新配方赤烧')
        self.assertEqual(normalize_name('items', '特芙咖啡烤点心'), '特芙烤点心')
        self.assertEqual(normalize_name('characters', '但丁'), '丹提')
        self.assertEqual(normalize_name('items', '但丁戏剧全集'), '但丁戏剧全集')
        self.assertEqual(normalize_name('items', '未收录物品'), '未收录物品')
        self.assertIsNone(normalize_name('items', None))

    def test_current_data_is_preserved_and_imported_names_are_restored(self):
        files = {'gifts': 'gifts', 'shops': 'shops', 'sources': 'sources',
                 'portraits': 'portraits', 'corrections': 'gift-corrections'}
        expected = {key: json.loads((ROOT / 'data' / (name + '.json')).read_text(encoding='utf-8'))
                    for key, name in files.items()}
        payloads = copy.deepcopy(expected)
        normalize_payloads(**payloads)
        self.assertEqual(payloads, expected, 'Existing preferences, provenance and stocks must remain unchanged')
        # Simulate source data returning original Chinese names, with Japanese IDs intact.
        for character in payloads['gifts']['characters']:
            entry = next((e for e in ALIASES['characters'] if e['id'] == character['id']), None)
            if entry:
                character['name'] = (entry['aliases'] or [entry['nameJa']])[0]
                character['portrait']['alt'] = (entry['aliases'] or [entry['nameJa']])[0] + '的人物头像'
            for item in character['loves'] + character['likes']:
                entry = next((e for e in ALIASES['items'] if e.get('nameJa') == item.get('nameJa')), None)
                if entry:
                    item['name'] = (entry['aliases'] or [entry['nameJa']])[0]
        for location in payloads['shops']['locations']:
            for shop in location['shops']:
                for item in shop['items']:
                    entry = next((e for e in ALIASES['items'] if e.get('nameJa') == item.get('nameJa')), None)
                    if entry:
                        item['name'] = (entry['aliases'] or [entry['nameJa']])[0]
        normalize_payloads(**payloads)
        self.assertEqual(payloads, expected)
        normalize_payloads(**payloads)
        self.assertEqual(payloads, expected, 'Normalization must be idempotent')


if __name__ == '__main__':
    unittest.main()
