import json, random, argparse

from libs.chatbot import MakeupBot
from libs.slotlist import SlotList
from libs.userStatus import UserStatus
from libs.database import Database
from libs.tools import *

SEARCH_ITEM_N = 3
SEARCH_MAKEUP_N = 3
SEARCH_ARTICLE_N = 2
ASK_PROPERTY_N= 1
RANDOM_N = 1
LIKE = 1
HATE = 0

RECOMMEND = 1
ASK_SLOT = 2
RECOMMEND_SLOT = 3

def update_and_search(db, intent, userStatus, slotlist, sentiment=LIKE):
	candidateList = []
	if intent in ['search_item','inform_item','skinProblem_item']:
		userStatus.score.update(db.itemList, slotlist, userStatus, sentiment, target='item')
		candidateList = search_candidates(userStatus.score.item_score, db.itemList, SEARCH_ITEM_N)
	elif intent=='search_makeup' or intent=='inform_makeup':
		userStatus.score.update(db.makeupList, slotlist, userStatus, sentiment, target='makeup')
		candidateList = search_candidates(userStatus.score.makeup_score, db.makeupList, SEARCH_MAKEUP_N)
	elif intent=='random_item': candidateList = search_candidates(None, db.itemList, RANDOM_N, RANDOM=1)
	elif intent=='random_makeup': candidateList = search_candidates(None, db.makeupList, RANDOM_N, RANDOM=1)
	elif intent=='skinProblem_article':
		userStatus.score.update(db.articleList, slotlist, userStatus, sentiment, target='article')
		candidateList = search_candidates(userStatus.score.article_score, db.articleList, SEARCH_ARTICLE_N)
	else: print('unknown')

	userStatus.update_slotlist(slotlist)
	print('----目前找到', len(candidateList),'個商品----')
	#print('\n'.join([str((i+1, c['name'], c['spec'])) for i, c in enumerate(candidateList)]))
	#print('\n'.join([str((i+1, c['name'], c['style'], c['occasion'])) for i, c in enumerate(candidateList)]))
	return candidateList

def candidate_action(chatbot, intent, n, slotlist, action=0):
	if len(chatbot.candidateList)<=n and len(chatbot.candidateList)!=0:
		res = chatbot.recommend(intent)
	else:
		if action==RECOMMEND: res = chatbot.recommend(intent)
		elif action==ASK_SLOT: res = chatbot.ask_slot(slotlist, intent)
		elif action==RECOMMEND_SLOT: res = chatbot.recommend_slot(slotlist, intent)
		else: res = chatbot.recommend_slot(slotlist, intent)
		# else:
			# prob = random.uniform(0, 1)
			# print('prob = ',prob)
			# if prob < 0.5: res = chatbot.ask_slot(slotlist, intent)
			# elif prob < 0.75: res = chatbot.recommend_slot(slotlist, intent)
			# else: res = chatbot.recommend(intent)
			# else: res = chatbot.chatbyslot(slotlist)
	return res

## 找到符合info要求的產品 ##
def search_in_list(candidateList, info):
	candidates = []
	for k,v in info.items():
		if k in ['where','sentiment']: continue
		if v=='' or v==-1: continue
		for candidate in candidateList:
			if candidate[k]==v: candidates.append(candidate)
	return candidates

def search_candidates(scorelist, dbList, n, RANDOM=0):
	candidateList = []
	if RANDOM:
		random_noList = random.sample(dbList.keys(), n)
		for no in random_noList: candidateList.append(dbList[no])
		return candidateList
	num = 0
	sorted_list = sorted(scorelist, key=scorelist.get, reverse=True)
	while num<len(sorted_list)-1 and scorelist[sorted_list[num]]==scorelist[sorted_list[num+1]]: num+=1
	for i in range(num+1): candidateList.append(dbList[sorted_list[i]])
	return candidateList

################################# Actions ###################################
#                                                                           #
#                                                                           #
#############################################################################

def inform(db, userStatus, chatbot, slotlist):
	sentiment = isLike(slotlist.info['sentiment'])
	if chatbot.intent!='': slotlist.re_organize(chatbot.intent, chatbot.recommendDict[chatbot.intent], userStatus.slotlist)
	if userStatus.intent in ['search_item','search_makeup']: domain = userStatus.intent
	else: domain = slotlist.find_domain()   # inform_domain = inform_items or inform_makeup
	chatbot.candidateList = update_and_search(db, domain, userStatus, slotlist, sentiment=sentiment)
	res = candidate_action(chatbot, domain, SEARCH_ITEM_N, userStatus.slotlist)
	chatbot.recommendDict['recommend_slot']=('','')
	return res

def search_item(db, userStatus, chatbot, slotlist):
	if userStatus.intent=='search_item' and slotlist.nothingRequired(): domain = 'random_item'
	else: domain = 'search_item'
	chatbot.candidateList = update_and_search(db, domain, userStatus, slotlist, sentiment=LIKE)
	return candidate_action(chatbot, domain, SEARCH_ITEM_N, userStatus.slotlist)

def ask_property(db, userStatus, chatbot, slotlist):
	if chatbot.intent=='recommend_item' and len(chatbot.recommendDict[chatbot.intent])==1:  # ask chatbot-recommended item
		#### TO-DO: 需要確認是不是在問現在的東西或是歪樓了 ####
		if slotlist.effect_used:
			effect = slotlist.get_used_effect()
			return chatbot.answer(chatbot.recommendDict[chatbot.intent], slotlist.ask, effect=effect)
		else: return chatbot.answer(chatbot.recommendDict[chatbot.intent], slotlist.ask)

	elif chatbot.intent=='recommend_makeup':
		return chatbot.answer_makeup(chatbot.recommendDict[chatbot.intent], slotlist, slotlist.ask)

	elif 'recommend_slot' in chatbot.lastIntent:  # 你要kate嗎？kate的眼影大概有哪些顏色啊
		slotlist.assign_slot_value(chatbot.recommendDict['recommend_slot'][0], chatbot.recommendDict['recommend_slot'][1])
		candidateList = update_and_search(db, 'search_item', userStatus, slotlist, sentiment=LIKE)
		return chatbot.answer(candidateList, slotlist.ask)

	elif chatbot.intent=='recommend_article':
		return chatbot.answer_article(chatbot.recommendDict[chatbot.intent], slotlist, slotlist.ask)

	else: # 需要處理：某某牌子的眼影好用嗎這種分類 QQ, ps.有一定的機率會另外推薦
		if len(chatbot.candidateList)!=0:   # Search in current list FIRST
			candidateList = search_in_list(chatbot.candidateList, slotlist.info)
			if len(candidateList)!=0: return chatbot.answer(candidateList, slotlist.ask)
		chatbot.candidateList = update_and_search(db, 'search_item', userStatus, slotlist, sentiment=LIKE)
		candidateList = chatbot.candidateList
		return chatbot.answer(candidateList, slotlist.ask)

def search_makeup(db, userStatus, chatbot, slotlist):
	chatbot.candidateList = update_and_search(db, 'search_makeup', userStatus, slotlist, sentiment=LIKE)
	return candidate_action(chatbot, 'search_makeup', SEARCH_MAKEUP_N, userStatus.slotlist)

# def makeup_property(db, userStatus, chatbot, slotlist):
# 	return chatbot.answer_makeup(chatbot.recommendDict[chatbot.intent], slotlist, slotlist.ask)

def help_decision():
	pass

def react(db, userStatus, chatbot, slotlist, userinput):
	sentiment = isLike(slotlist.info['sentiment'])
	if chatbot.intent=='recommend_item' or chatbot.intent=='recommend_makeup':
		if sentiment:
			return chatbot.praise() # chatbot.praise(chatbot.recommendDict[chatbot.intent])
			# chatbot.check_init()  # 是否要開啟新的conversation了呢
		else: return chatbot.ask_why()

	elif 'recommend_slot' in chatbot.intent:
		print('In recommend slot for react:')
		print(chatbot.recommendDict['recommend_slot'])

		slotlist.assign_slot_value(chatbot.recommendDict['recommend_slot'][0], chatbot.recommendDict['recommend_slot'][1])
		chatbot.candidateList = update_and_search(db, userStatus.intent, userStatus, slotlist, sentiment=sentiment)

		chatbot.recommendDict['recommend_slot']=('','')
		# N 可以改一下嗚嗚，依據makeup or item
		return candidate_action(chatbot, userStatus.intent, SEARCH_ITEM_N, userStatus.slotlist)
	elif userStatus.intent=='': return chatbot.chat(userinput)
	else: return

def choose(db, chatbot, slotlist):
	if slotlist.info['where']=='now': i=0
	else: i = whereInt(slotlist.info['where'],len(chatbot.recommendDict[chatbot.intent]))
	recommendDict[chatbot.intent] = [chatbot.recommendDict[chatbot.intent][i]]
	return chatbot.praise()

def noidea(db, userStatus, chatbot):
	if chatbot.lastIntent=='ask_slot':
		if chatbot.askslot=='slot':
			if userStatus.intent=='search_item': chatbot.candidateList = search_candidates(userStatus.score.item_score, db.itemList, SEARCH_ITEM_N)
			elif userStatus.intent=='search_makeup': chatbot.candidateList = search_candidates(userStatus.score.makeup_score, db.makeupList, SEARCH_MAKEUP_N)
			elif userStatus.intent=='search_article':
				chatbot.candidateList = search_candidates(userStatus.score.article_score, db.articleList, SEARCH_ARTICLE_N)
			return candidate_action(chatbot, userStatus.intent, SEARCH_ITEM_N, userStatus.slotlist, action=RECOMMEND)
		else:
			userStatus.slotlist.assign_slot_value(chatbot.askslot, 'NOIDEA')    # set askslot as NOIDEA
			return candidate_action(chatbot, userStatus.intent, SEARCH_ITEM_N, userStatus.slotlist)
	# elif chatbot.lastIntent=='recommend_slot':
	# elif chatbot.lastIntent=='recommend_item':
		# if len(chatbot.recommendDict['recommend_item']>1): chatbot.recommend(intent)
		# 強力推銷
		# return

def else_recommend(db, userStatus, chatbot, slotlist):
	if len(chatbot.candidateList)>1:
		chatbot.candidateList.remove(chatbot.recommendDict[chatbot.intent][0])
		chatbot.recommendDict[chatbot.intent] = [random.choice(chatbot.candidateList)]
		return chatbot.recommend(userStatus.intent)
	else: return chatbot.persuade(userStatus)

##### TO-DO: 加上items recommend #########
def skinbad(db, userStatus, chatbot, slotlist):
	prob = random.uniform(0, 1)
	if prob < 0.7 :
		chatbot.candidateList_article = update_and_search(db, 'skinProblem_article', userStatus, slotlist, sentiment=LIKE)
		return chatbot.recommend_article(slotlist, 'skinProblem') # 推薦文章解決
	else:
		chatbot.candidateList = update_and_search(db, 'skinProblem_item', userStatus, slotlist, sentiment=LIKE)
		return chatbot.recommend('recommend_item') # 推薦產品解決
	# elif prob < 0.75: res = chatbot.recommend_slot(slotlist, 'search_item')
	# elif prob < 0.98: res = chatbot.recommend(intent)
	# else: res = chatbot.ask_slot(slotlist, 'skinProblem')
	return res

def action(db, userinput, intent, slotlist):
	# if intent in ['search_item', 'search_makeup', 'ask_property'] and userStatus.intent=='': userStatus.intent = intent
    #
	# # candidate_n = candidateNumber(userStatus)
	# # print(userStatus.slotlist.info)
    #
	# if intent=='goodbye': return chatbot.goodbye()
	# elif intent in ['unknown', 'chat']: return chatbot.chat(userinput)      # chatbot.unknown()
	# elif intent=='greeting': return chatbot.greeting()
	# elif intent=='thanks': return chatbot.youAreWelcome()
	# elif intent=='aboutYou': return chatbot.selfInfo(slotlist.ask)
    #
	# elif intent=='inform': return inform(db, userStatus, chatbot, slotlist)
	# elif intent=='search_item': return search_item(db, userStatus, chatbot, slotlist)
	# elif intent=='ask_property': return ask_property(db, userStatus, chatbot, slotlist)
	# elif intent=='search_makeup': return search_makeup(db, userStatus, chatbot, slotlist)
	# # elif intent=='makeup_property': return makeup_property(db, userStatus, chatbot, slotlist)
	# elif intent=='help_decision': return help_decision()
    #
	# #### TO-DO: makeup_property ####
	# elif intent=='react' or intent=='confirm': return react(db, userStatus, chatbot, slotlist, userinput)
	# elif intent=='choose': return choose(db, chatbot, slotlist)
	# elif intent=='noidea': return noidea(db, userStatus, chatbot)
    #
	# #### TO-DO ####
	# elif intent=='skinBad': return skinbad(db, userStatus, chatbot, slotlist)
	# elif intent=='else_recommend': return else_recommend(db, userStatus, chatbot, slotlist)
	# else: return
