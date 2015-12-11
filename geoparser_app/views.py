from django.shortcuts import render
import glob, os
import urllib2
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
import geograpy
from geograpy import extraction
from geograpy import places
from geopy.geocoders import Nominatim

geolocator = Nominatim()
flip = True

APP_NAME = "geoparser_app"
UPLOADED_FILES_PATH = "static/uploaded_files"
SUBDOMAIN = ""


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
    return HttpResponse(status=200, content=str(domains))


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
            e = extraction.Extractor(text=text_content)
            e.find_entities()
            status = IndexLocationName(file_name, e.places)
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
            for location in location_names:
                try:
                    geolocation = geolocator.geocode(location)
                    points.append(
                        {'loc_name': location,
                        'position':{
                            'x': geolocation.longitude,
                            'y': geolocation.latitude
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
            location_names = []
            points = []
            query_range = 500
            try:
                url = "{0}/select?q=*%3A*&wt=json&rows=1".format(indexed_path)
                response = urllib2.urlopen(url)
                numFound = eval(response.read())['response']['numFound']
                for row in range(0, int(numFound), query_range):
                    query_url = "{0}/select?q=*%3A*&start={1}&rows={2}&wt=json".format(indexed_path, row, row+query_range)
                    places = geograpy.get_place_context(url=query_url)
                    location_names.append(places.regions)
                    location_names.append(places.countries)
                    location_names.append(places.cities)
                    location_names.append(places.other)
                    location_names = flatten(location_names)
                print "Found {0} Locations for {1}".format(len(location_names), indexed_path)
                print "Finding coordinates.." 
                for location in location_names:
                    try:
                        geolocation = geolocator.geocode(location)
                        points.append(
                            {'loc_name': "{0}".format(location),
                            'position':{
                                'x': geolocation.longitude,
                                'y': geolocation.latitude
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
