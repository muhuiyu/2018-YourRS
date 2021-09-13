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
    
    terms_info = {}
    
    entities_path = '.\entities\*.json'
    for file_path in glob.glob(entities_path):
        entity_type = file_path.rsplit('\\', 1)[1].split('_',1)[0]
        #entity_type = '_' + entity_type + '_'
        entities = JSONload(file_path)
        for entity in entities:
            value = entity["value"].lower()
            #value = '_' + value.replace(' ', '_') + '_'
            value = value.replace(' ', '_')
            terms_list = entity["synonyms"]
            temp = {term.lower():(value, entity_type) for term in terms_list if len(term.split()) == 1}
            terms_info.update(temp)

    JSONdump('terms_info.json', terms_info)

    with codecs.open('dict.txt', 'w', 'utf-16-le') as f:
        f.write('\ufeff')
        tlist = list(terms_info.keys())
        for t in tlist:
            f.write(t + '\n')
        
    
