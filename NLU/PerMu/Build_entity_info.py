import glob
import json
import codecs

def JSONload(file):
    with codecs.open(file, 'r', encoding='utf-8') as f:
        entities = json.load(f)
    return entities

def JSONdump(file, obj):
    with codecs.open(file, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent = 4)

if __name__ == '__main__':
    
    entity_info = {}
    
    entities_path = '.\entities\*.json'
    for file_path in glob.glob(entities_path):
        entity_type = file_path.rsplit('\\', 1)[1].split('_',1)[0]
        #entity_type = '_' + entity_type + '_'
        entities = JSONload(file_path)
        for entity in entities:
            value = entity["value"]
            value = value.replace(' ', '_')
            if entity_info.get(entity_type) is None: entity_info[entity_type] = [[], []] #next_layer_entity, words
            entity_info[entity_type][0].append(value)
            for terms in entity["synonyms"]:
                if entity_info.get(value) is None: entity_info[value] = [[], []] #next_layer_entity, words
                entity_info[value][1].append(terms)

    JSONdump('entity_info.json', entity_info)
    
