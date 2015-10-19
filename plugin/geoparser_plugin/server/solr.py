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
            command = "{0}/../../../Solr/solr-5.3.1/bin/solr create_core -c {1}".format(file_dir, COLLECTION_NAME)
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
    text = "".join(text.splitlines())
    text = text.encode('ascii', 'ignore')
    text = text.replace(" ","")
    text = text.replace("&","")
    text = text.replace("#","")
    text = text.replace("%","")
    text = text.replace("<","")
    text = text.replace(">","")
    if create_core(COLLECTION_NAME):
        try:
            url = '{0}{1}/update?stream.body=%3Cadd%3E%3Cdoc%3E%3Cfield%20name=%22id%22%3E{2}%3C/field%3E%3Cfield%20name=%22text%22%3E{3}%3C/field%3E%3C/doc%3E%3C/add%3E&commit=true'.format(SOLR_URL, COLLECTION_NAME, file_name, text)
            urllib2.urlopen(url)
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
    print places


def SolrQueryLocationName(file_name):
    '''
    Return location names for given filename
    '''


def SolrIndexLatLon(file_name, points):
    '''
    Index points for given file
    '''


def SolrQueryPoints(file_name):
    '''
    Return geopoints for given filename
    '''
