import os
import json
#from werkzeug import secure_filename
#from geo_tika import file_to_text, create_json, extract_loc_name, loc_name_lat_lon

import cherrypy

STATIC_FOLDER = "./static"
UPLOAD_FOLDER = 'static/uploaded_files'

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
    conf = {
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': STATIC_FOLDER
         }
     }
    cherrypy.quickstart(GeoParser(), conf)