#!/usr/bin/python
# =====================================================================================================================
#
# Overview: This script delete objects out of Cisco FMC utilizing the built-in API
#
# Usage:    Run python <script_name> 
#
# Use script at you own risk, and no warranties are inferred or granted. 
# =====================================================================================================================
import requests
import json
import requests
import logging
import time
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig(filename='response.log',level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True

results=[]
ipaddr = ""
user1="api"
pass1=""
querystring = {"limit":"1000"}
headers = {
    'cache-control': "no-cache",
    'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
    }

url = "https://%s/api/fmc_platform/v1/auth/generatetoken" % ipaddr

response = requests.request("POST", url, headers=headers, auth=(user1,pass1), verify=False)

# Authenicates token used in addiotnal HTTPS CRUD request
auth = response.headers['X-auth-access-token']

url = "https://%s/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies" % ipaddr

headers = {
    'x-auth-access-token': auth,
    'cache-control': "no-cache",
    'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
    }

#Need to work on this logic list item need to be verifed. Need to verify which ACP is applied.
# get all objects type based in user reponse from FMC 
response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

r = response.json()
number=1
for i in r['items']:
 print "%d. %s" % (number,i['name'])
 number+=1

acp = input("Enter your FMC ACP policy number: ")

acp -= 1
url = r['items'][acp]['links']['self']

#querystring = {"expanded":"true"}
response = requests.request("GET", url, headers=headers, verify=False)

url = response.json()['rules']['links']['self']

response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

raw = response.json()


for i in raw['items']:  
	results.append(i['links']['self'])
number=1

target = open('rules.csv', 'w')

for i in results:
	response = requests.request("GET", i, headers=headers, verify=False)
	raw=response.json()
	raw.setdefault('name', "noname_rule")
	raw.setdefault('action', "no_action")
	raw.setdefault('sourceNetworks', "any-src")
	raw.setdefault('destinationNetworks', "any-dest")
	raw.setdefault('sourcePorts', "any-src-port")
	raw.setdefault('destinationPorts', "any-dest-port")
	interesting_keys = ('name', 'action', 'sourceNetworks', 'sourcePorts', 'destinationNetworks', 'destinationPorts' )
	subdict = {x: raw.get(x, "any") for x in interesting_keys if x in raw}
	
	if 'objects' in subdict['sourceNetworks']:
		srcnet = subdict['sourceNetworks']['objects'][0]['name']
	else :
		srcnet = "any-src"
	
	if 'objects' in subdict['destinationNetworks']:
		dstnet = subdict['destinationNetworks']['objects'][0]['name']
	else :
		dstnet = "any-dst"
		
	if 'objects' in subdict['sourcePorts']:
		srcprt = subdict['sourcePorts']['objects'][0]['name']
	else :
		srcprt = "any-src-port"
		
	if 'objects' in subdict['destinationPorts']:
		dstprt = subdict['destinationPorts']['objects'][0]['name']
	else :
		dstprt = "any-dest-port"

	print >> target, "%d,%s,%s,%s,%s,%s,%s" %(number, subdict['name'],subdict['action'],srcnet,srcprt,dstnet,dstprt)
	number+=1
	time.sleep(.5)

target.close()







