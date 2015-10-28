
<p align="center">
  <img src="https://raw.githubusercontent.com/MBoustani/GeoParser/master/logo.png"  width="250"/>
</p>
# GeoParser

The Geoparser is a sofware tool that can process information from any type of file, extract geographic coordinates, and visualize locations on a map. Users who are interested in seeing a geographical representation of information or data can choose to search for locations using the Geoparser, through a search index or by uploading files from their computer. The Geoparser will parse the files and visualizes cities or latitude-longitude points on the map. After the infromation is parsed and points are plotted on the map, users are able to filter their results by density, or by searching a key word and applying a "facet" to the parsed information. On the map, users can click on location points to reveal more information about the location and how it is related to their search. 

##How to Install 

###Requirements
-Python 2.7 

-pip 

-Girder

###Instructions

1. Install python requirements
```
pip install -r requirements.txt
```
2. [Install Girder] (http://girder.readthedocs.org/en/latest/prerequisites.html)

###How to Run the Application

1. Run MongoDB
```
Mongod &
```

2. Run Solr
Change directory to where you cloned the project
```
Solr/solr-5.3.1/bin/solr start
```

3. Run Girder
```
girder-server -p 8081
```

4. Run the app
```
python app.py
```

5. Open in browser [http://localhost:8080/](http://localhost:8080/)

## Technologies we Use
- [Apache Tika](https://github.com/chrismattmann/tika-python)
- [Geograpy](https://github.com/ushahidi/geograpy)
- [Geopy](https://github.com/geopy/geopy)


