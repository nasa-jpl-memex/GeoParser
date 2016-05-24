from django.shortcuts import render
import glob, os
import urllib2
import urllib
import ast
import requests
from requests.auth import HTTPBasicAuth
from ConfigParser import SafeConfigParser
from compiler.ast import flatten
from os.path import isfile
import string
import shutil

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str, smart_unicode
from django.views.decorators.gzip import gzip_page
from .forms import UploadFileForm
from .models import Document

from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon, QueryPoints, IndexFile, create_core, IndexStatus, IndexCrawledPoints, GenerateKhooshe, GetIndexSize , SearchLocalSolrIndex
from solr_admin import get_index_core, get_all_domain_details, get_idx_details, update_idx_details,update_idx_field_csv,get_idx_field_csv

from tika import parser
from tika.tika import ServerEndpoint
from tika.tika import callServer
import traceback

import thread
import time
import re

flip = True

conf_parser = SafeConfigParser()
conf_parser.read('config.txt')


APP_NAME = conf_parser.get('general', 'APP_NAME')
UPLOADED_FILES_PATH = conf_parser.get('general', 'UPLOADED_FILES_PATH')
STATIC = conf_parser.get('general', 'STATIC')
SUBDOMAIN = conf_parser.get('general', 'SUBDOMAIN')
TIKA_SERVER = conf_parser.get('general', 'TIKA_SERVER')

QUERY_RANGE = 500
KHOOSHE_GEN_FREQ = QUERY_RANGE * 30
MAX_SEARCH_RESULT = 20000

headers = {"content-type" : "application/json"}
params = {"commit" : "true" }

accept_new_khooshe_request = True

exclude = set(string.punctuation)


def index(request):
    file_name = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Document(docfile=request.FILES['file'])
            instance.save()
            file_name = str(instance.docfile).replace("{0}/{1}/".format(APP_NAME, UPLOADED_FILES_PATH), "")
            return HttpResponse(status=200, content="{{ \"file_name\":\"{0}\" }}".format(file_name), content_type="application/json")
    else:
        form = UploadFileForm()
    return render_to_response('index.html', {'form': form, 'subdomian':SUBDOMAIN}, RequestContext(request))


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
    domains = get_all_domain_details()
    return HttpResponse(status=200, content="[" + str(domains) + "]")

    
def parse_lat_lon(locations):
    points = {}
    optionalCount = 0
    for key in locations.keys():
        if key.startswith("Optional_NAME"):
            optionalCount = optionalCount + 1 
    if 'Geographic_NAME' in locations:
        points[locations["Geographic_NAME"].replace(" ", "").decode("UTF-8",'ignore')] = [locations["Geographic_LATITUDE"].replace(" ", ""), locations["Geographic_LONGITUDE"].replace(" ", "")]
    else:
        print "No main location found"
    for x in range(1, optionalCount + 1):
        points[locations["Optional_NAME{0}".format(x)].replace(" ", "").decode("UTF-8",'ignore')] = [locations["Optional_LATITUDE{0}".format(x)].replace(" ", ""), locations["Optional_LONGITUDE{0}".format(x)].replace(" ", "")]

    return points


def removeNewLineAndPunctuation(text):
    regex = re.compile('[%s]' % re.escape(string.punctuation + "\n" ))
    return regex.sub(' ', text)


def extract_text(request, file_name):
    '''
        Using Tika to extract text from given file
        and return the text content.
    '''
    if "none" in IndexStatus("text", file_name):
        parsed = parser.from_file("{0}/{1}/{2}".format(APP_NAME, UPLOADED_FILES_PATH, file_name))
        text =  parsed["content"] + " ".join(parsed["metadata"]) 
        text = removeNewLineAndPunctuation(text)
        
        status = IndexUploadedFilesText(file_name, text)
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
            parsed = callServer('put', TIKA_SERVER, '/rmeta', text_content, {'Accept': 'application/json', 'Content-Type' : 'application/geotopic'}, False)
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

'''
Works only for file uploads
index geo tagging have different solr schema
TODO - Consider having a unified approach
'''
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

'''
Works only for index geo tagging 
file uploads have different solr schema
TODO - Consider having a unified approach
'''

def create_khooshe_result(rows_processed, total_docs, points_count,popup_fields, khooshe_tile):
    results = {}
    results["rows_processed"] = rows_processed
    results["total_docs"] = total_docs
    results["points_count"] = points_count 
    results["popup_fields"] = popup_fields
    results["khooshe_tile"] = khooshe_tile
    
    return results


def return_points_khooshe(request, indexed_path, domain_name):
    '''
        Returns geo point for give file using khooshe
    '''
    core_name,_,_ = get_index_core(domain_name, indexed_path)

    total_docs, points_count = get_idx_details(domain_name, indexed_path)

    file_name = ''.join(ch for ch in core_name if ch not in exclude)

    results  = create_khooshe_result(GetIndexSize(core_name), total_docs, points_count, 
                                     get_idx_field_csv(domain_name, indexed_path),"static/tiles/{0}".format(file_name) )
    
    if results["rows_processed"]:
        return HttpResponse(status=200, content="[{0}]".format(results))
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude(return_points_khooshe).")


def _gen_khooshe_update_admin_thread(core_name, domain_name, indexed_path, numFound):
    global accept_new_khooshe_request
    try:
        points_len = GenerateKhooshe(core_name)
        update_idx_details(domain_name, indexed_path, numFound, points_len)
    except Exception as e:
        print traceback.format_exc()
        print e
    accept_new_khooshe_request = True
    

def gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound):
    global accept_new_khooshe_request
    if(accept_new_khooshe_request) :
        accept_new_khooshe_request = False
        thread.start_new_thread(_gen_khooshe_update_admin_thread, (core_name, domain_name, indexed_path, numFound))
        return True
    else:
        print "Rejected Khooshe generation request.. Waiting for previous request to get completed"
        return False


def refresh_khooshe_tiles(request, domain_name, indexed_path):
    core_name,_,_ = get_index_core(domain_name, indexed_path)
    numFound = GetIndexSize(core_name)
    is_in_queue = gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
    if(is_in_queue):
        return HttpResponse(status=200, content="[{'msg':'Queued Khooshe generation'}]")
    else:
        return HttpResponse(status=200, content="[{'msg':'Can't queue another Khooshe generation'}]")


def get_idx_fields_for_popup(request, domain_name, indexed_path):
    print "get popup fields"
    return HttpResponse(status=200, content=get_idx_field_csv(domain_name, indexed_path))


def set_idx_fields_for_popup(request, domain_name, indexed_path, index_field_csv):
    print "setting popup fields"
    if(update_idx_field_csv(domain_name, indexed_path, index_field_csv)):
        return HttpResponse(status=200, content="[{'msg':'success'}]")
    else:
        return HttpResponse(status=200, content="[{'msg':'failed'}]")


def add_crawled_index(request, domain_name, indexed_path, username, passwd):
    '''
        Adds a new index in admin core. Storing username and password for future use
    '''
    core_name,_,_ = get_index_core(domain_name, indexed_path, username, passwd)
    print "Created core ", core_name
    
    if(core_name):
        return HttpResponse(status=200, content="[{'msg':'success'}]")
    else:
        return HttpResponse(status=200, content="[{'msg':'failed'}]")
    
def query_crawled_index(request, domain_name, indexed_path):
    '''
        To query crawled data that has been indexed into
        Solr or Elastichsearch and return location names
    '''
    if "solr" in indexed_path.lower():
        '''
        Query admin core to get core information for domain_name, indexed_path combination
        '''
        core_name, username, passwd = get_index_core(domain_name, indexed_path)
        print core_name
        if create_core(core_name):
            # 1 query solr QUERY_RANGE records at a time
            # 2     Run GeotopicParser on each doc one at a time
            # 3     keep appending results 
            # 4 Save it in local solr instance
            rows_processed = 0
            try:
                rows_processed = GetIndexSize(core_name)
            except:
                pass
            try:
                url = "{0}/select?q=*%3A*&wt=json&rows=1".format(indexed_path)
                r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
                
                if r.status_code != 200:
                    return HttpResponse(status=r.status_code, content=r.reason)
                
                response = r.json()
                numFound = response['response']['numFound']
                print "Total number of records to be geotagged {0}".format(numFound)
                #gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
                khooshe_gen_freq_l = rows_processed 
                for row in range(rows_processed, int(numFound), QUERY_RANGE):  # loop solr query
                    if row <= khooshe_gen_freq_l <= (row + QUERY_RANGE):
                        print "Generating khooshe tiles.."
                        gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
                        if (khooshe_gen_freq_l >= KHOOSHE_GEN_FREQ):
                            khooshe_gen_freq_l += KHOOSHE_GEN_FREQ
                        else:
                            khooshe_gen_freq_l = (row + QUERY_RANGE) * 2
                    else:
                        print "Skip generating khooshe tiles.. row - {0}, next scheduled - {1} ".format(row,khooshe_gen_freq_l)

                    docs = {}
                    url = "{0}/select?q=*%3A*&start={1}&rows={2}&wt=json".format(indexed_path, row, QUERY_RANGE)
                    print "solr query - {0}".format(url)
                    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
                    response = r.json()
                    text = response['response']['docs']
                    docCount = 0
                    for t in text:  # loop tika server starts
                        points = []
                        try:
                            docCount += 1
                            text_content = ''
                            try:
                                for v in t.values():
                                    if(hasattr(v, '__iter__')):
                                        a = u' '.join(unicode(e) for e in v)
                                    elif(isinstance(v, unicode)):
                                        a = v.encode('ascii', 'ignore')
                                    else:
                                        a = str(v)
                                    text_content += ' ' + a.encode('ascii', 'ignore')
                            except Exception as e:
                                print traceback.format_exc()
                                text_content = str(t.values())
                            
                            # simplify text
                            text_content = ' '.join(text_content.split())
                            
                            parsed = callServer('put', TIKA_SERVER, '/rmeta', text_content, {'Accept': 'application/json', 'Content-Type' : 'application/geotopic'}, False)
                            location_names = parse_lat_lon(eval(parsed[1])[0])
        
                            for key, values in location_names.iteritems():
                                try:
                                    # # TODO - ADD META DATA
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
                            # print docs
                        except Exception as e:
                            print traceback.format_exc()
                            pass
                        
                        docs[str(t['id'])] = points
                        # loop tika server ends
                    status = IndexCrawledPoints(core_name, docs)
                    print status
                    # loop solr query ends
                gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
                return HttpResponse(status=200, content= ("Crawled data geo parsed successfully."))
            except Exception as e:
                print traceback.format_exc()
                print e
                return HttpResponse(status=500, content= ("Error while geo parsing crawled data."))

    else:
        return HttpResponse(status=500, content= ("Only solr indexes supported for now"))
    

def search_crawled_index(request, indexed_path, domain_name, username, passwd, keyword):
    '''
    Searches a 'keyword' in 'indexed_path', using 'username', 'passwd'
    '''
    print "Searching for {0} in {1}".format(keyword, indexed_path)

    keyword = urllib.quote_plus(keyword)

    url = "{0}/select?q=*{1}*&wt=json&rows=1".format(indexed_path, keyword)
    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
    
    if r.status_code != 200:
        return HttpResponse(status=r.status_code, content=r.reason)
    
    response = r.json()
    numFound = response['response']['numFound']
    list_id = []
    print "Total number of records found {0}".format(numFound)
    
    # limiting search count to MAX_SEARCH_RESULT 
    if numFound > MAX_SEARCH_RESULT:
        numFound = MAX_SEARCH_RESULT
        print "Processing only {0} records".format(numFound)
        
    for row in range(0, int(numFound), QUERY_RANGE):  # loop solr query
        docs = {}
        url = "{0}/select?q=*{1}*&start={2}&rows={3}&wt=json&fl=id".format(indexed_path, keyword, row, QUERY_RANGE)
        print "solr query - {0}".format(url)
        r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
        response = r.json()
        docs = response['response']['docs']
        
        list_id += [doc["id"] for doc in docs]
    
    #To get the local Solr core name from domain name and index path
    core_name,_,_ = get_index_core(domain_name, indexed_path)
    
    khooshe_tile_folder_name,points_count = SearchLocalSolrIndex(core_name, list_id, keyword)
    
    result = create_khooshe_result(len(list_id), GetIndexSize(core_name), points_count,
                                    get_idx_field_csv(domain_name, indexed_path), khooshe_tile_folder_name)
    
    if khooshe_tile_folder_name:
        return HttpResponse(status=200, content="[{0}]".format(str(result)))
    else:
        return HttpResponse(status=404, content="No points found for given search")


def list_of_searched_tiles(request):
    '''
    Returns list of Khooshe tiles generated from previous search keywords"
    '''
    main_dir = os.path.realpath("manage.py").split("manage.py")[0]
    search_tiles_dir = "{0}geoparser_app/static/search/tiles/".format(main_dir)
    try:
        return HttpResponse(status=200, content="{0}".format([name for name in os.listdir(search_tiles_dir) if os.path.isdir("{0}/{1}".format(search_tiles_dir,name))]))
    except:
        return HttpResponse(status=200, content="No search folder found.")


def remove_khooshe_tile(request, tiles_path, khooshe_folder):
    '''
    Remove the Khooshe tile folder.
    '''
    main_dir = os.path.realpath("manage.py").split("manage.py")[0]
    search_tiles_dir = "{0}{1}".format(main_dir, tiles_path)
    existing_folders = [name for name in os.listdir(search_tiles_dir) if os.path.isdir("{0}/{1}".format(search_tiles_dir,name))]
    try:
        if khooshe_folder in existing_folders:
            shutil.rmtree('{0}/{1}'.format(search_tiles_dir, khooshe_folder))
            return HttpResponse(status=200, content="Folder {0} successfully removed.".format(khooshe_folder))
        else:
            return HttpResponse(status=200, content="Folder does not exists.")
    except:
        return HttpResponse(status=404, content="Something went wrong. (maybe tiles folder does not exists.")
