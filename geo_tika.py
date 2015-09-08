import os
import shlex
import subprocess
import json
import ast
import geograpy
from geograpy import extraction
from geopy.geocoders import Nominatim

import tika
from tika import parser

files_dir = 'static/uploaded_files'
tika_path = "/Users/MBoustani/Downloads/tika/tika-app/target/tika-app-1.10-SNAPSHOT.jar"

#to_geot_server = "http://localhost:9997/" #java -classpath /Users/MBoustani/Downloads/tika/tika-server/target/tika-server-1.10-SNAPSHOT.jar org.apache.tika.server.TikaServerCli --port 9997

geolocator = Nominatim()


def file_to_text(f):
    parsed = parser.from_file(f)
    #cmd = 'curl -T {0}/{1} -H "Content-Disposition: attachment; filename={1}" {2}rmeta'.format(files_dir, f, to_lat_lon_server)
    #return subprocess.check_output(cmd, shell=True)
    return parsed["content"]


def extract_loc_name(t):
    e = extraction.Extractor(text=t)
    e.find_entities()
    return e.places


def loc_name_lat_lon(loc_names):
    points = []
    for loc in loc_names:
        try:
            location = geolocator.geocode(loc)
            points.append([location.latitude, location.longitude,loc])
        except:
            pass
    return points


def create_json(points):
    json = '{"type": "FeatureCollection", "features": ['
    for point in points:
        json += """{"geometry": {"type": "Point","coordinates": [%s,%s]},"type": "Feature","properties": {"location": "%s"}},""" % (point[1],point[0], point[2])
    if json[-1]==",":
        json = json[:-1]
    json += ']}'
    return json


# def location_names(json_files):
#     loc_names = {}
#     for json_file in json_files:
#         with open(json_file, 'r') as f:
#             json_obj = list(f.readlines())
#             for each in json_obj:
#                 features = ast.literal_eval(each)['features']
#                 for feature in features:
#                     print feature['properties']['location']