'''
Created on Feb 21, 2016

@author: azaringh
'''

'''
Retrieve topology of the network
'''

import requests
requests.packages.urllib3.disable_warnings()
import json
import ssl


class MyAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
        )

url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group6', 'password': 'Group6'}
response = requests.post (url, data=payload, auth=('group6','Group6'), verify=True)
print response.headers
# json_data = json.loads(response.text)
# authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

# r = requests.get('http://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1', headers=authHeader, verify=False)
# print json.dumps(r.json(), indent=4, separators=(',', ': '))
