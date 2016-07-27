import tornado.websocket
import redis
import json
from pprint import pprint
import threading

import requests
requests.packages.urllib3.disable_warnings()

# redis client gets used in two Server Handles, so we will just share it
redis_client = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)

HOSTNAME_MAPPINGS = {
	'SF': 'san francisco',
	'Dallas': 'dallas',
	'LA': 'los angeles',
	'Miami': 'miami',
	'Houston': 'houston',
	'Tampa': 'tampa',
	'NY': 'new york',
	'Chicago': 'chicago'
}

INTERFACE_NODE_LINK_MAPPINGS = {
	'SF-Dallas': '10',
	'SF-Chicago': '31',
	'SF-LA': '00',
	'LA-Dallas': '11',
	'LA-Houston': '20',
	'Houston-Dallas': '12',
	'Houston-Miami': '20',
	'Houston-Tampa': '30',
	'Tampa-Miami': '11',
	'Tampa-NY': '27',
	'NY-Miami': '32',
	'NY-Chicago': '54',
	'Dallas-Miami': '33',
	'Dallas-Chicago': '42',
	'Chicago-Miami': '34',
}

 	
class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def __init__(self, *args, **kwargs):
		super(WebSocketHandler, self).__init__(*args, **kwargs)
		self.sub_to_redis()

	def sub_to_link_events(self):
		listener = threading.Thread(target=self._sub_listen)
		listener.setDaemon(True)
		listener.start()

	def _sub_listen(self):
		for ev in self.pubsub.listen():
			self.write_message(ev)

	def sub_to_redis(self):
		self.pubsub = redis_client.pubsub()
		self.pubsub.subscribe('link_event')
		self.sub_to_link_events()

	def open(self):
		print "New client connected"

	def on_message(self, message):
		print "on_message:", message

	def on_close(self):
		print "Client disconnected"
	
	def check_origin(self, origin):
		return True

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		f = open('../visualizer/index.html', 'r')
		contents = f.read()
		f.close()
		self.write(contents)

class APIRequestHandler(tornado.web.RequestHandler):

	def __GetFromToInterfaceKey(self, fromNode, toNode):
		key_build_a = '{0}-{1}'.format(fromNode, toNode)
		key_build_b = '{0}-{1}'.format(toNode, fromNode)

		try:
			v = INTERFACE_NODE_LINK_MAPPINGS[key_build_a]
			return {'endA': 'ge-1/0/{0}'.format(v[0]), 'endZ': 'ge-1/0/{0}'.format(v[1])}
		except:
			pass

		try:
			v = INTERFACE_NODE_LINK_MAPPINGS[key_build_b]
			return {'endA': 'ge-1/0/{0}'.format(v[1]), 'endZ': 'ge-1/0/{0}'.format(v[0])}
		except: pass

	def getTokenHeader(self):
		url = "https://10.10.2.29:8443/oauth2/token"
		payload = {'grant_type': 'password', 'username': 'group6', 'password': 'Group6'}
		response = requests.post (url, data=payload, auth=('group6','Group6'), verify=False)
		return {"Authorization":"{token_type} {access_token}".format(**json.loads(response.text))}
	
	def getRedisKeys(self):
		return redis_client.keys()

	def getInterfaceStats(self, interface_key):
		return redis_client.lrange(interface_key, 0, -1)

	def getNetworkTopology(self):
		# my local doesnt work, thats why this code, on server above code will be used
		# file = open('topology.txt', 'r')
		# data = file.read()
		# file.close()
		# return json.loads(data)
		# ----

		r = requests.get('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1', headers=self.getTokenHeader(), verify=False)
		return r.json()

	def getLinksStatus(self):
		# my local doesnt work, thats why this code, on server above code will be used
		# file = open('link_status.txt', 'r')
		# data = file.read()
		# file.close()
		# return json.loads(data)
		# ----

		r = requests.get('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/links/', headers=self.getTokenHeader(), verify=False)
		return r.json()

	def getLsps(self):
		# my local doesnt work, thats why this code, on server above code will be used
		# file = open('lsps.txt', 'r')
		# data = file.read()
		# file.close()
		# return [i for i in json.loads(data) if "GROUP_SIX" in i['name']]
		# ----

		r = requests.get('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/te-lsps/', headers=self.getTokenHeader(), verify=False)
		return [i for i in r.json() if "GROUP_SIX" in i['name']]

	def getLinkTrafficStats(self, fromLink, toLink):

		ge_keys = self.__GetFromToInterfaceKey(fromLink, toLink)
		fromLinkInterfaceTrafficStatsKey = "{0}:{1}:traffic statistics".format(HOSTNAME_MAPPINGS[fromLink], ge_keys['endA'])
		toLinkInterfaceTrafficStatsKey = "{0}:{1}:traffic statistics".format(HOSTNAME_MAPPINGS[toLink], ge_keys['endZ'])

		link_latency_key_a = "{0}:{1}:latency".format(HOSTNAME_MAPPINGS[fromLink], HOSTNAME_MAPPINGS[toLink])
		link_latency_key_b = "{0}:{1}:latency".format(HOSTNAME_MAPPINGS[toLink], HOSTNAME_MAPPINGS[fromLink])

		stats = [
			{
				'key' : fromLinkInterfaceTrafficStatsKey,
				'name': fromLink,
				'data': json.loads(self.getInterfaceStats(fromLinkInterfaceTrafficStatsKey)[0])
			},
			{
				'key' : toLinkInterfaceTrafficStatsKey,
				'name': toLink,
				'data': json.loads(self.getInterfaceStats(toLinkInterfaceTrafficStatsKey)[0])
			},
			{
				'latency': [json.loads(self.getInterfaceStats(link_latency_key_a)[0]), json.loads(self.getInterfaceStats(link_latency_key_b)[0])]
			}
		]

		return stats

	def get(self):
		operation = self.get_argument("operation", default=None)
		if not operation:
			self.write(json.dumps({'error': 'No operation specified'}))

		if operation == "GET_REDIS_KEYS":
			self.write(json.dumps({'data': self.getRedisKeys()}))
		elif operation == "GET_INTERFACE_STATS":
			interface = self.get_argument('interface', default=None)
			self.write(json.dumps({'data': self.getInterfaceStats(interface)}))
		elif operation == "GET_NETWORK_TOPOLOGY":
			self.write(json.dumps({'data': self.getNetworkTopology()}))
		elif operation == "GET_LINKS_STATUS":
			self.write(json.dumps({'data': self.getLinksStatus()}))
		elif operation == "GET_LINK_TRAFFIC_STATS":
			fromLink = self.get_argument('from', default='')
			toLink = self.get_argument('to', default='')
			self.write(json.dumps({'data': self.getLinkTrafficStats(fromLink, toLink)}))
		elif operation == "GET_LSPS":
			self.write(json.dumps({'data': self.getLsps()}))
		else:
			self.write(json.dumps({'error': 'Invalid operation specified'}))

	def post(self):
		req_allparams = self.request.body.split('&')
		req_key_val_pairs = [tuple(i.split('=')) for i in req_allparams]
		
		operation = [i[1] for i in req_key_val_pairs if i[0] == "operation"][0]
		if operation == "CREATE_NEW_LSP":
			lsp_name = [i[1] for i in req_key_val_pairs if i[0] == "lspName"][0]
			erosObjs = [{'address': i[1], 'topoObjectType': 'ipv4'} for i in req_key_val_pairs if i[0][:4] == "eros"]

			lsp = [i for i in self.getLsps() if i['name'] == lsp_name][0]

			new_lsp = {}
			for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
				new_lsp[key] = lsp[key]

			new_lsp['plannedProperties'] = {
				'ero': erosObjs
			}

			response = requests.put('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), json = new_lsp, headers=self.getTokenHeader(), verify=False)

			self.write(json.dumps({'data': json.loads(response.text)}))
		else:
			self.write(json.dumps({'error': 'Invalid operation specified'}))

		
		
application = tornado.web.Application([
	# (r"/socket", WebSocketHandler),
	(r"/", MainHandler),
	(r"/api/v1", APIRequestHandler),
	(r'/(.*)', tornado.web.StaticFileHandler, {"path": "../visualizer"}),
])

PORT=8888

if __name__ == "__main__":
	application.listen(PORT)
	print "Visit: http://localhost:{0}".format(PORT)
	tornado.ioloop.IOLoop.instance().start()
