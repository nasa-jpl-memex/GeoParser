#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mako
import json
import os

from girder import constants, events
from girder.utility.model_importer import ModelImporter
from girder.utility.webroot import Webroot

from girder.api.rest import Resource, loadmodel, RestException
from girder.api.describe import Description
from girder.api import access

from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon


from tika import parser
from geograpy import extraction
from geopy.geocoders import Nominatim

geolocator = Nominatim()


class GeoParserJobs(Resource):
    def __init__(self):
        self.resourceName = 'geoparser_jobs'
        self.route('GET', ("extract_text",), self.extractText)
        self.route('GET', ("find_location",), self.findLocation)
        self.route('GET', ("find_lat_lon",), self.findLatlon)
        self.route('GET', ("query_points",), self.QueryPoints)


    @access.public
    def extractText(self, params):
        '''
        Using Tika to extract text from given file
        and return the text content.
        '''
        file_name = params['file_name']
        parsed = parser.from_file(file_name)
        status = IndexUploadedFilesText(file_name, parsed["content"])
        if status[0]:
            return {'job':'text_extraction', 'status': 'successful', 'comment':'Text extracted and indexed to Solr.'}
        else:
            return {'job':'text_extraction', 'status': 'unsuccessful', 'comment':status[1]}
    extractText.description = (
        Description('Extract text')
    )


    @access.public
    def findLocation(self, params):
        '''
        Find location name from extracted text using Geograpy.
        '''
        file_name = params['file_name']
        text_content = QueryText(file_name)
        if text_content:
            e = extraction.Extractor(text=text_content)
            e.find_entities()
            status = IndexLocationName(file_name, e.places)
            if status[0]:
                return {'job':'find_location', 'status': 'successful', 'comment':'Location/s found and indexed to Solr.'}
            else:
                return {'job':'find_location', 'status': 'unsuccessful', 'comment':status[1]}
        else:
            return {'job':'find_location', 'status': 'unsuccessful', 'comment':'Cannot extract text.'}
    findLocation.description = (
        Description('Find location name')
    )


    @access.public
    def findLatlon(self, params):
        '''
        Find latitude and longitude from location name using GeoPy.
        '''
        file_name = params['file_name']
        location_names = QueryLocationName(file_name)
        if location_names:
            points = []
            for location in location_names:
                try:
                    geolocation = geolocator.geocode(location)
                    points.append(
                        {'loc_name': location,
                        'position':{
                            'x': geolocation.latitude,
                            'y': geolocation.longitude
                        }
                        }
                    )
                except:
                    pass
            status = IndexLatLon(file_name, points)
            if status[0]:
                return {'job':'find_lat_lon', 'status': 'successful', 'comment':'Latitude and Longitude found and indexed to Solr.'}
            else:
                return {'job':'find_lat_lon', 'status': 'unsuccessful', 'comment':status[1]}
        else:
            return {'job':'find_lat_lon', 'status': 'unsuccessful', 'comment':'Cannot find location name.'}
    findLatlon.description = (
        Description('Find latitude and longitude')
    )


    @access.public
    def QueryPoints(self, params):
        '''
        Return geopoints for given filename
        '''
    QueryPoints.description = (
        Description('Return geo points for given file name.')
    )


def load(info):
    info['apiRoot'].geoparser_jobs = GeoParserJobs()