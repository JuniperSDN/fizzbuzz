import matplotlib.pyplot as plt
import os, json, redis

def graphStats(datakey, data, keys=['input-bytes', 'output-bytes', 'input-packets', 'output-packets', 'input-pps', 'output-pps']):
	for key in keys:
		x = range(0, len(data))
		y = [int(i['stats'][0][key][0]['data']) for i in data]
		plt.plot(x, y)
		plt.xlabel('#num')
		plt.ylabel(key)

		# make dir before hand, so matplot lib can save
		datakey = datakey.replace('/', '-') # path escaping
		dirpath = 'graphs/{0}/'.format(datakey)
		
		try: os.makedirs(dirpath)
		except: pass # most likely dir exists, so ignoring

		plt.savefig( (dirpath + key + '.png') )
		plt.gcf().clear() # clear for next run


if __name__ == "__main__":
	r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)
	r_keys = r.keys()
	# print r_keys

	for key in r_keys:
		if "statistics" in key: # only query statistics as of now
			continue;
			key_data = [json.loads(i) for i in r.lrange(key, 0, -1)]
			graphStats(key, key_data)
		elif "latency" in key:
			print r.lrange(key, 0, -1)
