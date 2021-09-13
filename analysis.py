import csv, json, os, re
import xml.etree.ElementTree as ET

with open('data/product_dict_effect.json','r') as f: data = json.load(f)

for k,v in data.items():
    for e, ev in v['功效'].items():
        if ev!=[]: print(e, ev)
    print()
