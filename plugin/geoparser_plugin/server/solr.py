import os

SOLR_URL = "http://localhost:8983/solr/"
COLLECTION_NAME = "uploaded_files"


def check_solr():
    '''
    Check is solr running
    '''
    pass


def create_collection(collection_name):
    '''
    If Solr collection not built, create one.
    '''


def SolrIndexText(file_name, text):
    '''
    Index extracted text from each file.
    '''


def SolrQueryText(file_name):
    '''
    Return extracted and indexed text for each file.
    '''


def SolrIndexLocationName(file_name, places):
    '''
    Index location name for each file.
    '''


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
