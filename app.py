import os
import json
#from flask import Flask, request, redirect, url_for, render_template, jsonify
#from werkzeug import secure_filename
#from geo_tika import file_to_text, create_json, extract_loc_name, loc_name_lat_lon

import cherrypy

UPLOAD_FOLDER = 'static/uploaded_files'
JSON_FOLDER = 'static/json'

class GeoParser(object):
    @cherrypy.expose
    def upload(self):
        pass


    @cherrypy.expose
    def status(self):
        pass


    @cherrypy.expose
    def search(self):
        pass

    @cherrypy.expose
    def bookmark(self):
        pass


if __name__ == '__main__':
   cherrypy.quickstart(GeoParser())