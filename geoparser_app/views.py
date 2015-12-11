from django.shortcuts import render
import glob, os
import urllib2
import ast
import requests
from compiler.ast import flatten
from os.path import isfile
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from .forms import UploadFileForm
from .models import Document
from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon, QueryPoints, IndexFile, create_core, IndexStatus, IndexCrawledPoints, get_all_cores, get_domains_urls

from tika import parser

flip = True

APP_NAME = "geoparser_app"
UPLOADED_FILES_PATH = "static/uploaded_files"
STATIC = "static"
TIKA_APP = "tika/tika-app/target/tika-app-1.12-SNAPSHOT.jar"
SUBDOMAIN = ""
geotopic_server = "http://localhost:9997/"
headers = {"content-type" : "application/json" }
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
            domains[core] = ids
    return HttpResponse(status=200, content=str(domains))


def parse_lat_lon(locations):
    points = {}
    lines = locations.split("\n")
    Geographic_NAME = None
    for line in lines:
        if len(line.split("Geographic_NAME:")) == 2:
            Geographic_NAME = line.split("Geographic_NAME:")[1]
        if len(line.split("Geographic_LONGITUDE:")) == 2:
            Geographic_LONGITUDE = line.split("Geographic_LONGITUDE:")[1]
        if len(line.split("Geographic_LATITUDE:")) == 2:
            Geographic_LATITUDE = line.split("Geographic_LATITUDE:")[1]
    if Geographic_NAME:
        points[Geographic_NAME.replace(" ","")] = [Geographic_LATITUDE.replace(" ",""), Geographic_LONGITUDE.replace(" ","")]

    optional_count = locations.count("Optional_NAME")
    for num in range(1, optional_count+1):
        Optional_NAME = None
        for line in lines:
            if len(line.split("Optional_NAME{0}:".format(str(num)))) == 2:
                Optional_NAME = line.split("Optional_NAME{0}:".format(str(num)))[1]
            if len(line.split("Optional_LONGITUDE{0}:".format(str(num)))) == 2:
                Optional_LONGITUDE = line.split("Optional_LONGITUDE{0}:".format(str(num)))[1]
            if len(line.split("Optional_LATITUDE{0}:".format(str(num)))) == 2:
                Optional_LATITUDE = line.split("Optional_LATITUDE{0}:".format(str(num)))[1]
        if Optional_NAME:
            points[Optional_NAME.replace(" ","")] = [Optional_LATITUDE.replace(" ",""), Optional_LONGITUDE.replace(" ","")]

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
            with open("{0}/{1}/tmp.txt".format(APP_NAME, STATIC), 'w') as f:
                f.write(text_content)
                f.close()
            cmd = "java -classpath {0}/{1}:{0}/GeoTopicParser/location-ner-model/:{0}/GeoTopicParser/geotopic-mime/ org.apache.tika.cli.TikaCLI -m {0}/{2}/tmp.txt".format(APP_NAME, TIKA_APP, STATIC)
            locations = os.popen(cmd).read()
            points = parse_lat_lon(locations)
            status = IndexLocationName(file_name, points)
            os.remove("{0}/{1}/tmp.txt".format(APP_NAME, STATIC))
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
                        {'loc_name': key,
                        'position':{
                            'x': values[1],
                            'y': values[0]
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


def return_points(request, file_name, core_name):
    '''
        Returns geo point for give file
    '''
    points = QueryPoints(file_name, core_name)

    if points:
        return HttpResponse(status=200, content=points)
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude.")


def query_crawled_index(request, core_name, indexed_path):
    '''
        To query crawled data that has been indexed into
        Solr or Elastichsearch and return location names
    '''
    if "solr" in indexed_path.lower():
        if IndexFile(core_name, indexed_path.lower()):
            points = []
            query_range = 500
            text_content = ""
            try:
                url = "{0}/select?q=*%3A*&wt=json&rows=1".format(indexed_path)
                response = urllib2.urlopen(url)
                numFound = eval(response.read())['response']['numFound']
                for row in range(0, int(numFound), query_range):
                    url = "{0}/select?q=*%3A*&start={1}&rows={2}&wt=json".format(indexed_path, row, row+query_range)
                    r = requests.get(url, headers=headers)
                    response = r.json()
                    text = response['response']['docs']
                    text_content = text_content + str(text)
                with open("{0}/{1}/tmp.txt".format(APP_NAME, STATIC), 'w') as f:
                    f.write(str(text_content))
                    f.close()
                cmd = "java -classpath {0}/{1}:{0}/GeoTopicParser/location-ner-model/:{0}/GeoTopicParser/geotopic-mime/ org.apache.tika.cli.TikaCLI -m {0}/{2}/tmp.txt".format(APP_NAME, TIKA_APP, STATIC)
                locations = os.popen(cmd).read()
                location_names = parse_lat_lon(locations)
                os.remove("{0}/{1}/tmp.txt".format(APP_NAME, STATIC))
                for key, values in location_names.iteritems():
                    try:
                        points.append(
                            {'loc_name': key,
                            'position':{
                                'x': values[1],
                                'y': values[0]
                            }
                            }
                        )
                    except:
                        pass
                print "Found {0} coordinates..".format(len(points))
                status = IndexCrawledPoints(core_name, indexed_path.lower(), points)
                return HttpResponse(status=200, content=status)
            except Exception as e:
                return False
    else:
        pass
