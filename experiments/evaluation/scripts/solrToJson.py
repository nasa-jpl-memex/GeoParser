import urllib2
import simplejson
import json
import sys

#Accept name of the file in which index will be exported as a JSON.
filename = sys.argv[1]

#Sample url fetching all documents containing text/html content types.
url = 'http://imagecat.dyndns.org/solr/cronIngest/select?q=contentType+%3A+text%2Fhtml&rows=10000&wt=json&indent=true'
username = 'darpamemex'
password = 'darpamemex'
p = urllib2.HTTPPasswordMgrWithDefaultRealm()

p.add_password(None, url, username, password)

handler = urllib2.HTTPBasicAuthHandler(p)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

connection = urllib2.urlopen(url)
response = simplejson.load(connection)

#Example : html.json
with open(filename, "w") as f:	
    f.write(json.dumps(response["response"]["docs"], sort_keys=True, indent=4, separators=(',', ': ')))