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


class GeoParserJobs(Resource):
    def __init__(self):
        self.resourceName = 'geoparser_jobs'
        self.route('GET', ("extract_text",), self.extractText)
        self.route('GET', ("find_location",), self.findLocation)
        self.route('GET', ("find_lat_lon",), self.findLatlon)

    @access.public
    def extractText(self, params):
        ## Run Tika text extraction
        return {'data': 'some text'}
    extractText.description = (
        Description('Extract text')
    )

    @access.public
    def findLocation(self, params):
        # Run Geograpy location name finder from text
        return {'data': 'some location'}
    findLocation.description = (
        Description('Find location name')
    )

    @access.public
    def findLatlon(self, params):
        # Run Geopy latitude and longitude finder from location name
        return {'data': 'some lat lon'}
    findLatlon.description = (
        Description('Find latitude and longitude')
    )


def load(info):
    info['apiRoot'].geoparser_jobs = GeoParserJobs()