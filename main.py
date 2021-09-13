### 2018.06.28 YourRS PGDM Work on makeup ###
### offline version ###
# coding: utf8
import json, argparse, torch, random
from http.server import BaseHTTPRequestHandler
from lib.nlu import *
from lib.nlg import *
from lib.tools import *
from lib.action import *
from lib.modules import *
from lib.parameters import *

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--product_db', default='data/product_dict_effect.json', type=str, help='file of product list')
    parser.add_argument('--entity_file', default='data/clean_entity_info.json', type=str, help='file of product list')
    parser.add_argument('--reversed_entity_file', default='data/reversed_clean_entity_info.json', type=str, help='file of product list')
    parser.add_argument('--intent_file', default='data/intent_pattern.json', type=str, help='file of product list')
    parser.add_argument('--epochs', default=1000, type=int, help='training epochs')
    parser.add_argument('--debug', action='store_true',help='open debug mode')
    parser.add_argument('--online', action='store_true',help='open online mode')
    parser.add_argument('--train', action='store_true',help='open online mode')
    return parser.parse_args()

def needInsertSlot(intent): return intent not in ['thank','greeting','goodbye','noidea']
def main(uid, userinput):
    print('>>>',userinput)
    try: user = users[uid]
    except KeyError:
        users[uid] = User(uid)
        user = users[uid]
    if userinput=='reset':
        print('Reset session {}, user #turn = {}'.format(uid, user.turn))
        return user.empty()

    user.turn += 1
    # print(convertnum(userinput), str(chinese2num(find_chinese_num(userinput))))
    intent, parameters = intentClassifier.Match(userinput)
    conflict = user.update(intent, parameters, dialogManager.prev_action)
    done = dialogManager.update(intent, parameters, user.state, user.turn, conflict)
    if done:
        action = 13         # 13
        prediction = 1      # 還沒接產品
        user.empty()
    else: action, prediction = dialogManager.action(db, user.state, user.turn)
    response = nlg(action, prediction)
    print('intent:{}, parameters:{}\nstate:{}, turn: {}, \naction:{}, prediction:{}'.format(intent, parameters, user.state, user.turn, action, prediction))
    return response

users = {}

if __name__ == '__main__':
    args = arg_parse()
    DEBUG = args.debug
    if DEBUG: print('DEBUG is opened...')
    db = Database(filename=args.product_db)
    intentClassifier = IntentClassifier(args.entity_file, args.reversed_entity_file, args.intent_file)
    dialogManager = DialogManager()
    dialogManager.policy = torch.load('model')
    # dialogManager.policy_out = torch.load('policy_out')

    # for my training
    if args.train:
        for i in range(args.epochs):
            print('=========',i)
            userinput = random.choice(['幫我找za的粉餅','我想找za的粉底液','有蘭芝的口紅嗎','有什麼好的香水','有沒有面膜','有沒有推薦的眼線筆','有推薦的眼影嗎','給我個明星商品','想找蜜粉'])
            status, response = main(0, userinput.lower().replace(' ',''))
            print(status, response)
            while status!='ok':
                userinput = random.choice(['好啊','不要'])
                status, response = main(0, userinput.lower().replace(' ',''))
                print(status, response)
            print('\n\nAverage Rewards:{}'.format(dialogManager.sum_reward/(i+1)))
            print('=========',)
        print('\n\nAverage Rewards:{}'.format(dialogManager.sum_reward/args.epochs))
        torch.save(dialogManager.policy, 'model')
    # user use
    else:
        while True:
            userinput = input('>>> ')
            if userinput=='exit':
                torch.save(dialogManager.policy, 'model')
                break
            print(main(0, userinput.lower().replace(' ','')))
