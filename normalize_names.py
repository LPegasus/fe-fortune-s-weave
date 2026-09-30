"""Apply approved names and gift precedence while retaining source evidence."""
import json
from pathlib import Path
from gift_rules import enforce_gift_precedence

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
ALIASES = json.loads((DATA / 'name-aliases.json').read_text(encoding='utf-8-sig'))
INDEX = {}
for scope in ('characters', 'items', 'locations'):
    INDEX[scope] = {}
    for entry in ALIASES.get(scope, []):
        for alias in [entry['canonicalName'], entry.get('nameJa'), entry.get('nameEn'), *entry['aliases']]:
            if not alias:
                continue
            previous = INDEX[scope].setdefault(alias, entry['canonicalName'])
            if previous != entry['canonicalName']:
                raise ValueError(f'Conflicting {scope} alias: {alias}')


def normalize_name(scope, name, name_ja=None, name_en=None):
    """Match original names first; character aliases never affect item names."""
    index = INDEX[scope]
    for value in (name_ja, name_en, name):
        if value in index:
            return index[value]
    if scope == 'items' and isinstance(name, str):
        for rule in ALIASES['itemSubstringRules']:
            name = name.replace(rule['from'], rule['to'])
        return index.get(name, name)
    return name


def normalize_item(item):
    item['name'] = normalize_name('items', item.get('name'), item.get('nameJa'), item.get('nameEn'))
    for material in item.get('exchange', []):
        normalize_item(material)
    for observation in item.get('sourceObservations', []):
        if 'name' in observation:
            normalize_item(observation)
    if 'preferenceCorrection' in item:
        normalize_correction(item['preferenceCorrection'])


def normalize_correction(correction):
    if 'itemName' in correction:
        correction['itemName'] = normalize_name('items', correction['itemName'], correction.get('itemNameJa'))
    if 'item' in correction:
        normalize_item(correction['item'])


def normalize_payloads(gifts=None, shops=None, sources=None, portraits=None, corrections=None):
    for character in (gifts or {}).get('characters', []):
        character['name'] = normalize_name('characters', character['name'], character.get('nameJa'), character.get('nameEn'))
        if character.get('portrait'):
            character['portrait']['alt'] = character['name'] + '的人物头像'
        for key in ('loves', 'likes'):
            for item in character[key]:
                normalize_item(item)
    for location in (shops or {}).get('locations', []):
        location['name'] = normalize_name('locations', location['name'], location.get('nameJa'), location.get('nameEn'))
        for shop in location['shops']:
            for item in shop['items']:
                normalize_item(item)
    for source in sources or []:
        if source['id'].startswith('cn-') and ' · ' in source['title']:
            prefix, name = source['title'].split(' · ', 1)
            source['title'] = prefix + ' · ' + normalize_name('characters', name)
    for portrait in (portraits or {}).values():
        name = portrait['alt'].removesuffix('的人物头像')
        portrait['alt'] = normalize_name('characters', name) + '的人物头像'
    for correction in corrections or []:
        normalize_correction(correction)
    if gifts is not None:
        enforce_gift_precedence(gifts)


def main():
    files = {'gifts': 'gifts', 'shops': 'shops', 'sources': 'sources',
             'portraits': 'portraits', 'corrections': 'gift-corrections'}
    payloads = {key: json.loads((DATA / (name + '.json')).read_text(encoding='utf-8-sig'))
                for key, name in files.items()}
    before = {key: json.dumps(value, ensure_ascii=False) for key, value in payloads.items()}
    normalize_payloads(**payloads)
    for key, value in payloads.items():
        if json.dumps(value, ensure_ascii=False) != before[key]:
            (DATA / (files[key] + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Keep the offline HTML copy consistent after importing external JSON.
    bundle = {key: payloads[key] for key in ('gifts', 'shops', 'sources')}
    bundle['nameAliases'] = ALIASES
    (ROOT / 'data.js').write_text('window.GUIDE_DATA = ' + json.dumps(bundle, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    print('User-approved names applied; offline data synchronized.')


if __name__ == '__main__':
    main()
