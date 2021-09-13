import csv, json, os, re
import xml.etree.ElementTree as ET


def raw2dict(subfolder):
    foldername = 'data/purged_article_gnrid/'+subfolder
    folder_path =  os.path.join(os.getcwd(), foldername)
    allfile = os.listdir(folder_path)
    outputdir = os.path.join(os.getcwd(), 'data/purged_output_xml/'+subfolder)#'MATBN_raw_json/'+filename.split('/')[1].split('.')[0]+'.json'
    if not os.path.exists(outputdir): os.makedirs(outputdir)
    for filename in allfile:
        out = []
        with open(folder_path+'/'+filename,'r', encoding='utf8') as f: lines = tuple(f)
        for l in lines:
            a = {'sentence':re.sub("<.*?>", "", l),'item':[]}
            # print(re.findall(r'<product(.*?) >', l))
        for l in lines: out.append('<sentence>'+l.replace('\n','')+'</sentence>')
        # print(filename, out[0])
        with open(outputdir+'/'+filename,'w', encoding='utf8') as f: print('<document>'+''.join(out)+'</document>', file=f)
    pass

def dict2json(subfolder):    # dict file to json file
    foldername = 'data/purged_output_xml/'+subfolder
    folder_path = os.path.join(os.getcwd(), foldername)
    allfile = os.listdir(folder_path)
    outputdir = os.path.join(os.getcwd(), 'data/purged_output_json/'+subfolder)
    if not os.path.exists(outputdir): os.makedirs(outputdir)

    for filename in allfile:
        tree = ET.parse(folder_path+'/'+filename)
        root = tree.getroot()
        allout = []
        for sentence in root:
            sent = ''
            out = {'sentence':'','item':[]}
            children = sentence.findall('product')
            if sentence.text: sent+=sentence.text
            if len(children):
                for child in children:
                    if child.text: sent+=child.text
                    gid = child.attrib['gid']
                    # print(gid)
                    if gid.isdigit() and gid not in out['item']: out['item'].append(gid)
            out['sentence'] = sent
            # print(filename, out['item'])
            allout.append(out)
        outputfilename = filename.replace('.xml','.json')
        with open(outputdir+'/'+outputfilename,'w', encoding='utf8') as f: json.dump(allout,f)
    pass

def json2db(subfolder):   # json file to database
    RANGE = 5
    with open('data/product_dict_effect.json','r', encoding='utf8') as f: data = json.load(f)   # product list in dict
    foldername = 'data/purged_output_json/'+subfolder
    folder_path = os.path.join(os.getcwd(), foldername)
    allfile = os.listdir(folder_path)
    for filename in allfile:
        with open(folder_path+'/'+filename, 'r', encoding='utf8') as f: article = json.load(f)
        for i in range(len(article)):
            if len(article[i]['item'])==0: continue
            for item in article[i]['item']:
                if item in data:
                    # print(data[item])
                    data[item]['討論文章數']+=1
                    for j in range(-RANGE, RANGE):
                        if i+j>=0 and i+j<len(article):
                            sent = article[i+j]
                            for e in data[item]['功效']:
                                for effect in EFFECTLIST[e]:
                                    if effect in sent['sentence']:
                                        data[item]['功效'][e].append({'sentence':sent['sentence'], 'article': filename})
                                    # print(e, sent)
                    # print(data[item]['功效'])
    with open('data/product_dict_effect.json','w', encoding='utf8') as f: json.dump(data,f)   # product list in dict
    pass

def reserve_entity():
    with open('data/clean_entity_info.json') as f: data = json.load(f)
    reversed_entity = {}
    for k,v in data.items():
        for name in v[1]:
            print('{} -> {}'.format(k, name))
            if name in reversed_entity and k!=reversed_entity[name]: print('{} vs. {} -> {}'.format(k, reversed_entity[name], name))
            else: reversed_entity[name] = k
    with open('data/reversed_clean_entity_info.json','w') as f: json.dump(reversed_entity, f)
    pass

def clean_sent(s):
    # 全部小寫, 空白換成□, -_-_++
    s = s.lower()
    s = re.sub(r'[^\S\n]', r'□', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff、\n□]+', '', s)
    s = re.sub(r'□+($|[0-9\u4e00-\u9fff、\n])', r'\1', s)
    s = re.sub(r'(\A|[0-9\u4e00-\u9fff、\n])□+', r'\1', s)
    s = re.sub(r'\n+', '\n', s)
    s = re.sub(r'□+', '□', s)
    return s

def clean_entity():
    with open('data/entity_info.json') as f: data = json.load(f)
    for i,v in enumerate(data['name'][0]):
        new_v = clean_sent(v)
        print('{}     {}'.format(v,new_v))
        if new_v !=v:
            data['name'][0][i] = new_v
            data[new_v] = data[v]
            del data[v]
    for i,v in enumerate(data['brand'][0]):
        new_v = clean_sent(v)
        print('{}     {}'.format(v,new_v))
        if new_v !=v:
            data['brand'][0][i] = new_v
            data[new_v] = data[v]
            del data[v]
    with open('data/clean_entity_info.json','w') as f: json.dump(data,f)

# with open('data/product_dict.json','r') as f: data = json.load(f)
# for k,v in data.items(): data[k]['討論文章數'] = 0
# with open('data/product_dict2.json','w') as f: json.dump(data,f)

# folder_path = os.path.join(os.getcwd(), 'data/purged_article_gnrid')
# folders= os.listdir(folder_path)
# for subfolder in folders: print(subfolder)
# raw2dict(subfolder)
# dict2json(subfolder)
# json2db(subfolder)

clean_entity()
reserve_entity()
# with open('data/repo/product.txt') as f: data = f.readlines()
