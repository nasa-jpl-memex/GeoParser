import urllib2
import simplejson
import json
import sys
import requests
import urllib
import re

def findCount(content):
    listc = list(content)
    for c in range(len(content)):
        character = content[c]
        if(ord(character) in range(65,91) or ord(character) in range(97,123)):
                continue
        else:
            listc[c] = "\n"
    content = "".join(listc)
    re.sub('\n+','\n',content)
    words = content.split("\n")
    searchList = search.split(",")
    #print searchList
    for word in words:
        if word in searchList:
            if search in count1.keys():
                count1[search]+=1
            else:
                count1[search]=1

    return count1


def secureSolr(query):
    url = 'http://imagecat.dyndns.org/solr/cronIngest/select?'+query+'&wt=json&indent=true&rows=100000'
    username = 'username'
    password = 'password'
    p = urllib2.HTTPPasswordMgrWithDefaultRealm()
    p.add_password(None, url, username, password)
    handler = urllib2.HTTPBasicAuthHandler(p)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    connection = urllib2.urlopen(url)
    response = simplejson.load(connection)
    return response

def localSolr(query):
    url = 'http://localhost:8983/solr/cronIngest/select?'+query+'&wt=json&indent=true&rows=100000'
    connection = urllib2.urlopen(url)
    response = simplejson.load(connection)
    return response

if __name__ == "__main__":
    query = urllib.urlencode({'q':sys.argv[1]})
    print(query)
    #response = secureSolr(query)
    response = localSolr(query)
    numFound = response["response"]["numFound"]
    print numFound

    search = sys.argv[1]
    count1 = {}
    count1[search]=0

    for i in range(numFound):
        for j in response["response"]["docs"][i].keys():
            if type(response["response"]["docs"][i][j]) == list:
                for k in range(len(response["response"]["docs"][i][j])):
                    content = response["response"]["docs"][i][j][k]
                    count1 = findCount(content)
            elif type(response["response"]["docs"][i][j]) == str:
                content = response["response"]["docs"][i][j]
                count1 = findCount(content)
            elif type(response["response"]["docs"][i][j]) == unicode:
                content = response["response"]["docs"][i][j].encode('ascii','ignore')
                count1 = findCount(content)

    print(count1)

#with open(filename, "w") as f:
    #f.write(json.dumps(response["response"]["docs"], sort_keys=True, indent=4, separators=(',', ': ')))