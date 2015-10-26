from django.shortcuts import render
import glob, os
from os.path import isfile
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from geoparser_app.models import Document
from geoparser_app.forms import DocumentForm

from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon, QueryPoints

from tika import parser
from geograpy import extraction
from geopy.geocoders import Nominatim

geolocator = Nominatim()
flip = True


def index(request):
    context = {'title': "GeoParser"}
    
    return render(request, 'index.html', context)


def upload_file(request):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             newdoc = Document(docfile = request.FILES['docfile'])
#             uploaded_file_name = newdoc.docfile.name
#             newdoc.save()
#             return HttpResponseRedirect('/upload_file/{0}'.format(uploaded_file_name))
#     else:
#         form = DocumentForm()
#     return render_to_response('index.html', {'form': form})
    return HttpResponse(status=200, content="Uploaded")


def upload_file(request, uploaded):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             newdoc = Document(docfile = request.FILES['docfile'])
#             uploaded_file_name = newdoc.docfile.name
#             newdoc.save()
#             return HttpResponseRedirect('/upload_file/{0}'.format(uploaded_file_name))
#     else:
#         form = DocumentForm()
#     return render_to_response('index.html', {'form': form})
    return HttpResponse(status=200, content="Uploaded POST")

def extract_text(request, file_name):
    '''
        Using Tika to extract text from given file
        and return the text content.
    '''
    return HttpResponse(status=200, content="Text extracted.")
#     parsed = parser.from_file(file_name)
#     status = IndexUploadedFilesText(file_name, parsed["content"])
#     if status[0]:
#         return HttpResponse(status=200, content="Text extracted.")
#     else:
#         return HttpResponse(status=400, content="Cannot extract text.")


def find_location(request, file_name):
    '''
        Find location name from extracted text using Geograpy.
    '''
    return HttpResponse(status=200, content="Location/s found and index to Solr. " + file_name)
#     text_content = QueryText(file_name)
#     if text_content:
#         e = extraction.Extractor(text=text_content)
#         e.find_entities()
#         status = IndexLocationName(file_name, e.places)
#         if status[0]:
#             return HttpResponse(status=200, content="Location/s found and index to Solr.")
#         else:
#             return HttpResponse(status=400, content=status[1])
#     else:
#         return HttpResponse(status=400, content="Cannot find location.")



def find_latlon(request, file_name):
    '''
    Find latitude and longitude from location name using GeoPy.
    '''
    return HttpResponse(status=200, content="Latitude and longitude found.")
#     location_names = QueryLocationName(file_name)
#     if location_names:
#         points = []
#         for location in location_names:
#             try:
#                 geolocation = geolocator.geocode(location)
#                 points.append(
#                     {'loc_name': location,
#                     'position':{
#                         'x': geolocation.latitude,
#                         'y': geolocation.longitude
#                     }
#                     }
#                 )
#             except:
#                 pass
#         status = IndexLatLon(file_name, points)
#         if status[0]:
#             return HttpResponse(status=200, content="Latitude and longitude found.")
#         else:
#             return HttpResponse(status=400, content="Cannot find latitude and longitude.")
#     else:
#         return HttpResponse(status=400, content="Cannot find latitude and longitude.")


def return_points(request, file_name):
    '''
        Returns geo point for give file
    '''
    #Madhav put your fake JSON here and return to client and map
    print file_name
    if(file_name == 'File2.txt'):
        return HttpResponse(status=200, content="[{\"y\":28.615019,\"x\":77.234914,\"content\":\"Ref Text 3\",\"location\":\"New Delhi, India\"},{\"y\":35.695060,\"x\":51.386888,\"content\":\"Ref Text 4\",\"location\":\"Tehran, Iran\"}]")
    
    return HttpResponse(status=200, content="[{\"y\":45.767850939271945,\"x\":-103.5755255809404,\"content\":\"Ref Text 1\",\"location\":\"North Harding, South Dakota\"},{\"y\":32.531870132266306,\"x\":-109.21120923437086,\"content\":\"Ref Text 2\",\"location\":\"Greenlee County, Arizona\"}]")

