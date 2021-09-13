import re, pickle
from lib.tools import *

entity_info = None
intents_info = None
re_pattern_list = None

class IntentClassifier(object):
    """docstring for IntentClassifier."""
    def __init__(self, entity_file, reversed_entity_file, intent_file):
        super(IntentClassifier, self).__init__()
        self.entity_info = JSONload(entity_file)
        self.reversed_entity_info = JSONload(reversed_entity_file)
        self.intents_info = JSONload(intent_file)
        self.re_pattern_list = self.LoadPatterns()

    def TransRegExp(self, pattern):
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
                        if entity in self.entity_info:
                            terms = self.SearchTerms(entity)
                        else:
                            terms = self.SearchTerms(entity.rsplit('_', 1)[0])
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
                else: entities += ch

        reg_exp = reg_exp.replace('()','')
        reg_exp = reg_exp.replace('(|','|(')
        regex = re.compile(reg_exp)
        return regex

    def LoadPatterns(self):
        re_pattern_list = []
        for cate in self.intents_info.keys():
            for pattern in self.intents_info[cate]:
                regex = self.TransRegExp(pattern)
                re_pattern_list.append((regex, cate))
        return re_pattern_list

    def Match(self, sent):
        intent_cate = ''
        slot = {}
        max_score = -1
        for regex, cate in self.re_pattern_list:
            obj = regex.match(sent)
            if obj:
                start_idx = obj.start()
                end_idx = obj.end()
                score = (end_idx - start_idx) / len(sent)
                if score > max_score:
                    intent_cate = cate
                    slot = obj.groupdict()
                    max_score = score
        if intent_cate=='': intent_cate = 'chat'
        for k,v in slot.items():
            if v in [None,'']: continue
            slot[k] = self.reversed_entity_info[v]
        return intent_cate, slot

    def SearchTerms(self, entity):
        tlist = []
        if entity in self.entity_info:
            next_entities_list, synonyms_list = self.entity_info[entity]
            tlist += synonyms_list
            for next_entity in next_entities_list: tlist += self.SearchTerms(next_entity)
        return tlist
