'''
GeoParser admin core Utility
- Store information about index configuration
	- id - domain-name
	- key(index) <-> value(core name in GeoParser solr)
'''
import base64

import yaml

from solr import *


ADMIN_CORE = 'admin'

#TODO change it to custom base 62 encoding without =
def encode_index(index_path):
	encodeStr = base64.b64encode(index_path, ['-', '_'])
	return encodeStr.replace("=", "_")

def decode_index(encodeStr):
	index_path = encodeStr.replace("_", "=")
	index_path = base64.b64decode(index_path, ['-', '_'])
	return index_path

def get_index_core(domain, index_path):

	if create_core(ADMIN_CORE):
		enc_index = encode_index(index_path)
		headers = {'content-type': 'application/json'}
		url = '{0}{1}/select?q=id:{2}&wt=json'.format(SOLR_URL, ADMIN_CORE, domain)
		
		response = requests.get(url, headers=headers)
		response = yaml.safe_load(response.text)
		
		num_found = response['response']['numFound']
		if(num_found == 0):  # # No record found for this domain.  
			count = 1  # # Initialize a new one
		else:
			# Check if this index exist for this domain
			if(enc_index in response['response']['docs'][0]):
				core_name = response['response']['docs'][0][enc_index][0]
				return core_name
			# if not create a new count for this index
			count = response['response']['docs'][0]['count'][0] + 1
		
		# get unique core name
		core_name = "{0}_{1}".format(domain, count)
		payload = {
					"add":{
						   "doc":{
								  "id" : "{0}".format(domain) ,
								  enc_index : {"set":core_name},
								  'count' : {"set":count}
								  }
						   }
				   }
		r = requests.post("{0}{1}/update".format(SOLR_URL, ADMIN_CORE), data=str(payload), params=params, headers=headers)
		
		print r.text
		
		if(not r.ok):
			raise "Can't create core with core name {0}".format(core_name)
		
		return core_name
