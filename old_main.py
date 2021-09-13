#### 2018.06.22 YourRS PGDM Work on makeup ####
import json
from lib.tools import Database

def intent_parser(userinput):
    intent = 'search_item'
    parameters = {'item':'口紅','brand':'1028'}
    return intent, parameters

def arg_parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('--pdb', default='data/product_dict_effect.json', type=str, help='file of product list')
    parser.add_argument('--debug', action='store_true',help='open debug mode')
    parser.add_argument('--online', action='store_true',help='open online mode')
	args = parser.parse_args()
	return args

class PostHandler(BaseHTTPRequestHandler):
	""" Server Connection """
	def do_POST(self):	# Parse the form data posted
		self.data_string = self.rfile.read(int(self.headers['Content-Length']))
		self.send_response(200)
		self.wfile.write('Content-Type : data/json\n'.encode("utf-8"))
		self.end_headers()
		data = json.loads(self.data_string)
		print ("{}".format(data))
		userinput = data['result']['resolvedQuery']
		intent = data['result']['metadata']['intentName']
		userId = data['sessionId']
		parameters = data['result']['parameters']
		response = main(userId, userinput, intent, parameters)
		print(response)
		response = json.dumps(response).encode("utf-8")
		self.wfile.write(response)
		return

class User(object):
	"""docstring for User"""
	def __init__(self, userId, bot):
		super(User, self).__init__()
		self.chatbot = MakeupBot(CHAT)
		self.userStatus = UserStatus(userId, db)
	def empty(self):
		self.chatbot.empty()
		self.userStatus.empty()
		return 'OK'

def needInsertSlot(intent): return intent not in ['thank','greeting','goodbye','noidea']
def main(userId, userinput, intent, parameters):
	try: user = users[userId]
	except KeyError: users[userId] = User(userId, bot)
	user = users[userId]

	if userinput=='reset':
		print('Reset session',userId)
		return user.empty()

	print('(intention: '+intent+')')
	# slotlist = SlotList()
	# if needInsertSlot(intent): slotlist.insert(intent, parameters, user.chatbot.askslot)
	# if DEBUG: slotlist.printslot()

	# res = action(db, user.chatbot, user.userStatus, userinput, intent, slotlist)
	# response = NLG(db, res, bot)

	if ONLINE:
		if res.ELEMENT or res.QUICK_REPLIES:
			return {"data": response}
		else:
			return {"speech":response, "displayText":response}
	else: return response


if __name__ == '__main__':
	args = arg_parse()
	DEBUG = args.debug
	ONLINE = args.online

	if DEBUG: print('DEBUG is opened...')
	db = Database(filename=arg.pdb)
	# db.load()

	# Server
	if ONLINE:
		from http.server import HTTPServer
		server = HTTPServer(('0.0.0.0', 9188), PostHandler)
		print('Starting server, use <Ctrl-C> to stop\n\n')
		server.serve_forever()
	else:
		while True:
			userinput = input('>>> ')
			if userinput=='exit': break
			intent, parameters = intent_parser(userinput)
			print(main(0, userinput, intent, parameters))
