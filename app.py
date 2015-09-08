import os
import json
from flask import Flask, request, redirect, url_for, render_template, jsonify
from werkzeug import secure_filename
from geo_tika import file_to_text, create_json, extract_loc_name, loc_name_lat_lon

UPLOAD_FOLDER = 'static/uploaded_files'
JSON_FOLDER = 'static/json'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

HOST = ""

def get_uploaded_files():
    files = {}
    for item in os.listdir(UPLOAD_FOLDER):
        if not item.startswith('.'):
            files[item.split('.')[0]] = item
    return files


def get_json_files():
    jsons = os.listdir(JSON_FOLDER)
    jsons_name = []
    for each in jsons:
        if each.split(".")[-1] == "json":
            jsons_name.append('{0}/{1}'.format(JSON_FOLDER, each))
    return jsons_name


@app.route('/')
def index():
    uploaded_files = get_uploaded_files()
    json_files = get_json_files()
    #loc_names = location_names(json_files)
    return render_template('index.html',uploaded_files=uploaded_files, json_files=json_files)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    uploaded_files = get_uploaded_files()
    json_files = get_json_files()
    return render_template('index.html',uploaded_files=uploaded_files, json_files=json_files)


@app.route('/remove/<f>')
def remove_file(f):
    uploaded_files = get_uploaded_files()
    os.remove("{0}/{1}".format(UPLOAD_FOLDER, uploaded_files[f]))
    json_name = "{0}/{1}.json".format(JSON_FOLDER, f)
    if os.path.isfile(json_name):
        os.remove(json_name)
    return redirect(url_for('index'))


@app.route('/extract_text/<f>')
def extract_text(f):
    uploaded_files = get_uploaded_files()
    global text
    text = file_to_text(uploaded_files[f])
    return jsonify(out='Text Extracted')


@app.route('/find_loc_name/<f>')
def find_loc_name(f):
    global text
    global loc_names
    loc_names = extract_loc_name(text)
    return jsonify(out='Location Name Found')


@app.route('/find_lat_lon/<f>')
def find_lat_lon(f):
    global loc_names
    global points
    points = loc_name_lat_lon(loc_names)
    return jsonify(out='LAT/LON Extracted')


@app.route('/create_geojson/<f>')
def create_geojson(f):
    global points
    geojson = create_json(points)
    geojson_file = "{0}/{1}.json".format(JSON_FOLDER, f)
    with open(geojson_file, 'w') as f:
        f.write(geojson)
        f.close()
    del geojson
    text = ""
    return jsonify(out='GeoJSON Created', geojson_file=geojson_file)


if __name__ == "__main__":
    app.debug = True
    app.run()
    text = ""
    loc_names = ""
    points = ""
