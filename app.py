import os
import cherrypy

from girder.models.user import User
from girder.models.collection import Collection
from girder.models.folder import Folder

from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'])


STATIC_FOLDER = "./static"
UPLOAD_FOLDER = "./static/uploaded_files/"
CURRENT_DIR = os.getcwd()

GIRDER_USERNAME = "girder"
GIRDER_PASSWORD = "girder"

GIRDER_COLLECTION = "GeoParser_Upload_Files"



class GeoParser(object):

    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template("index.html")
        return tmpl.render(salutation="Hello", target="World")



if __name__ == '__main__':

    girderUser = User()
    girderCollection = Collection()
    girderFolder = Folder()

    currentUser = girderUser.getAdmins()[0]
    existinig_collections = [each['name'] for each in girderCollection.list()]

    if len(existinig_collections) == 0 or not GIRDER_COLLECTION in existinig_collections:
        girderCollection.createCollection(GIRDER_COLLECTION, currentUser)
        existinig_collections = [each['name'] for each in girderCollection.list()]
    else:
        print "ERROR: Cannot create Collection. User not registered or logged in."

    for collection in girderCollection.list():
        if collection['name'] == GIRDER_COLLECTION:
            girderFolder.createFolder(collection, 'uploaded_files', description="uploaded files", parentType='collection')
        else:
            print "WARNING: Uploaded_Files folder already exists."

    main_conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': CURRENT_DIR
            },
            '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': STATIC_FOLDER
            }
    }


    cherrypy.server.max_request_body_size = 0
    cherrypy.server.socket_timeout = 60

    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                            'server.socket_port': 8080})

    cherrypy.tree.mount(GeoParser(), '/', main_conf)

    cherrypy.engine.start()
    cherrypy.engine.block()
