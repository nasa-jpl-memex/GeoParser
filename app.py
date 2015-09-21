import os
import json
#from werkzeug import secure_filename
#from geo_tika import file_to_text, create_json, extract_loc_name, loc_name_lat_lon

import cherrypy
import cgi
import tempfile


STATIC_FOLDER = "./static"
UPLOAD_FOLDER = "./static/uploaded_files/"

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


class GeoParser(object):

    @cherrypy.expose
    def index(self):
        """Simplest possible HTML file upload form. Note that the encoding
        type must be multipart/form-data."""

        return """
            <html>
            <body>
                <form action="upload" method="post" enctype="multipart/form-data">
                    File: <input type="file" name="theFile"/> <br/>
                    <input type="submit"/>
                </form>
            </body>
            </html>
            """

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
        theFile = formFields['theFile']
        os.link(theFile.file.name, UPLOAD_FOLDER + theFile.filename)

        return "ok, got it filename='%s'" % theFile.filename


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
        '/': {
            'tools.sessions.on': True
        },
        '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': STATIC_FOLDER
        }
    }

    # remove any limit on the request body size; cherrypy's default is 100MB
    # (maybe we should just increase it ?)
    cherrypy.server.max_request_body_size = 0

    # increase server socket timeout to 60s; we are more tolerant of bad
    # quality client-server connections (cherrypy's defult is 10s)
    cherrypy.server.socket_timeout = 60

    cherrypy.quickstart(GeoParser(), '/', conf)
