import os
import urllib2
import requests


SOLR_URL = "http://localhost:8983/solr/"
COLLECTION_NAME = "uploaded_files"


headers = {"content-type" : "application/json" }
params = {"commit" : "true" }

def check_solr():
    '''
    Check is solr running
    '''
    try:
        respond = urllib2.urlopen(SOLR_URL)
        return True
    except:
        return False


def core_exists(core_name):
    '''
    Check if core alreay created
    '''
    if check_solr():
        try:
            url = "{0}{1}/select?q=*%3A*".format(SOLR_URL, core_name)
            respond = urllib2.urlopen(url)
            return True
        except:
            return False
    else:
        print "Error: Solr has not started."
        return False


def create_core(core_name):
    '''
    If Solr core not created, create one.
    '''
    if core_exists(core_name):
        return True
    elif check_solr():
        try:
            file_dir = os.path.realpath(__file__).split("solr.py")[0]
            command = "{0}/../Solr/solr-5.3.1/bin/solr create_core -c {1}".format(file_dir, core_name)
            os.system(command)
            return True
        except:
            return False
    else:
        print False


def get_all_cores():
    '''
    Return all existing cores
    '''
    try:
        url = "{0}admin/cores?action=STATUS&wt=json".format(SOLR_URL)
        r = requests.get(url, headers=headers)
        response = r.json()
        return response["status"].keys()
    except:
        return None


def get_domains_urls(core):
    '''
    Return list of urls (ids) inside that core
    '''
    try:
        url = "{0}{1}/select?q=*%3A*&fl=id&wt=json&indent=true".format(SOLR_URL, core)
        r = requests.get(url, headers=headers)
        response = r.json()
        return [each['id'] for each in response["response"]["docs"]]
    except:
        return None


def IndexStatus(step, file_name):
    try:
        url = "{0}{1}/select?q=*%3A*&fq=id%3A+%22{2}%22&fl={3}&wt=json&indent=true".format(SOLR_URL, COLLECTION_NAME, file_name, step)
        r = requests.get(url, headers=headers)
        response = r.json()
        return response['response']['docs'][0][step][0]
    except Exception as e:
        return "none"


def IndexFile(core_name, file_name):
    '''
    Index filename, text, location and points fields in Solr if not already exists.
    '''
    if create_core(core_name):
        try:
            url = "{0}{1}/select?q=*%3A*&fl=id&wt=json&indent=true".format(SOLR_URL, core_name)
            response = urllib2.urlopen(url)
            files = eval(response.read())['response']['docs']
            files = [f['id'] for f in files]
            if file_name in files:
                return True
            else:
                try:
                    if core_name == COLLECTION_NAME:
                        payload = {
                            "add":{
                                "doc":{
                                    "id" : str(file_name) ,
                                    "text" : "none",
                                    "locations" : "none",
                                    "points" : "none"
                                }
                            }
                        }
                        r = requests.post("{0}{1}/update".format(SOLR_URL, COLLECTION_NAME), data=str(payload), params=params,  headers=headers)
                    else:
                        payload = {
                            "add":{
                                "doc":{
                                    "id" : str(file_name)
                                }
                            }
                        }
                        r = requests.post("{0}{1}/update".format(SOLR_URL, core_name), data=str(payload), params=params,  headers=headers)
                    return True
                except:
                    print "Cannot index status fields"
                    return False
        except:
            print "Error calling solr"
            return False
    else:
        return False


def IndexUploadedFilesText(file_name, text):
    '''
    Index extracted text for given file.
    '''
    text = text.replace("'", " ")
    file_dir = os.path.realpath(__file__).split("solr.py")[0]
    tmp_json = "{0}/static/json/tmp.json".format(file_dir)
    with open(tmp_json, 'w') as f:
        f.write("[{{'id':'{0}', 'text':'{1}', 'locations':'\"none\"', 'points':'\"none\"'}}]".format(file_name, text.encode('ascii', 'ignore')))
        f.close()
    if create_core(COLLECTION_NAME):
        try:
            command = "{0}/../Solr/solr-5.3.1/bin/post -c {1} {2}".format(file_dir, COLLECTION_NAME, tmp_json)
            os.system(command)
            os.remove(tmp_json)
            return (True, "Text indexed to Solr successfully.")
        except:
            return (False, "Cannot index text to Solr.")
    else:
        return (False, "Either Solr not running or cannot create Core.")


def QueryText(file_name):
    '''
    Return extracted and indexed text for each file.
    '''
    if create_core(COLLECTION_NAME):
        try:
            url = '{0}{1}/select?q=*%3A*&fq=id%3A%22{2}%22&wt=json&indent=true'.format(SOLR_URL, COLLECTION_NAME, file_name)
            response = urllib2.urlopen(url)
            return eval(response.read())['response']['docs'][0]['text'][0]
        except:
            return False


def IndexLocationName(name, places):
    '''
    Index location name for each file.
    '''
    if create_core(COLLECTION_NAME):
        try:
            p = ",".join(places)
            url = SOLR_URL + COLLECTION_NAME + '/update?stream.body=[{%22id%22:%22' + name + '%22,%22locations%22:{%22set%22:"' + p + '"}}]&commit=true'
            urllib2.urlopen(url)
            return (True, "Location name/s indexed to Solr successfully.")
        except:
            return (False, "Cannot index location name/s to Solr.")
    else:
        return (False, "Either Solr not running or cannot create Core.")


def QueryLocationName(file_name):
    '''
    Return location names for given filename
    '''
    if create_core(COLLECTION_NAME):
        try:
            url = '{0}{1}/select?q=*%3A*&fq=id%3A%22{2}%22&wt=json&indent=true'.format(SOLR_URL, COLLECTION_NAME, file_name)
            response = urllib2.urlopen(url)
            return eval(response.read())['response']['docs'][0]['locations'][0].split(',')
        except:
            return False


def IndexLatLon(file_name, points):
    '''
    Index points for given file
    '''
    if create_core(COLLECTION_NAME):
        try:
            payload = {
                "add":{
                    "doc":{
                        "id" : str(file_name) ,
                        "points" : {"set" : "{0}".format(points)}
                    }
                }
            }
            r = requests.post("{0}{1}/update".format(SOLR_URL, COLLECTION_NAME), data=str(payload), params=params,  headers=headers)
            return (True, "Latitude and longitude indexed to Solr successfully.")
        except:
            return (False, "Cannot index latitude and longitude to Solr.")
    else:
        return (False, "Either Solr not running or cannot create Core.")


def QueryPoints(file_name, core_name):
    '''
    Return geopoints for given filename
    '''
    if create_core(core_name):
        try:
            url = '{0}{1}/select?q=*%3A*&fq=id%3A%22{2}%22&wt=json&indent=true'.format(SOLR_URL, core_name, file_name)
            response = urllib2.urlopen(url)
            return eval(response.read())['response']['docs'][0]['points'][0]
        except:
            return False


def IndexCrawledPoints(core_name, name, points):
    '''
    Index geopoints extracted from crawled data
    '''
    try:
        payload = {
            "add":{
                "doc":{
                    "id" : str(name) ,
                    "points" : "{0}".format(points)
                }
            }
        }
        r = requests.post("{0}{1}/update".format(SOLR_URL, core_name), data=str(payload), params=params,  headers=headers)
        return (True, "Crwaled data geopoints indexed to Solr successfully.")
    except:
        return (False, "Cannot index geopoints from crawled data to Solr.")
