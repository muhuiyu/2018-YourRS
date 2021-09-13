# coding: utf8
import random
from lib.parameters import *

# 'request_item': 8, 'request_brand':9, 'request_color':10, 'request_price':11,
# 'request_effect': 12, 'request_picture':13, 'request_link':14, 'request_comment': 15,

# recommend_slot for item, brand, color, effect: 510
# answer: index 0, recommend_item: index 1
def gen_semantic(intent):
    sframe = []
    if intent=='greeting':
        sframe = random.choice([['安安'],['你好'],['嗨我是小M']])
    elif intent=='goodbye':
        sframe = random.choice([['掰掰'],['再見'],['掰'],['ㄅㄅ'],[':)'],['掰餔'],['再會噢'],['珍重再見嗚嗚QQ'],['要記得回來看我噢！']])
    elif intent=='recommend_item':
        sframe = ['要不要','試試','SLOT_BRAND','的','SLOT_NAME','？','價錢','約','在','SLOT_PRICE','元','（','SLOT_VOLUME','）','左右','～','這個','商品','SLOT_INFO']
    elif intent.startswith('recommend_slot_item'):
        item = intent.replace('recommend_slot_item_','')
        sframe = ['要不要','試試',item,'呢','？']
    elif intent.startswith('recommend_slot_brand'):
        brand = intent.replace('recommend_slot_brand_','')
        sframe = ['要不要','試試',brand,'的','產品','呢','？']
    elif intent.startswith('recommend_slot_color'):
        color = intent.replace('recommend_slot_color_','')
        sframe = [color,'你','覺得','如何','呢','？']
    elif intent.startswith('recommend_slot_effect'):
        effect = intent.replace('recommend_slot_effect_','')
        sframe = ['有個',effect,'效果','怎麼樣','呢','？']
    elif intent=='recommend_slot_makeup':
        sframe = ['想要','試試','SLOT_SLOT','的','妝容','嗎','？']
    elif intent=='ask_slot_item':
        sframe = ['請問','有','想要','找','的','物品','嗎','？']
    elif intent=='ask_slot_brand':
        sframe = ['請問','有','想要','找','的','品牌','嗎','？']
    elif intent=='ask_slot_color':
        sframe = ['請問','有','想要','找','的','顏色','嗎','？']
    elif intent=='ask_slot_price':
        sframe = ['請問','預算','大概','是','多少','呢']
    elif intent=='ask_slot_effect':
        sframe = ['請問','有','希望','產品','能有','哪些','效果','嗎','？']
    elif intent=='ask_skinProblem':
        sframe = ['噢','拍拍','你','QQ',' ','請問','還有','什麼','其他','症狀','嗎','？']
    elif intent=='del_slot':
        sframe = ['有','一點','找','不太','到','資訊','欸','，','不然','我們','先','不要','考慮','SLOT_SLOT','好嗎？']
    elif intent=='youAreWelcome':
        sframe = ['不','客氣','噢～']
    elif intent=='ok':
        sframe = ['好','噢','～']

    # 修改這邊的回話，之後放上評價or 評論or blog 文章
    elif 'praise' in intent:
        if intent=='praise_item': sframe = ['果真','是個','有','品味','的','水水','呢','>////< ','這款商品','SLOT_COMMENT']
        elif intent=='praise_makeup': sframe = ['您','的','選擇','真的','非常','有','眼光','呢','>///<']
        else: sframe = ['您','的','選擇','真的','非常','有','眼光','呢','>///<']
    elif intent=='chat':
        # if (self.chatmode): res = '(chat) '+str(self.bot.get_response(s))
        sframe = random.choice([['是噢哈哈'],['不要一直跟我聊天啦XD'],['咦真的嗎？！'],['這個我不知道欸XD'],['嗚嗚我不知道要說什麼了QQ'],['這個你要不要去問MuYu？']])
    elif intent=='answer':
        sframe = ['是','這樣這樣','的','噢']
    elif intent=='persuade':
        sframe = ['但','我','覺得','這個','產品','挺','不錯','的','，','並且有符合你','SLOT_LIST_USER_REQUSET','的','要求','啊～']

    elif intent=='answer_effect':
        sframe = ['SLOT_LIST_EFFECT_COMMENT']
    elif intent=='answer_makeup':
        try: sframe = [res.recommend[0]['item'][res.info['item']][res.askslot],'\n','我','個人','覺得','她','用的','產品','效果','還','不錯','，','也許','可以','入手','一隻']      # 待改
        except KeyError: sframe = ['抱歉','這篇','文章','沒有','這個','資料','噢','QQ']
    elif intent=='answer_article':
        if res.recommend[0][res.askslot]!=None and res.recommend[0][res.askslot]!='': sframe = [nameslot[res.askslot]]
        else: sframe = ['抱歉','！','文章','資料','裡','沒有','這','方面','的','資訊','噢','QQ']
    elif intent=='unknown':
        sframe = random.choice([['你在工三小XD'],['蝦毀OAO'],['聽不懂啦嗚嗚嗚'],['えっ？！'],['問號問號'],['我聽不懂欸你去問MuYu好了']])
    elif intent=='ask_why':
        sframe = random.choice([['為什麼不喜歡呢？'],['是哪邊不合您的要求呢？'],['你覺得哪裡不夠好呢？'],['為什麼，他錯了ㄇ？']])
    elif intent=='selfInfo':
        if res.askslot=='name': sframe = ['你好我乃超級厲害的美妝機器人小M是也！我可以教你怎麼化妝，也可以推薦最厲害又適合你的美妝產品噢 O_<']
        elif res.askslot=='ability': sframe = ['我可以教你怎麼化妝、除去臉上的瑕疵，還可以推薦給你最厲害又適合你的美妝產品噢！']
        elif res.askslot=='connect': sframe = ['我的電話是2882-5252，晚上八點以後都有空O_<']
        elif res.askslot=='looks': sframe = ['自己在表特版找小M就可以看到了噢ㄏㄏ']
        elif res.askslot=='hobby': sframe = ['小M平常最喜歡練習化妝了，你要給小M當實驗品嗎嘿嘿嘿...']
        elif res.askslot=='age': sframe = ['年齡是女人的秘密噢 >///<']
        else: sframe = random.choice([['；）'], ['(ㆁᴗㆁ✿)'], ['（＾ｖ＾）'], ['(≖ᴗ≖✿)'], ['(✪‿✪)ノ']])
    return sframe

def nlg(action, prediction):
    senmantic = gen_semantic(ACTIONTABLE[action])
    return ACTIONTABLE[action],''.join(senmantic)
