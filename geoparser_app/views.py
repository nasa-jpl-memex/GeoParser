from django.shortcuts import render
import glob, os
import urllib2
import ast
import requests
from requests.auth import HTTPBasicAuth
from ConfigParser import SafeConfigParser
from compiler.ast import flatten
from os.path import isfile
import string

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str, smart_unicode
from django.views.decorators.gzip import gzip_page
from .forms import UploadFileForm
from .models import Document

from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon, QueryPoints, IndexFile, create_core, IndexStatus, IndexCrawledPoints, get_all_cores, get_domains_urls, SimplifyPoints
from solr_admin import get_index_core

from tika import parser
from tika.tika import ServerEndpoint
from tika.tika import callServer
import traceback

import khooshe

flip = True

conf_parser = SafeConfigParser()
conf_parser.read('config.txt')


APP_NAME = conf_parser.get('general', 'APP_NAME')
UPLOADED_FILES_PATH = conf_parser.get('general', 'UPLOADED_FILES_PATH')
STATIC = conf_parser.get('general', 'STATIC')
SUBDOMAIN = conf_parser.get('general', 'SUBDOMAIN')
TIKA_SERVER = conf_parser.get('general', 'TIKA_SERVER')

headers = {"content-type" : "application/json"}
params = {"commit" : "true" }

def index(request):
    file_name = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Document(docfile=request.FILES['file'])
            instance.save()
            file_name = str(instance.docfile).replace("{0}/{1}/".format(APP_NAME, UPLOADED_FILES_PATH),"")
            return HttpResponse(status=200, content="{{ \"file_name\":\"{0}\" }}".format(file_name), content_type="application/json")
    else:
        form = UploadFileForm()
    return render_to_response('index.html', {'form': form, 'subdomian':SUBDOMAIN},  RequestContext(request))


def index_file(request, file_name):
    IndexFile("uploaded_files", file_name)
    return HttpResponse(status=200)


def list_of_uploaded_files(request):
    '''
    Return list of uploaded files.
    '''
    files_list = []
    file_dir = os.path.realpath(__file__).split("views.py")[0]
    for f in os.listdir("{0}{1}".format(file_dir, UPLOADED_FILES_PATH)):
        if not f.startswith('.'):
            files_list.append(f)
    return HttpResponse(status=200, content="{0}".format(files_list))


def list_of_domains(request):
    '''
    Returns list of Solr cores except "uploaded_files"
    '''
    domains = {}
    all_cores = get_all_cores()
    if all_cores:
        if "uploaded_files" in all_cores:
            all_cores.remove("uploaded_files")
        for core in all_cores:
            ids = get_domains_urls(core)
            domains["{0}".format(core)] = ids
    return HttpResponse(status=200, content="[" + str(domains) + "]")

    
def parse_lat_lon(locations):
    points = {}
    optionalCount = 0
    for key in locations.keys():
        if key.startswith("Optional_NAME"):
            optionalCount = optionalCount + 1 
    if 'Geographic_NAME' in locations:
        points[locations["Geographic_NAME"].replace(" ","")] = [locations["Geographic_LATITUDE"].replace(" ",""), locations["Geographic_LONGITUDE"].replace(" ","")]
    else:
        print "No main location found"
    for x in range(1, optionalCount+1):
        points[locations["Optional_NAME{0}".format(x)].replace(" ","")] = [locations["Optional_LATITUDE{0}".format(x)].replace(" ",""), locations["Optional_LONGITUDE{0}".format(x)].replace(" ","")]

    return points


def extract_text(request, file_name):
    '''
        Using Tika to extract text from given file
        and return the text content.
    '''
    if "none" in IndexStatus("text", file_name):
        parsed = parser.from_file("{0}/{1}/{2}".format(APP_NAME, UPLOADED_FILES_PATH, file_name))
        status = IndexUploadedFilesText(file_name, parsed["content"])
        if status[0]:
            return HttpResponse(status=200, content="Text extracted.")
        else:
            return HttpResponse(status=400, content="Cannot extract text.")
    else:
        return HttpResponse(status=200, content="Loading...")



def find_location(request, file_name):
    '''
        Find location name from extracted text using Geograpy.
    '''
    if "none" in IndexStatus("locations", file_name):
        text_content = QueryText(file_name)
        if text_content:
            parsed = callServer('put', TIKA_SERVER, '/rmeta', text_content, {'Accept': 'application/json',  'Content-Type' : 'application/geotopic'}, False)
            points = parse_lat_lon(eval(parsed[1])[0])
            
            status = IndexLocationName(file_name, points)
            if status[0]:
                return HttpResponse(status=200, content="Location/s found and index to Solr.")
            else:
                return HttpResponse(status=400, content=status[1])
        else:
            return HttpResponse(status=400, content="Cannot find location.")
    else:
        return HttpResponse(status=200, content="Loading...")



def find_latlon(request, file_name):
    '''
    Find latitude and longitude from location name using GeoPy.
    '''
    if "none" in IndexStatus("points", file_name):
        location_names = QueryLocationName(file_name)
        if location_names:
            points = []
            location_names = ast.literal_eval(location_names)
            for key, values in location_names.iteritems():
                try:
                    points.append(
                        {'loc_name': "{0}".format(key),
                        'position':{
                            'x': "{0}".format(values[0]),
                            'y': "{0}".format(values[1])
                        }
                        }
                    )
                except:
                    pass
            status = IndexLatLon(file_name, points)
            if status[0]:
                return HttpResponse(status=200, content="Latitude and longitude found.")
            else:
                return HttpResponse(status=400, content="Cannot find latitude and longitude.")
        else:
            return HttpResponse(status=400, content="Cannot find latitude and longitude.")
    else:
        return HttpResponse(status=200, content="Loading...")


@gzip_page
def return_points(request, file_name, core_name):
    '''
        Returns geo point for give file
    '''
    results = {}
    points, total_docs, rows_processed = QueryPoints(file_name, core_name)
    results["points"] = points
    results["total_docs"] = total_docs
    results["rows_processed"] = rows_processed
    if total_docs or points:
        return HttpResponse(status=200, content="[{0}]".format(results))
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude(return_points).")


def return_points_khooshe(request, file_name, core_name):
    '''
        Returns geo point for give file using khooshe
    '''
    results = {}
    points, total_docs, rows_processed = QueryPoints(file_name, core_name)
    results["total_docs"] = total_docs
    results["rows_processed"] = rows_processed
    results["points_count"] = len(points)
    exclude = set(string.punctuation)
    file_name = ''.join(ch for ch in core_name+file_name if ch not in exclude)
    results["khooshe_tile"] = "static/tiles/{0}".format(file_name)
    if total_docs or points:
        return HttpResponse(status=200, content="[{0}]".format(results))
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude(return_points_khooshe).")


def query_crawled_index(request, domain_name, indexed_path, username, passwd):
    '''
        To query crawled data that has been indexed into
        Solr or Elastichsearch and return location names
    '''
    if "solr" in indexed_path.lower():
        '''
        Query admin core to get core information for domain_name, indexed_path combination
        '''
        core_name = get_index_core(domain_name, indexed_path)
        print core_name
        if create_core(core_name):
            query_range = 500
            simplilfy_freq = query_range * 50
            # 1 QUERY solr 100 records at a time
            # 2     Run GeotopicParser on each doc one at a time
            # 4     Save it in local solr instance
            rows_processed = 0
#             try:
#                 _, _, rows_processed = QueryPointsIndex(core_name)
#             except:
#                 pass
            try:
                url = "{0}/select?q=*%3A*&wt=json&rows=1".format(indexed_path)
                r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
                
                if r.status_code != 200:
                    return HttpResponse(status=r.status_code, content=r.reason)
                
                response = r.json()
                numFound = response['response']['numFound']
                print "Total number of records to be geotagged {0}".format(numFound)
                #print SimplifyPoints(domain_name, indexed_path.lower())
                for row in range(rows_processed, int(numFound), query_range): #loop solr query
#                     if row % simplilfy_freq == 0:
#                         print SimplifyPoints(domain_name, indexed_path.lower())

                    docs = {}
                    url = "{0}/select?q=*%3A*&start={1}&rows={2}&wt=json".format(indexed_path, row, query_range)
                    print "solr query - {0}".format(url)
                    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
                    response = r.json()
                    text = response['response']['docs']
                    docCount = 0
                    for t in text: #loop tika server starts
                        points = []
                        try:
                            docCount+=1
                            text_content = ''
                            try:
                                for v in t.values():
                                    if(hasattr(v, '__iter__')):
                                        a =u' '.join(v)
                                    elif(isinstance(v, unicode) ):
                                        a = v.encode('ascii','ignore')
                                    else:
                                        a=str(v)
                                    text_content+=a.encode('ascii','ignore')
                            except Exception as e:
                                print traceback.format_exc()
                                text_content=str(t.values())
                            
                            # simplify text
                            text_content= ' '.join(text_content.split())
                            
                            parsed = callServer('put', TIKA_SERVER, '/rmeta', text_content, {'Accept': 'application/json',  'Content-Type' : 'application/geotopic'}, False)
                            location_names = parse_lat_lon(eval(parsed[1])[0])
        
                            for key, values in location_names.iteritems():
                                try:
                                    ## TODO - ADD META DATA
                                    points.append(
                                        {'loc_name': smart_str(key),
                                        'position':{
                                            'x': smart_str(values[0]),
                                            'y': smart_str(values[1])
                                        }
                                        }
                                    )
                                except Exception as e:
                                    print "Error while transforming points "
                                    print e
                                    pass
                            print "Found {0} coordinates..".format(len(points))
                            docs[str(t['id'])] = points
                            #print docs
                        except Exception as e:
                            print traceback.format_exc()
                            pass
                        #loop tika server ends
                    status = IndexCrawledPoints(core_name, docs)
                    #loop solr query ends
                #print SimplifyPoints(domain_name, indexed_path.lower())
                return HttpResponse(status=200, content=status)
            except Exception as e:
                print "Error::: "
                print e
                return False
    else:
        pass
