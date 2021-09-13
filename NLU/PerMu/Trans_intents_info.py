import re
import glob
import json
import codecs

def JSONload(file):
    with codecs.open(file, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    return obj

def JSONdump(file, obj):
    with codecs.open(file, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent = 4)
        
if __name__ == '__main__':
    
    intents_path = ".\\intents\\*_usersays_zh-cn.json"
    terms_info = JSONload('terms_info.json')
    entity_info = JSONload('entity_info.json')
    
    entity_type = set(entity_info.keys())
    intents_info = {}
        
    for file_path in glob.glob(intents_path):
        intent_cate = file_path.rsplit('\\', 1)[1].rsplit('_',2)[0]
        if intent_cate not in intents_info:
            intents_info[intent_cate] = []
            
        intents = JSONload(file_path)
        for intent in intents:
            intent_alias_list = []
            for item in intent["data"]:
                text = item["text"]
                if text == ' ': continue
                if terms_info.get(text) is not None:
                    alias = terms_info[text][0]
                    intent_alias_list.append(alias)
                else:
                    intent_alias_list.append(text)

                if '@' in text and ':' in text:
                    intent_alias_list.pop()
                    text = re.split('[ ]+', text)
                    for txt in text:
                        fields = re.split('@[a-zA-z_]+:', txt)
                        _list = [re.sub(r'[0-9]+', '', field.split('_')[0]) for field in fields if field != '']
                        intent_alias_list += _list
                        
                new_intent_alias_list = []
                for i, item in enumerate(intent_alias_list):
                    item = re.sub(r'\s+', ' ', item)
                    if item in entity_type:
                        item = '(' + item + ')' 
                        new_intent_alias_list.append(item)
                    else:
                        new_intent_alias_list.append(item)

            new_intent_alias_str = ''.join(new_intent_alias_list)
            intents_info[intent_cate].append(new_intent_alias_str)
            
        JSONdump('intents_info.json', intents_info)
