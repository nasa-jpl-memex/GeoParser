import os
import json
#from werkzeug import secure_filename
#from geo_tika import file_to_text, create_json, extract_loc_name, loc_name_lat_lon

import cherrypy
import cgi
import tempfile
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'])


STATIC_FOLDER = "./static"
UPLOAD_FOLDER = "./static/uploaded_files/"
CURRENT_DIR = os.getcwd()


class myFieldStorage(cgi.FieldStorage):
    """Our version uses a named temporary file instead of the default
    non-named file; keeping it visibile (named), allows us to create a
    2nd link after the upload is done, thus avoiding the overhead of
    making a copy to the destination filename."""

    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile()


def noBodyProcess():
    """Sets cherrypy.request.process_request_body = False, giving
    us direct control of the file upload destination. By default
    cherrypy loads it to memory, we are directing it to disk."""
    cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)


def get_uploaded_files():
    """
    This function returns list of uploaded files.
    """
    list_of_uploaded_files = []
    for item in os.listdir(UPLOAD_FOLDER):
        if not item.startswith('.'):
            list_of_uploaded_files.append(item)
    print list_of_uploaded_files
    return list_of_uploaded_files


class GeoParser(object):

    @cherrypy.expose
    def index(self):
        """Simplest possible HTML file upload form. Note that the encoding
        type must be multipart/form-data."""

        tmpl = lookup.get_template("index.html")
        return tmpl.render(salutation="Hello", target="World")


    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    def upload(self, theFile=None):
        """upload action

        We use our variation of cgi.FieldStorage to parse the MIME
        encoded HTML form data containing the file."""

        # the file transfer can take a long time; by default cherrypy
        # limits responses to 300s; we increase it to 1h
        cherrypy.response.timeout = 3600

        # convert the header keys to lower case
        lcHDRS = {}
        for key, val in cherrypy.request.headers.iteritems():
            lcHDRS[key.lower()] = val

        # at this point we could limit the upload on content-length...
        # incomingBytes = int(lcHDRS['content-length'])

        # create our version of cgi.FieldStorage to parse the MIME encoded
        # form data where the file is contained
        formFields = myFieldStorage(fp=cherrypy.request.rfile,
                                    headers=lcHDRS,
                                    environ={'REQUEST_METHOD':'POST'},
                                    keep_blank_values=True)

        # we now create a 2nd link to the file, using the submitted
        # filename; if we renamed, there would be a failure because
        # the NamedTemporaryFile, used by our version of cgi.FieldStorage,
        # explicitly deletes the original filename
        theFile = formFields.list[0] # TODO: This is to be reviewed
        os.link(theFile.file.name, UPLOAD_FOLDER + theFile.filename)

        return "ok, got it filename='%s'" % theFile.filename


class Status:

    exposed = True

    def GET(self, status=None):
        print status


class Search:

    exposed = True

    def GET(self, search=None):
        print search


if __name__ == '__main__':

    main_conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': CURRENT_DIR
            },
            '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': STATIC_FOLDER
            },
            '/favicon.ico':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': CURRENT_DIR + '/logo.png'
            }
    }

    status_conf = {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
    }

    search_conf = {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
    }


    cherrypy.server.max_request_body_size = 0
    cherrypy.server.socket_timeout = 60

    cherrypy.tree.mount(GeoParser(), '/', main_conf)
    cherrypy.tree.mount(Status(), '/status', status_conf)
    cherrypy.quickstart(Search(), '/search', search_conf)

    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                            'server.socket_port': 8080,
                            })

    cherrypy.engine.start()
    cherrypy.engine.block()
