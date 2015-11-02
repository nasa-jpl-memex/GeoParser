from django.shortcuts import render
import glob, os
from os.path import isfile
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from .forms import UploadFileForm
from .models import Document
from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon, QueryPoints, IndexFile, create_core, IndexStatus

from tika import parser
from geograpy import extraction
from geopy.geocoders import Nominatim

geolocator = Nominatim()
flip = True

COLLECTION_NAME = "uploaded_files"


def index(request):
    if create_core(COLLECTION_NAME):
        context = {'title': "GeoParser"}
        return render(request, 'index.html', context)
    else:
        return HttpResponse(status=400, content="Cannot create uploaded_files core.")


def upload_file(request, file_name):
    if IndexFile(file_name):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, content="Cannot upload file.")


def list_of_uploaded_files(request):
    '''
    Return list of uploaded files and status of geoparsed
    '''
    return HttpResponse(status=200, content="[filenames]")


def extract_text(request, file_name):
    '''
        Using Tika to extract text from given file
        and return the text content.
    '''
    if "false" in IndexStatus("text", file_name):
        parsed = parser.from_file("geoparser_app/static/uploaded_files/{0}".format(file_name))
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
    if "false" in IndexStatus("locations", file_name):
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
    if "false" in IndexStatus("points", file_name):
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


def return_points(request, file_name):
    '''
        Returns geo point for give file
    '''
    points = QueryPoints(file_name)

    if points:
        return HttpResponse(status=200, content='['+points+']')
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude.")
