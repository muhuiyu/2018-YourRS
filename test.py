import json
with open('data/product.json') as f: data = json.load(f)

item = {}

for d in data:
    for i in d['品項']:
        if not i in item: item[i] = []
        color = d['顏色']
        if color=='': color = 'NOCOLOR'
        if not color in item[i]: item[i].append(color)

with open('data/product_color.json','w') as f: json.dump(item, f)
