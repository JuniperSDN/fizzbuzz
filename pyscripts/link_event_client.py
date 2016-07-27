'''
Created on Feb 20, 2016

@author: azaringh
'''

import redis
import json
import pprint


r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)
latency_keys = [i for i in r.keys() if "houston" in i]

print r.lrange('houston:miami:latency', 0, -1)[0]
# for k in latency_keys:
# 	print k
	# print r.lrange(k, 0, -1)[0]
	# break

# pubsub = r.pubsub()
# pubsub.subscribe('link_event')
# # print pubsub.listen()
# for i in pubsub.listen():
# 	print 'ev:',i
# # for item in pubsub.listen():
# #     print item['channel'], ":", item['data']
# #     if isinstance(item['data'], basestring):
# #         d = json.loads(item['data'])
# #         pprint.pprint(d, width=1)