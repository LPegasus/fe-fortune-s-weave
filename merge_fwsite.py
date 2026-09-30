"""Union imported gift observations with local data; preserve user corrections."""
import copy
import json
from pathlib import Path
from normalize_names import ALIASES, normalize_name, normalize_payloads
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
SOURCE={'id':'fwsite-misc','language':'zh','title':'万缕千丝中文攻略站 · 礼物与商人','url':'https://fire-emblem-fw.site/misc.html','note':'2026-10-01 导入；礼物主要转译 Game8，并含玩家补充。按日文名称取并集，冲突保留原始来源，用户修正优先。','accessed':'2026-10-01'}
ALIGN_SOURCE={'id':'game8-gift-alignment','language':'ja','title':'Game8 · 礼物原名对照','url':'https://game8.jp/fe-banshisenko/816847','note':'用于核对中文站译名与日文物品身份；不将转译页面视为独立实测。','accessed':'2026-10-01'}
CHAR_SOURCE={'id':'fwsite-characters','language':'zh','title':'万缕千丝中文攻略站 · 人物图鉴','url':'https://fire-emblem-fw.site/characters.html','note':'人物通过共用 GameWith 头像编号及对应日文名对齐。','accessed':'2026-10-01'}

def add_unique(values,value):
    if value not in values:values.append(value)

def identity(item):
    jp=item.get('nameJa');name=item.get('name') or item.get('itemName')
    for entry in ALIASES['items']:
        if jp==entry.get('nameJa') or jp in entry['aliases'] or name in [entry['canonicalName'],*entry['aliases']]:
            return entry['nameJa']
    return jp or name

def merge_gifts(gifts,sources,corrections=None):
    path=DATA/'imports/fwsite-gifts.json'
    if not path.exists():return {}
    imported=json.loads(path.read_text(encoding='utf-8'))
    corrections=corrections if corrections is not None else json.loads((DATA/'gift-corrections.json').read_text(encoding='utf-8'))
    overrides={(x['characterId'],identity({'name':x.get('itemName'),'nameJa':x.get('itemNameJa')})):x for x in corrections}
    for source in [SOURCE,ALIGN_SOURCE,CHAR_SOURCE]:
        if not any(s['id']==source['id'] for s in sources):sources.append(copy.deepcopy(source))
    stats={'sourceCharacters':len(imported['characters']),'sourcePreferences':0,'addedPreferences':0,'matchedPreferences':0,'userOverrides':0,'conflictingItems':0}
    for character in gifts['characters']:
        # Canonical Japanese keys unify previously unidentified items and spelling aliases.
        for key in ['loves','likes']:
            dedup={}
            for item in character[key]:
                jp=identity(item)
                if jp!=item.get('nameJa'):
                    if item.get('nameJa'):add_unique(item.setdefault('originalNameJa',[]),item['nameJa'])
                    item['nameJa']=jp
                item['name']=normalize_name('items',item['name'],jp)
                if jp not in dedup:dedup[jp]=item
                else:
                    for sid in item['sourceIds']:add_unique(dedup[jp]['sourceIds'],sid)
            character[key]=list(dedup.values())
    for row in imported['characters']:
        character=next(c for c in gifts['characters'] if c['id']==row['characterId'])
        add_unique(character['sourceIds'],SOURCE['id'])
        for preference in ['loves','likes']:
            for incoming in row[preference]:
                stats['sourcePreferences']+=1
                jp=identity(incoming);override=overrides.get((character['id'],jp));target=override['to'] if override else preference
                other='likes' if target=='loves' else 'loves'
                observation={'sourceId':SOURCE['id'],'sourceUrl':row['sourceUrl'],'preference':preference,'rawName':incoming['rawName'],'upstreamSource':row.get('upstreamSource'),'observedAt':imported['fetchedAt']}
                match=next((i for i in character[target] if identity(i)==jp),None)
                if not match:
                    match={'name':incoming['name'],'nameJa':jp,'kind':'item','sourceIds':[]};character[target].append(match);stats['addedPreferences']+=1
                else:stats['matchedPreferences']+=1
                add_unique(match.setdefault('sourceObservations',[]),observation)
                if target==preference:add_unique(match['sourceIds'],SOURCE['id'])
                else:
                    stats['userOverrides']+=1
                    add_unique(match.setdefault('preferenceConflicts',[]),{'sourceId':SOURCE['id'],'reportedPreference':preference,'keptPreference':target,'resolution':'user_override'})
                if override:
                    match['preferenceCorrection']=copy.deepcopy(override)
                    for old in character[other]:
                        if identity(old)==jp:
                            for evidence in old.get('sourceObservations',[]):add_unique(match['sourceObservations'],evidence)
                    character[other]=[i for i in character[other] if identity(i)!=jp]
        if row.get('seriesNote'):
            add_unique(character.setdefault('sourceNotes',[]),{'sourceId':SOURCE['id'],'text':row['seriesNote'],'usedForPreferenceExpansion':False})
    for character in gifts['characters']:
        both={identity(i) for i in character['loves']}&{identity(i) for i in character['likes']}
        stats['conflictingItems']+=len(both)
        for k in ['loves','likes']:
            for item in character[k]:
                if identity(item) in both:item['preferenceConflict']=True
        if both:
            note='部分礼物的喜好等级在来源间不一致，已按并集保留在两栏并标注“来源分歧”；不代表一次送礼同时获得两种效果。'
            add_unique(character.setdefault('notes',[]),note)
        character['status']='documented' if character['loves'] or character['likes'] else 'unknown'
        for note in list(character.get('notes',[])):
            if '鱼酱' in note and '日文名称待确认' in note:character['notes'].remove(note)
        for correction in corrections:
            if correction['characterId']==character['id']:add_unique(character.setdefault('notes',[]),correction['note'])
    normalize_payloads(gifts=gifts,sources=sources)
    gifts['updated']=imported['fetchedAt']
    return stats

def merge_shops(shops,sources):
    path=DATA/'imports/fwsite-shops.json'
    if not path.exists():return {}
    imported=json.loads(path.read_text(encoding='utf-8'))
    for source in [
        {'id':'fwsite-merchants','language':'zh','title':'万缕千丝中文攻略站 · 商人截图与帝都兑换','url':imported['url'],'note':imported['note'],'accessed':imported['fetchedAt']},
        {'id':'gamewith-item-alignment','language':'ja','title':'GameWith · 物品原名对照','url':'https://gamewith.jp/fefw/574296','note':'按原名、用途、获取地点核对物品及材料的不同中文译名。','accessed':imported['fetchedAt']},
        {'id':'gamewith-weapon-alignment','language':'ja','title':'GameWith · 武器原名对照','url':'https://gamewith.jp/fefw/576859','note':'核对武器名称、数值和获取地点。','accessed':imported['fetchedAt']}
        ,{'id':'gamewith-equipment-alignment','language':'ja','title':'GameWith · 装备原名对照','url':'https://gamewith.jp/fefw/574252','note':'按装备效果区分面具、护符等不同物品，避免将相近中文译名误合并。','accessed':imported['fetchedAt']}
    ]:
        if not any(s['id']==source['id'] for s in sources):sources.append(source)
    stats={'sourceLocations':len(imported['locations']),'sourceObservations':0,'addedLocations':0,'addedProducts':0,'matchedProducts':0}
    for row in imported['locations']:
        loc=next((l for l in shops['locations'] if l['id']==row['locationId']),None)
        if loc is None:
            loc={'id':row['locationId'],'name':row['name'],'nameJa':row['nameJa'],'type':'旅行商人观测地点','shops':[],'sourceIds':[],'notes':[]}
            shops['locations'].append(loc);stats['addedLocations']+=1
        add_unique(loc['sourceIds'],imported['sourceId'])
        add_unique(loc.setdefault('aliases',[]),row['rawName'])
        shop=next((s for s in loc['shops'] if s['type']==row['type']),None)
        if shop is None:
            shop={'type':row['type'],'status':'documented','items':[]};loc['shops'].append(shop)
        shop['status']='documented'
        add_unique(shop.setdefault('notes',[]),row.get('context',imported['context']))
        if row['type']=='travel':add_unique(loc['notes'],'旅行商人会随机移动；此处仅记录截图中的出现地点，不能视为固定店铺。')
        for incoming in row['items']:
            stats['sourceObservations']+=1
            matched=next((i for i in shop['items'] if identity(i)==identity(incoming)),None)
            observation={**copy.deepcopy(incoming),'sourceId':imported['sourceId'],'sourceUrl':imported['url'],'observedAt':imported['fetchedAt'],'context':row.get('context',imported['context']),'stockMeaning':'observed_remaining' if incoming['stock'] is not None else 'not_reported'}
            if matched is None:
                matched={k:copy.deepcopy(incoming[k]) for k in ['name','nameJa','stock','price','exchange']}
                matched.update(stockStatus='known' if incoming['stock'] is not None else 'unknown',stockMeaning=observation['stockMeaning'],sourceIds=[],phase=observation['context'])
                shop['items'].append(matched);stats['addedProducts']+=1
            else:stats['matchedProducts']+=1
            # Snapshot stock may be after purchases: never replace earlier inventory.
            add_unique(matched.setdefault('sourceObservations',[]),observation)
            add_unique(matched['sourceIds'],imported['sourceId'])
            if not matched['exchange'] and incoming['exchange']:
                matched['exchange']=copy.deepcopy(incoming['exchange']);matched['exchangeSourceId']=imported['sourceId']
            if matched['price'] is None and incoming['price'] is not None:
                matched['price']=incoming['price'];matched['priceSourceId']=imported['sourceId']
    normalize_payloads(shops=shops)
    shops['updated']=imported['fetchedAt']
    return stats

if __name__=='__main__':
    gifts=json.loads((DATA/'gifts.json').read_text(encoding='utf-8'));sources=json.loads((DATA/'sources.json').read_text(encoding='utf-8'))
    shops=json.loads((DATA/'shops.json').read_text(encoding='utf-8'))
    stats={'gifts':merge_gifts(gifts,sources),'shops':merge_shops(shops,sources)}
    for name,value in [('gifts',gifts),('shops',shops),('sources',sources)]:
        (DATA/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=DATA/'fwsite-merge-report.json'
    previous=json.loads(report.read_text(encoding='utf-8')) if report.exists() else {}
    if 'sourceCharacters' in previous:stats['gifts']=previous
    elif previous:stats=previous
    report.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False))
