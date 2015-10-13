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


    def SolrIndexText(text):
        pass


    def SolrQueryText(file_name):
        pass


    def SolrIndexLocationName(places):
        pass


    def SolrQueryLocationName(file_name):
        pass


    def SolrIndexLatLon(points):
        pass


    @access.public
    def extractText(self, file_name):
        '''
        Using Tika to extract text from given file
        and return the text content.
        '''
        parsed = parser.from_file(file_name)
        SolrIndexText(parsed["content"])
        return {'data': 'Text Extracted'}
    extractText.description = (
        Description('Extract text')
    )


    @access.public
    def findLocation(self, file_name):
        '''
        Find location name from extracted text using Geograpy.
        '''
        text_content = SolrQueryText(file_name)
        e = extraction.Extractor(text=text_content)
        e.find_entities()
        SolrIndexLocationName(e.places)
        return {'data': 'Location name Found.'}
    findLocation.description = (
        Description('Find location name')
    )


    @access.public
    def findLatlon(self, file_name):
        '''
        Find latitude and longitude from location name using GeoPy.
        '''
        location_names = SolrQueryLocationName(file_name)
        points = []
        for location in location_names:
            try:
                geolocation = geolocator.geocode(location)
                points.append([geolocation.latitude, geolocation.longitude,location])
            except:
                pass
        SolrIndexLatLon(points)
        return {'data': 'Latitude and longitude Found.'}
    findLatlon.description = (
        Description('Find latitude and longitude')
    )


def load(info):
    info['apiRoot'].geoparser_jobs = GeoParserJobs()