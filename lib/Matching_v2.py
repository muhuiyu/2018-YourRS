import re
import json
import codecs
import pickle

entity_info = None
intents_info = None
re_pattern_list = None

def JSONload(file):
    with codecs.open(file, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    return obj

def JSONdump(file, obj):
    with codecs.open(file, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent = 4)

def TransRegExp(pattern):
    global entity_info

    reg_exp = ''
    entities = ''
    do_Replace = False

    layer = 0

    for ch in pattern:
        if not do_Replace:
            if ch == '(':
                layer += 1
                do_Replace = True
            reg_exp += ch
        else:
            if ch == '(':
                if entities != '':
                    reg_exp += entities
                    entities = ''
                layer += 1
                reg_exp += ch
            elif ch == ')':
                elist = entities.split('|')
                terms_list = []

                sub_re_exp = '('

                for entity in elist:

                    if entity in entity_info:
                        terms = SearchTerms(entity)
                    else:
                        terms = SearchTerms(entity.rsplit('_', 1)[0])

                    if len(terms) > 0:
                        terms_list = list(set(terms))
                        terms_list = [re.escape(term) for term in terms_list]
                        sub_re_exp += '(?P<' + entity + '>' + '|'.join(terms_list) + ')' + '|'
                    else:
                        sub_re_exp += entity + '|'

                reg_exp += sub_re_exp[:-1] + ')' + ch
                entities = ''
                layer -= 1
                if layer == 0: do_Replace = False
            else:
                entities += ch

    reg_exp = reg_exp.replace('()','')
    reg_exp = reg_exp.replace('(|','|(')
    regex = re.compile(reg_exp)
    return regex

def LoadPatterns(intents_info):
    re_pattern_list = []
    for cate in intents_info.keys():
        for pattern in intents_info[cate]:
            regex = TransRegExp(pattern)
            re_pattern_list.append((regex, cate))
    return re_pattern_list

def Match(sent):
    intent_cate = ''
    slot = {}

    max_score = -1
    for regex, cate in re_pattern_list:
        obj = regex.search(sent)
        if obj:
            start_idx = obj.start()
            end_idx = obj.end()
            score = (end_idx - start_idx) / len(sent)
            if score > max_score:
                intent_cate = cate
                slot = obj.groupdict()
                max_score = score
    return intent_cate, slot

def SearchTerms(entity):
    global entity_info

    tlist = []

    if entity in entity_info:
        next_entities_list, synonyms_list = entity_info[entity]
        tlist += synonyms_list
        for next_entity in next_entities_list:
            tlist += SearchTerms(next_entity)

    return tlist

if __name__ == '__main__':

    entity_info = JSONload('../data/entity_info.json')
    intents_info = JSONload('../data/intent_pattern.json')
    re_pattern_list = LoadPatterns(intents_info)

    while True:
        sent = input('>>> ')
        if sent == 'exit': break
        print(Match(sent))
    # sent = '有沒有保濕效果的相關評價？'
    # print(Match(sent))
