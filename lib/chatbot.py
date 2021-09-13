import random

from libs.lists import EFFECTITEMLIST
from libs.dialog import HELLOLIST
from libs.dialog import SELFINTRO
from libs.dialog import SKINGREETINGS
from libs.res import Res
from chatterbot import ChatBot

class MakeupBot(object):
	"""docstring for MakeupBot"""
	def __init__(self, chatmode):
		super(MakeupBot, self).__init__()
		self.chatmode = chatmode
		self.intent = ''
		self.lastIntent = ''
		self.askslot = ''
		self.candidateList = []
		self.candidateList_article = []
		self.recommendDict = {
			'recommend_item':None,
			'recommend_makeup':None,
			'recommend_slot':('',''),
			'recommend_article':None
		}

	def empty(self):
		self.intent = ''
		self.lastIntent = ''
		self.askslot = ''
		self.candidateList = []
		self.recommendDict = {'recommend_item':None, 'recommend_makeup':None, 'recommend_slot':('','')}
		pass

	def recommend(self, intent):
		if 'item' in intent: return self.recommend_item()
		elif 'makeup' in intent: return self.recommend_makeup()
		return

	def recommend_makeup(self):
		makeup = random.choice(self.candidateList)
		res = Res(ELEMENT=True, intent='recommend_makeup', recommend=[makeup])

		self.recommendDict['recommend_makeup'] = [makeup]
		self.intent = 'recommend_makeup'
		self.lastIntent = 'recommend_makeup'
		return res

	def recommend_item(self):
		prob = random.uniform(0, 1)
		if prob < 0.9:
			product = random.choice(self.candidateList)
			self.recommendDict['recommend_item'] = [product]
			res = Res(intent='recommend_item', recommend=self.recommendDict['recommend_item'])
		else:
			if len(self.candidateList)>3: self.recommendDict['recommend_item'] = random.sample(self.candidateList, 3)
			else: self.recommendDict['recommend_item'] = self.candidateList
			res = Res(ELEMENT=True, intent='recommend_item', recommend=self.recommendDict['recommend_item'])

		self.intent = 'recommend_item'	# here 可能要再調整 QQ
		self.lastIntent = 'recommend_item'	# here 可能要再調整 QQ
		return res

	def recommend_slot(self, slotlist, intent):
		if 'item' in intent:
			askslot, slot = choose_add_slot(slotlist.info, slotlist.effect)
			intent = 'recommend_item'
		elif 'makeup' in intent:
			askslot, slot = choose_add_slot_makeup(slotlist.others)
			intent = 'recommend_makeup'

		# 問了一些不能用的askslot，就直接推薦
		if askslot=='pricelowerbound' or askslot=='priceupperbound' or askslot==None or askslot=='slot':
			c = random.choice(self.candidateList)
			self.recommendDict[intent] = [c]
			self.intent = intent
			self.lastIntent = intent
			if intent=='recommend_makeup': res = Res(intent=intent, recommend=[c], ELEMENT=True)
			else: res = Res(intent=intent, recommend=[c])
		else:
			while True:		# 等到顏色都填完就可以了QQ
				c = random.choice(self.candidateList)
				slot = c[askslot]
				if slot!=None and slot!='' and slot!=['']: break
			# for those whose slot is a list
			if askslot=='item' or 'makeup' in intent: slot=random.choice(slot)
			self.recommendDict['recommend_slot'] = (askslot, slot)
			self.intent = 'recommend_slot'
			self.lastIntent = 'recommend_slot'
			if 'item' in intent: res = Res(intent='recommend_slot_item', recommend_slot=slot)
			else: res = Res(intent='recommend_slot_makeup', recommend_slot=slot)
		return res

	def recommend_article(self, slotlist, intent):
		# print(len(self.candidateList_article))
		if intent=='skinProblem':
			article = random.choice(self.candidateList_article)
			self.recommendDict['recommend_article'] = [article]
			res = Res(ELEMENT=True, intent='recommend_article', recommend=[article])
		self.intent = 'recommend_article'
		self.lastIntent = 'recommend_article'
		return res

	def ask_slot(self, slotlist, intent):
		if 'item' in intent or intent=='ask_property':
			self.askslot, slot = choose_add_slot(slotlist.info, slotlist.effect)
			res = Res(intent='ask_slot', askslot=self.askslot)
		elif 'makeup' in intent:
			self.askslot, slot = choose_add_slot_makeup(slotlist.others)
			need_quick_replies = False
			if (self.askslot in ['style', 'occasion']):
				need_quick_replies = True
			res = Res(intent='ask_slot', askslot=self.askslot, QUICK_REPLIES=need_quick_replies)
		elif 'skin' in intent:
			self.askslot = 'slot'
			res = Res(intent='ask_skinProblem')
		self.lastIntent = 'ask_slot'
		return res

	def del_slot(self, slotlist, intent):
		delslot, slot = choose_del_slot(slotlist.info)
		res = Res(intent='del_slot', askslot=delslot)
		self.lastIntent = 'del_slot'
		return res

	def answer(self, candidateList, askslot, effect=None):
		if askslot=='pic': res = Res(ELEMENT=True, intent='answer', recommend=candidateList, askslot='pic')
		elif effect!=None: res = Res(intent='answer_effect', recommend=candidateList, askslot=askslot, effect=effect)	# ask item effect
		else: res = Res(intent='answer', recommend=candidateList, askslot=askslot)
		self.lastIntent = 'answer'
		return res

	def answer_article(self, candidateList, slotlist, askslot):
		res = Res(intent='answer_makeup',recommend=candidateList, askslot=askslot, info=slotlist.info)
		self.lastIntent = 'answer_article'
		return res

	def answer_makeup(self, candidateList, slotlist, askslot):
		if askslot=='pic': res = Res(ELEMENT=True, intent='answer_makeup', recommend=candidateList, askslot='pic')
		elif askslot=='info': res = Res(ELEMENT=True, intent='answer_makeup', recommend=candidateList, askslot='info', info=slotlist.info)
		else: res = Res(intent='answer_makeup',recommend=candidateList, askslot=askslot, info=slotlist.info)
		self.lastIntent = 'answer'
		return res

	def praise(self):
		if self.intent=='recommend_item': res = Res(intent='praise_item', recommend=self.recommendDict[self.intent])
		elif self.intent=='recommend_makeup': res = Res(intent='praise_makeup', recommend=self.recommendDict[self.intent])
		else: res = Res(intent='praise', recommend=self.recommendDict[self.intent])
		self.lastIntent = 'praise'
		return res

	def persuade(self, userStatus):
		res = Res(intent='persuade', recommend=self.recommendDict[self.intent], userrequest=userStatus.slotlist)
		return res

	def chat(self, s):
		res = Res(intent='chat', s=s)
		self.lastIntent = 'chat'
		return res

	# def chatbyslot(self, slotlist):
	# 	#### TO-DO: 可以做什麼功能 ####
	# 	res = '最近又多出了很多新的'+slotlist.info['item']+'呢～'
	# 	print('(chat)', res)
	# 	return res

	def unknown(self):
		res = Res(intent='unknown')
		return res

	def greeting(self):
		res = Res(intent='greeting')
		self.lastIntent = 'greeting'
		return res

	def selfInfo(self, query):
		need_quick_replies = False
		if query in ['name', 'ability']:
			need_quick_replies = True
		res = Res(intent='selfInfo', askslot=query, QUICK_REPLIES=need_quick_replies)
		return res

	def ask_why(self):
		res = Res(intent='ask_why')
		self.lastIntent = 'ask_why'
		return res

	def ok(self):
		res = Res(intent='ok')
		self.lastIntent = 'ok'
		return res

	def goodbye(self):
		res = Res(intent='goodbye')
		self.lastIntent = 'goodbye'
		return res

	def youAreWelcome(self):
		res = Res(intent='youAreWelcome')
		return res

def searchbyInfo(candidateList, info):
	for identity in ['brand', 'color', 'name']:
		if info[identity]=='': continue
		for candidate in candidateList:
			if candidate[identity]==info[identity] or candidate[identity] in info[identity]: return candidate
	return

def whereInt(where, n):
	whereChineseList = {'第一個':0, '第二個':1, '第三個':2, '最後一個':n-1}
	return whereChineseList[where]

def choose_add_effect(item, effectlist):
	while True:
		effect = random.choice(EFFECTITEMLIST[item])
		if effectlist[effect]!=0: return effect


def related(slot, item):
	if slot=='color':
		return item in ['妝前打底','指甲油','BB霜', '妝前打底', '眉彩', '腮紅修容', '唇彩唇蜜', '氣墊粉餅', '唇膏', '粉餅', '眼影', '眼線', 'CC霜', '粉霜', '唇筆', '粉底液', '遮瑕', '粉條']
	return True

def all_filled(info, add_list):
	for slot in add_list:
		if slot=='slot': continue
		if info[slot]=='' or info[slot]==-1: return False
	return True

def choose_add_slot_makeup(others):
	slotlist = ['occasion','style','slot']
	slotChinese = {'occasion':'場合','style':'風格','slot':'其他要求'}
	while True:
		askslot = random.choice(slotlist)
		if askslot=='slot': break
		if others[askslot]=='': break
	return askslot, slotChinese[askslot]

###### TO-DO: 要改成有智慧的方式刪掉 #### 目前先暫時使用random的 ###
def choose_add_slot(info, effectlist):
	slotChinese = {'item':'商品','path':'購買通路','brand':'品牌','color':'顏色','effect':'效用','pricelowerbound':'價格下限（至少多少錢）','priceupperbound':'價格上限（不超過多少錢）', 'slot':'其他要求'}
	add_list = ['slot','path','brand','color','pricelowerbound','priceupperbound'] 	# 晚一點加入effect
	slotname = ''

	if info['item']=='' and info['name']=='': return 'item',slotChinese['item']	# 沒有商品就先問item
	while True:
		if all_filled(info, add_list): return 'slot', slotChinese['slot']
		slot = random.choice(add_list)
		# if slot=='effect' and info.item!='': return slot, choose_add_effect(info.item, effectlist)
		if slot=='slot': return slot, slotChinese[slot]
		if info[slot]!='' and info[slot]!=-1: continue
		elif not related(slot, info['item']): continue
		elif slot=='path' and info['brand']!='': continue		# 特殊狀況，已經有品牌就不用問path了
		else: return slot, slotChinese[slot]
	return slot, slotname

def choose_del_slot(info):
	del_list = []
	for k,v in info:
		if v==0 or v=='': continue
		del_list.append(k)
	delslot = random.choice(del_list)
	return delslot, slotChinese[delslot]
