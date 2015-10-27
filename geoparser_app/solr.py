import os
import urllib2

SOLR_URL = "http://localhost:8983/solr/"
COLLECTION_NAME = "uploaded_files"


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
            command = "{0}/../Solr/solr-5.3.1/bin/solr create_core -c {1}".format(file_dir, COLLECTION_NAME)
            os.system(command)
            return True
        except:
            return False
    else:
        print False


def IndexUploadedFilesText(file_name, text):
    '''
    Index extracted text for given file.
    '''
    file_dir = os.path.realpath(__file__).split("solr.py")[0]
    tmp_json = "{0}/static/json/tmp.json".format(file_dir)
    with open(tmp_json, 'w') as f:
        f.write("[{{'id':'{0}', 'text':'{1}'}}]".format(file_name, text.encode('ascii', 'ignore')))
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


def IndexLocationName(file_name, places):
    '''
    Index location name for each file.
    '''
    if create_core(COLLECTION_NAME):
        try:
            p = ",".join(places)
            url = SOLR_URL + COLLECTION_NAME + '/update?stream.body=[{%22id%22:%22' + file_name + '%22,%22locations%22:{%22set%22:"' + p + '"}}]&commit=true'
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
            points = ",".join(str(p) for p in points)
            points = urllib2.quote(points)
            url = SOLR_URL + COLLECTION_NAME + '/update?stream.body=[{%22id%22:%22' + file_name + '%22,%22points%22:{%22set%22:%22' + points + '%22}}]&commit=true'
            urllib2.urlopen(url)
            return (True, "Latitude and longitude indexed to Solr successfully.")
        except:
            return (False, "Cannot index latitude and longitude to Solr.")
    else:
        return (False, "Either Solr not running or cannot create Core.")


def QueryPoints(file_name):
    '''
    Return geopoints for given filename
    '''
    if create_core(COLLECTION_NAME):
        try:
            url = '{0}{1}/select?q=*%3A*&fq=id%3A%22{2}%22&wt=json&indent=true'.format(SOLR_URL, COLLECTION_NAME, file_name)
            response = urllib2.urlopen(url)
            return eval(response.read())['response']['docs'][0]['points'][0]
        except:
            return False
