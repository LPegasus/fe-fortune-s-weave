"""Rules shared by research imports, full rebuilds, and local data cleanup."""
import copy
import json
from pathlib import Path

ALIASES=json.loads((Path(__file__).resolve().parent/'data/name-aliases.json').read_text(encoding='utf-8-sig'))
RULE='loves_over_likes'
NOTE='同一礼物同时列为“非常喜欢”和“喜欢”时，按规则仅保留在“非常喜欢”；原始来源等级保留供核对。'

def item_identity(item):
    jp=item.get('nameJa');name=item.get('name') or item.get('itemName')
    for entry in ALIASES['items']:
        if (jp and jp in [entry.get('nameJa'),*entry['aliases']]) or (name and name in [entry['canonicalName'],*entry['aliases']]):
            return entry.get('nameJa') or entry['canonicalName']
    return jp or name

def add_unique(values,value):
    if value not in values:values.append(copy.deepcopy(value))

def enforce_gift_precedence(gifts):
    """Remove overlapping likes; attach their evidence to the retained love.

    Item-specific user corrections are applied by the importer before this rule.
    Unmodified source snapshots remain separate from the display data.
    """
    removed=0
    for character in gifts.get('characters',[]):
        loves={item_identity(i):i for i in character['loves']}
        likes=[]
        for item in character['likes']:
            match=loves.get(item_identity(item))
            if match is None:
                likes.append(item);continue
            removed+=1
            resolution=match.setdefault('preferenceResolution',{
                'rule':RULE,'keptPreference':'loves','removedPreference':'likes','removedLikeSourceIds':[]
            })
            for sid in item.get('sourceIds',[]):add_unique(resolution['removedLikeSourceIds'],sid)
            observations=match.setdefault('sourceObservations',[])
            for observation in item.get('sourceObservations',[]):add_unique(observations,observation)
            # Source IDs on the love itself continue to mean support for loves.
            for sid in item.get('sourceIds',[]):
                if not any(o.get('sourceId')==sid and o.get('preference')=='likes' for o in observations):
                    add_unique(observations,{'sourceId':sid,'preference':'likes','rawName':item.get('nameJa') or item['name']})
            for conflict in item.get('preferenceConflicts',[]):add_unique(match.setdefault('preferenceConflicts',[]),conflict)
        character['likes']=likes
        for item in character['loves']+character['likes']:item.pop('preferenceConflict',None)
        character['notes']=[n for n in character.get('notes',[]) if '按并集保留在两栏' not in n]
        if any(i.get('preferenceResolution',{}).get('rule')==RULE for i in character['loves']):
            add_unique(character['notes'],NOTE)
    gifts['preferenceRules']={'overlap':RULE,'description':NOTE}
    return removed
