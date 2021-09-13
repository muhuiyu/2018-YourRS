# coding: utf8
import json, numpy as np
from lib.parameters import *
from lib.tools import *

def search_info(recommendList, info):
    for k,v in info.items():
        if v=='' or v==-1: continue
        if k=='where': return recommendList[v]
        if k in ['sentiment','bad','pricelowerbound','priceupperbound']: continue
        for r in recommendList:
            if r[k]==v: return r
    return None

class Database(object):
    """docstring for Database."""
    def __init__(self, filename):
        super(Database, self).__init__()
        with open(filename, 'r') as f: self.data = json.load(f)
        return

class SlotList(object):
    """docstring for SlotList"""
    def __init__(self):
        super(SlotList, self).__init__()
        self.info = {'path':'', 'brand':'', 'series_name':'', 'name':'', 'maincate':'', 'category':'',
                        'item':'', 'color':'', 'listed_time':'', 'pricelowerbound':-1, 'priceupperbound':-1,
                        'where':'','sentiment':'', 'bad':'', 'price_limit':''
                    }
        self.info2 = {'path':'', 'brand':'', 'series_name':'', 'name':'', 'maincate':'', 'category':'',
                        'item':'', 'color':'', 'listed_time':'', 'pricelowerbound':-1, 'priceupperbound':-1,
                        'where':'','sentiment':'', 'bad':'', 'price_limit':''
                    }
        self.others = {'occasion':'', 'style':''}
        self.skin = {'skinType':'','skinProblem':''}
        self.ask = ''
        self.effect = EFFECTLIST
        self.effect = {key: 0 for key in self.effect}
        self.effect_used = 0

    def empty(self):
        self.info = {'path':'', 'brand':'', 'series_name':'', 'name':'', 'maincate':'', 'category':'',
                        'item':'', 'color':'', 'listed_time':'', 'pricelowerbound':-1, 'priceupperbound':-1,
                        'where':'','sentiment':'', 'bad':'', 'price_limit':''
                    }
        self.info2 = {'path':'', 'brand':'', 'series_name':'', 'name':'', 'maincate':'', 'category':'',
                        'item':'', 'color':'', 'listed_time':'', 'pricelowerbound':-1, 'priceupperbound':-1,
                        'where':'','sentiment':'', 'bad':'', 'price_limit':''
                    }
        self.others = {'occasion':'', 'style':''}
        self.skin = {'skinType':'','skinProblem':''}
        self.ask = ''
        self.effect = {key: 0 for key in self.effect}
        self.effect_used = 0

    def insert(self, intent, parameters, askedslot):
        if intent=='search_makeup': self.others = parameters
        elif intent=='aboutYou': self.ask = parameters['query']
        else:
            price = 0
            bound = 0
            for k,v in parameters.items():
                if v=='' or v==0 or v==None: continue
                if k in ['brand','item','color']: self.info[k] = v
                elif k=='slot': self.ask = v
                elif k=='effect' or k=='effect1' or k=='effect2':
                    self.effect[v] = 1
                    self.effect_used = 1
                elif k in ['occasion','style']: self.others[k]=v
                elif k in ['skinType','skinProblem']: self.skin[k]=v

            #   if v.lower()=='dr.wu': v='DR.WU'    #### for error of DR.WU QQ ####
            #   if k=='price': price=1
            #   elif k=='bound': bound=1
            #   elif k=='color1': self.info['color']=v
            #   elif k=='color2': self.info2['color']=v
            #   elif k=='brand1': self.info['brand']=v
            #   elif k=='brand2': self.info2['brand']=v
            #   else: self.info[k]=v
            #
            # if price and bound:
            #   if parameters['bound']=='以上': self.info['pricelowerbound'] = parameters['price']
            #   elif parameters['bound']=='以下': self.info['priceupperbound'] = parameters['price']
            #   elif parameters['bound']=='左右':
            #       self.info['pricelowerbound'] = parameters['price']-50
            #       self.info['priceupperbound'] = parameters['price']+50
            # elif price and askedslot!='':
            #   if askedslot=='pricelowerbound': self.info['pricelowerbound'] = parameters['price']
            #   elif askedslot=='priceupperbound': self.info['priceupperbound'] = parameters['price']

        return

    def assign_slot_value(self, slot, value):
        if slot=='effect': self.effect[value] = 1
        elif slot in ['occasion','style']: self.others[slot] = value
        else: self.info[slot] = value
        return

    def re_organize(self, intent, recommendList, userslotlist):
        if self.ask!='' or self.info['bad']!='':
            # if intent=='recommend_slot':
                # if recommendList!=('',''):
                    # self.info[self.ask] = recommendList[1]
                    # return
            if len(recommendList)==1: candidate = recommendList[0]
            else: candidate = search_info(recommendList, self.info)
            if self.info['bad']=='price_tooHigh': self.info['priceupperbound'] = candidate['spec'][0]['price']
            elif self.info['bad']=='price_tooLow': self.info['pricelowerbound'] = candidate['spec'][0]['price']
            else:
                if self.ask in ['color','brand']: self.info[self.ask] = candidate[self.ask]

    def nothingRequired(self):
        return self.nothingRequired_info() and self.nothingRequired_skin() and (self.effect_used==0) and (self.ask=='')

    def nothingRequired_info(self):
        for k,v in self.info.items():
            if v!='' and v!=-1: return False
        return True
    def nothingRequired_skin(self):
        for k,v in self.skin.items():
            if v!='': return False
        return True

    def nothingRequired_effect(self):
        for k,v in self.effect.items():
            if v!=0: return False
        return True

    def nothingRequired_others(self):
        for k,v in self.others.items():
            if v!='': return False
        return True

    def get_used_effect(self):
        effect = []
        for k,v in self.effect.items():
            if v!=0: effect.append(k)
        return effect

    def find_domain(self):
        if self.nothingRequired_others(): return 'inform_item'
        else: return 'inform_makeup'    # default domain

    def load_information(self, chatbot):
        return

    def printslot(self):
        print('(',end='')
        for k,v in self.info.items():
            if v=='' or v==-1: continue
            print(k,':',v,end=' ')
        for k,v in self.effect.items():
            if v==0: continue
            print(k,':',v,end=' ')
        for k,v in self.others.items():
            if v=='': continue
            print(k,':',v,end=' ')
        if self.ask!='': print('ask:',self.ask,end='')
        print(')')


class User(object):
    """docstring for User"""
    def __init__(self, uid):
        super(User, self).__init__()
        # self.skintype = ''
        # self.preference = PREFERLIST
        # self.blacklist = PREFERLIST
        # self.skinstatus = SKINSTATUSDICT
        # self.skinstatus = {key: 0 for key in self.skinstatus}
        # self.slotlist = SlotList()
        # self.score = Score(db)
        self.state = np.zeros(N_SLOTS)
        self.intent = ''
        self.turn = 0

    def empty(self):
        # self.skintype = ''
        # self.preference = PREFERLIST
        # self.blacklist = PREFERLIST
        # self.skinstatus = {key: 0 for key in self.skinstatus}
        # self.slotlist.empty()
        # self.score.empty_score()
        self.state = np.zeros(N_SLOTS)
        self.intent = ''
        self.turn = 0

    def update(self, intent, parameters, prev_action):
        self.state[0] = STATEDICT[intent]
        ##### TODO #####
        entities = {
            'item':{"眉彩": 12,"眼影": 14,"CC霜": 4,"眼部保養": 33,"防曬隔離": 26,"眼唇卸妝": 27,"眼線": 15,"精華液": 23,"蜜粉": 10,"臉部去角質": 31,"卸妝產品": 25,"洗顏產品": 24,"乳霜": 21,"粉底液": 7,"清潔面膜": 30,"腮紅修容": 6,"粉條": 8,"化妝水": 19,"前導保養": 34,"BB霜": 3,"氣墊粉餅": 2,"凝膠凝凍": 22,"保濕噴霧": 29,"妝前打底": 1,"粉霜": 9,"唇膏": 0,"唇部保養": 32,"粉餅": 5,"睫毛膏": 13,"精華油": 28,"遮瑕": 11,"唇筆": 17,"唇彩唇蜜": 16,"保養面膜": 18,"乳液": 20},
            'brand':{"dermalogica德卡": 252,"skinfood": 256,"domohornwrinkle朵茉麗蔻": 341,"kate凱婷": 112,"erborian艾博妍": 199,"suqqu": 205,"dkny": 148,"missha": 0,"revlon露華濃": 290,"jumelle佐媚朵爾": 246,"hacci": 33,"esprique": 16,"uriage優麗雅": 29,"dermal": 307,"dermaction": 6,"fromnature": 135,"facequeen絕世愛美肌": 301,"salvatoreferragamo": 315,"tky": 15,"nooni": 350,"mentholatum曼秀雷敦": 344,"bbia": 248,"remeg潤美肌": 279,"essence": 155,"legere蘭吉兒": 313,"bonanza寶藝": 339,"sebamed施巴": 84,"drorganic": 123,"rahua": 347,"chronoaffection時間寵愛": 134,"fashionkbeauty": 23,"kamill": 32,"陽農園": 354,"megustame美愛美": 169,"jillstuart吉麗絲朵": 52,"diptyque": 82,"valentino范倫鐵諾": 250,"jomalonelondon": 216,"clinique倩碧": 37,"animecosme": 215,"neotec妮傲絲翠": 373,"mio": 83,"forbelovedone寵愛之名": 297,"marykay玫琳凱": 277,"laprairie": 275,"kaideluxe型色大師": 333,"3ce": 183,"mdnaskin": 359,"smithcult": 182,"aveda肯夢": 48,"revive麗膚再生": 198,"clio珂莉奧": 325,"ryo呂": 363,"eos伊歐詩": 209,"tonymoly": 237,"wondercore": 30,"ampmskincare": 201,"media媚點": 10,"kanebo佳麗寶": 206,"caudalie": 114,"hadalabo": 163,"ettusais艾杜紗": 12,"ludeya露蒂雅": 288,"labseries雅男士": 220,"stclare聖克萊爾": 190,"glamglow": 253,"cellina雪芙蘭": 157,"beautia倍立雅": 273,"pure": 281,"hupanique涵沛": 161,"webner葦柏納": 194,"shelleyandteddy": 298,"thecucumber廣源良": 8,"etudehouse": 261,"azlb": 165,"我的美麗日記": 126,"immeme": 259,"oguma水美媒": 312,"zeynabear": 85,"rmk": 136,"skinlife滋卿愛": 280,"avalon": 227,"freshel膚蕊": 202,"azzeen芝妍": 278,"annasui安娜蘇": 180,"youbest優倍多": 75,"forbelovedgirl寵愛女孩": 7,"paltac": 221,"rudyprofumi": 338,"canmake": 231,"chlitina克麗緹娜": 143,"bioessence碧歐斯": 228,"clarins克蘭詩": 97,"aromebywatsons": 314,"alterna": 270,"elizabetharden伊麗莎白雅頓": 306,"watsonsskin屈臣氏": 342,"nealsyardremedies尼爾氏香芬庭園": 300,"srbeauty": 107,"kryolan歌劇魅影": 164,"heme": 9,"loccitane歐舒丹": 160,"beautymate美肌之誌": 276,"divinia蒂芬妮亞": 102,"drhsieh達特醫": 208,"法國歐德瑪": 255,"goat": 188,"benefit": 304,"lorealparis巴黎萊雅": 137,"malingoetz": 217,"mori水漾膜麗": 260,"cleanclear可伶可俐": 243,"maybelline媚比琳": 291,"absolutenewyork絕色紐約": 249,"chicaychico": 105,"cnplaboratory": 174,"kpalette": 285,"dermaformula美肌醫生": 241,"tszjitsuei瓷肌萃": 69,"drjart": 57,"neom": 78,"renefurterer荷那法蕊": 145,"equilibra義貝拉": 236,"burberry": 245,"curel珂潤": 151,"rodial": 318,"olay歐蕾": 214,"zbyziva": 265,"toocoolforschool": 263,"nivea妮維雅": 25,"freshline": 235,"giorgioarmani亞曼尼": 141,"makeupforever": 176,"three": 287,"swissvita瑞士薇佳": 305,"becca": 86,"alkmene": 346,"myscheming我的心機": 154,"lamer海洋拉娜": 264,"jone": 329,"chapex喬沛詩": 40,"premier": 13,"decorte黛珂": 106,"sisley希思黎": 45,"nars": 213,"neuve惹我": 91,"garnier卡尼爾": 124,"marcjacobs": 352,"johnmastersorganics": 11,"uka": 73,"hikaru喜凱露": 192,"philosophy肌膚哲理": 309,"natracare": 38,"burtsbees小蜜蜂爺爺": 337,"espoir": 5,"himalaya喜瑪拉雅": 20,"bellabeauty": 103,"nacola": 284,"dhc": 167,"covermark": 17,"softymo絲芙蒂": 322,"sofina蘇菲娜": 152,"bioderma法國貝德瑪": 171,"targetprobywatsons": 193,"ele": 345,"prada": 128,"lauramercier蘿拉蜜思": 251,"fasio菲希歐": 365,"tommyhilfiger": 173,"loveways羅崴詩": 232,"orbis": 184,"mdmmd明洞國際": 185,"neutrogena露得清": 153,"memebox": 242,"versace凡賽斯": 357,"bifesta": 335,"drbronners布朗博士": 187,"chateaulabiotte": 211,"origins品木宣言": 294,"ghosttowash": 60,"muji無印良品": 39,"za": 224,"banilaco": 108,"derminstitute得因特": 269,"listwistea": 55,"skinadvanced": 196,"moroccanoil": 4,"bondiwash": 80,"integrate絕色魅癮": 181,"whiteformula自白肌": 172,"thefaceshop菲詩小舖": 100,"cetaphil舒特膚": 64,"becupidon邱比特": 66,"calvinklein": 34,"lovecode": 366,"azplaza": 129,"hopegirl": 156,"shiseido資生堂": 115,"byterry": 113,"bevyc妝前保養": 121,"laneige蘭芝": 46,"apieu": 200,"chanel香奈兒": 110,"petalfresh沛特斯": 41,"專科": 98,"darphin朵法": 238,"motives莫蒂膚": 361,"carmax小蜜媞": 70,"collagen": 303,"institutkariteparis巴黎乳油木": 104,"bionike": 140,"voodoo": 27,"jurlique茱莉蔻": 116,"albion艾倫比亞": 327,"sulwhasoo雪花秀": 330,"teapower茶寶": 282,"harmony": 349,"grainedepastel": 49,"drsatin": 222,"080": 111,"majolicamajorca戀愛魔鏡": 61,"俏佳人": 42,"mote": 67,"corsica科皙佳": 31,"point": 47,"avene雅漾": 58,"brand1028": 3,"locherber樂凱博": 358,"byredo": 364,"thailandbirds泰國雙燕": 283,"claires格麗": 144,"miumiu": 62,"benzac": 355,"chantecaille香緹卡": 247,"kbeauty": 54,"rebeccabonbon": 272,"ponpon澎澎": 293,"biore蜜妮": 367,"sweetheartbeauty甜心美妝": 175,"skinbiotec肌研生醫": 147,"dior迪奧": 178,"御泥坊": 79,"aatest測試": 360,"pauljoe": 195,"crabtreeevelyn瑰珀翠": 50,"chicchoc奇可俏可": 204,"lsy林三益": 299,"srichand喜簪": 310,"purepawpaw": 72,"johnsons嬌生": 230,"phisoderm菲蘇德美": 328,"conibeauty": 189,"naf": 321,"kose高絲": 210,"gatsby": 2,"奢華寶貝": 257,"cota": 226,"naruko": 274,"prettiean法國雅姿麗": 89,"frusirnana美膚娜娜": 19,"clarisonic科萊麗": 177,"numismed樂美思": 87,"西班牙babaria": 14,"dejavu": 131,"panatec沛莉緹": 223,"eyeko": 225,"aqualabel水之印": 203,"thesaem": 375,"evelom": 316,"mayskin優若美": 21,"aesop": 94,"aderma艾芙美": 130,"dermedic": 35,"sabon": 186,"guerlain嬌蘭": 56,"ipsa茵芙莎": 268,"moonshot": 331,"vaseline凡士林": 371,"ninaricci": 369,"tsaio上山採藥": 191,"lalique": 168,"aviva": 332,"bobbibrown芭比布朗": 81,"evian愛維養": 244,"evolu艾芙洛": 158,"yuskin悠斯晶": 266,"vdl": 311,"tsubaki思波綺": 132,"beautymaker": 340,"etvos": 289,"fancl": 138,"50惠": 92,"jericho": 317,"brand3m": 18,"drwu": 295,"innisfree": 90,"cezanne": 271,"bonvivant": 119,"rosyrosa": 292,"fititwhitia": 219,"solone": 323,"perlabella義貝拉": 96,"lb": 376,"beautybuffet天天美麗": 336,"sisterdiary姊妹日記": 239,"ernolaszlo奧倫納素": 334,"whoo后": 122,"aroa": 24,"revlis": 356,"bvlgari寶格麗": 77,"yourheart": 28,"stives聖艾芙": 262,"evita艾薇塔": 240,"jingcheng京城之霜": 159,"puresmile": 308,"mac": 101,"once": 142,"iope": 267,"vichy薇姿": 324,"laformule法國植萃合度": 71,"lululun": 362,"bourjois妙巴黎": 319,"larocheposay理膚寶水": 233,"forencos": 59,"melvita蜜葳特": 150,"saugella賽吉兒": 368,"misshana花娜小姐": 374,"toryburch": 258,"white": 88,"unt": 146,"givenchy紀梵希": 162,"cledepeaubeaute肌膚之鑰": 296,"ysl聖羅蘭": 343,"dcs": 197,"clearturn": 93,"thebodyshop美體小舖": 166,"hadalabo肌研": 1,"kissme奇士美": 302,"valmont法兒曼": 353,"ren": 43,"peripera": 326,"omorovicza": 218,"shuuemura植村秀": 99,"elemis": 22,"absolution": 44,"palmers帕瑪氏": 117,"beyond": 120,"ponds旁氏": 170,"biooil百洛": 118,"ayura東洋美學": 372,"ponyeffect": 370,"ibl依必朗": 149,"countrystream": 109,"biotherm碧兒泉": 229,"klorane蔻蘿蘭": 351,"lesmerveilleusesladuree": 125,"aprilskin": 95,"lpmediheal美迪惠爾": 286,"uno": 234,"innerskin": 51,"dove多芬": 139,"aloederma璦露德瑪": 68,"mistine": 348,"vancleefarpels梵克雅寶": 212,"purebeauty": 76,"neogence霓淨思": 127,"syrio": 320,"pinkgogirlhey蘋果肌女孩": 26,"philips飛利浦": 133,"reinachu日本蕾娜啾": 254,"drmorita": 36,"kiehls契爾氏": 179,"美舒律": 207,"grownalchemist": 53,"skii": 74,"kosecosmeport蔻絲魅寶": 65},
            'color':{"粉紅色": 9,"紫色": 8,"玫瑰·": 16,"大地色": 17,"淺棕色": 10,"酒紅色": 2,"棕色": 5,"健康膚色": 23,"黃色": 7,"綠色": 3,"橘色": 0,"黑色": 6,"莓紅": 20,"桃紅": 22,"藍色": 4,"明亮膚色": 14,"珊瑚": 21,"自然膚色": 15,"金色": 12,"透明": 19,"白皙膚色": 18,"紅色": 1,"香檳色": 13,"深棕色": 11},
            'price':{'貴':1,'便宜':2}
        }
        conflict = 0
        if prev_action!=None and ACTIONTABLE[prev_action].startswith('recommend_slot'):
            for tag in ['item','brand','color','effect']:
                if not ('recommend_slot_'+tag) in ACTIONTABLE[prev_action]: continue
                r = ACTIONTABLE[prev_action].replace('recommend_slot_'+tag+'_','')
                if self.state[SLOTPARA['item']]!=0: item = ITEMLIST[int(self.state[SLOTPARA['item']])]
                else: item = ''
                if tag=='effect':
                    if self.state[EFFECTPARA[r]]!=0: conflict = 1
                    elif item and not r in PRODUCT_EFFECT[item]: return 1
                    if (intent=='react' and isgood(parameters)): self.state[EFFECTPARA[r]] = 1
                else:
                    if tag=='brand':
                        if item and not r in PRODUCT_BRAND[item]: return 1
                    if self.state[SLOTPARA[tag]]!=0: conflict = 1
                    if (intent=='react' and isgood(parameters)): self.state[SLOTPARA[tag]] = entities[tag][r]
        else:
            for k,v in parameters.items():
                if v == None: continue
                if k in SLOTPARA:
                    if self.state[SLOTPARA[k]]==0: self.state[SLOTPARA[k]] = entities[k][v]
                elif k in EFFECTPARA:
                    if self.state[EFFECTPARA[k]]==0: self.state[EFFECTPARA[k]] = 1
        return conflict

    #### Skin Status ####
    # def update(self):
    #     print('(skin_update)',random.choice(SKINGREETINGS['greetings']))
    #     while True:
    #         userinput = input('>>> ')
    #         if userinput=='exit' or userinput=='exit()': break
    #         intent, parameters = intent_parser(userinput)
    #         if intent=='skinBad' or (intent=='react' and parameters['sentiment']=='抱怨'):
    #             for k,v in parameters.items():
    #                 if v!='': self.skinstatus[k]=v
    #             print('(skin_bad)',random.choice(SKINGREETINGS['bad']), random.choice(SKINGREETINGS['others']))
    #             continue
    #         else:
    #             print('(skin_ok)',random.choice(SKINGREETINGS['ok']))
    #             break
    #     return

    #### Update Blacklist and Preference ####
    def update_slotlist(self, slotlist):
        for k,v in slotlist.info.items():
            if v=='' or v==-1: continue
            # if self.slotlist.info[k]!='' and self.slotlist.info[k]!=-1: continue
            else: self.slotlist.info[k] = v
        for k,v in slotlist.effect.items():
            if v==0: continue
            self.slotlist.effect[k] = 1
        for k, v in slotlist.others.items():
            if v=='': continue
            else: self.slotlist.others[k]=v

        if slotlist.skin['skinType']!='': self.skintype = slotlist.skin['skinType']
        if slotlist.skin['skinProblem']!='': self.skinstatus[slotlist.skin['skinProblem']]=1
        pass
    def add_blacklist(self, slotlist):
        for k,v in slotlist.info.items():
            if v=='' or v==-1: continue
            if k=='sentiment' or k=='where': continue       # 之後要把where放進去
            if v not in self.blacklist[k]: self.blacklist[k].append(v)
        pass
    def add_preference(self, slotlist):
        pass
