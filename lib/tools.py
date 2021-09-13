# coding: utf8
import codecs, json, itertools

def JSONload(file):
    with codecs.open(file, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    return obj

def JSONdump(file, obj):
    with codecs.open(file, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent = 4)

def find_chinese_num(string):
    number_set = ['〇','零','一','壹','二','貳','三','參','四','肆','五','伍','六','陸','七','柒','八','捌','九','玖','十','拾','百','佰','千','仟','萬','億','兆','兩','廿','卅','卌']
    tmp = ''
    last_i = -1
    for i,c in enumerate(string):
        if c in number_set and last_i in [i-1, -1]:
            tmp+=c
            last_i = i
        else: last_i = -1
    return tmp

def chinese2num(chinese):
    if chinese=='': return 0
    numbers = {'零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '壹':1, '貳':2, '贰':2, '參':3, '叁':3, '肆':4, '伍':5, '陸':6, '陆':6, '柒':7, '捌':8, '玖':9, '兩':2, '两':2, '廿':20, '卅':30, '卌':40}
    units = {'個':1, '个':1, '十':10, '百':100, '千':1000, '萬':10000, '万':10000, '億':100000000, '亿':100000000, '拾':10, '佰':100, '仟':1000}
    number, pureNumber = 0, True
    for i in range(len(chinese)):
        if chinese[i] in units or chinese[i] in ['廿', '卅', '卌', '虚', '圆', '近', '枯', '无']:
            pureNumber = False
            break
        if chinese[i] in numbers:
            number = number * 10 + numbers[chinese[i]]
    if pureNumber:
        return number
    number = 0
    for i in range(len(chinese)):
        if chinese[i] in numbers or chinese[i] == '十' and (i == 0 or  chinese[i - 1] not in numbers or chinese[i - 1] == '零'):
            base, currentUnit = 10 if chinese[i] == '十' and (i == 0 or chinese[i] == '十' and chinese[i - 1] not in numbers or chinese[i - 1] == '零') else numbers[chinese[i]], '个'
            for j in range(i + 1, len(chinese)):
                if chinese[j] in units:
                    if units[chinese[j]] >= units[currentUnit]:
                        base, currentUnit = base * units[chinese[j]], chinese[j]
            number = number + base
    return number

def convertnum(string):
    numstr = find_chinese_num(string)
    if numstr!='': string = string.replace(numstr, str(chinese2num(numstr)))
    return string

def isgood(parameters):
    if 'sentiment' in parameters:
        if parameters['sentiment'] in ['稱讚','好用','喜歡','想','nice_良好']: return True
    elif 'mediocre_可' in parameters: return True
    else: return False
