# coding:utf8
import json
from IPython import embed
# with open('data/entity_info.json','r') as f: data = json.load(f)
# action_list = []
# for item in data['item'][0]: action_list.append('recommend_slot_item_'+item)
# for brand in data['brand'][0]: action_list.append('recommend_slot_brand_'+brand)
# for color in data['color'][0]:action_list.append('recommend_slot_color_'+color)
# for effect in data['effect'][0]:action_list.append('recommend_slot_effect_'+effect)
# print(len(action_list))
#
with open('entity_info.json') as f: data = json.load(f)
reversed_entity = {}
for k,v in data.items():
    for name in v[1]:
        print('{} -> {}'.format(k, name))
        if name in reversed_entity and k!=reversed_entity[name]:
            print('{} vs. {} -> {}'.format(k, reversed_entity[name], name))
            # embed()
        else:
            reversed_entity[name] = k
with open('reversed_entity_info.json','w') as f: json.dump(reversed_entity, f)
