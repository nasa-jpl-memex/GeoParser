
<p align="center">
  <img src="https://raw.githubusercontent.com/MBoustani/GeoParser/master/logo.png"  width="250"/>
</p>
# GeoParser
The Geoparser is a sofware tool that can process information from any type of file, extract geographic coordinates, and visualize locations on a map. Users who are interested in seeing a geographical representation of information or data can choose to search for locations using the Geoparser, through a search index or by uploading files from their computer. The Geoparser will parse the files and visualizes cities or latitude-longitude points on the map. After the infromation is parsed and points are plotted on the map, users are able to filter their results by density, or by searching a key word and applying a "facet" to the parsed information. On the map, users can click on location points to reveal more information about the location and how it is related to their search.

##How to Install 

###Requirements
-Python 2.7 

-pip 

- Django 

- Apache Tika

###Instructions

Install python requirements
```
pip install -r requirements.txt
```

###How to Run the Application

1.Run Solr

Change directory to where you cloned the project
```
Solr/solr-5.3.1/bin/solr start
```

2.Clone lucene-geo-gazetteer repo
```
git clone https://github.com/chrismattmann/lucene-geo-gazetteer.git
cd lucene-geo-gazetteer
mvn install assembly:assembly
add lucene-geo-gazetteer/src/lucene-geo-gazetteer/src/main/bin to your PATH environment variable
```
make sure it is working
```
lucene-geo-gazetteer --help
```

3.You will now need to build a Gazetteer using the Geonames.org dataset. (1.2 GB)
```
cd lucene-geo-gazetteer/src/lucene-geo-gazetteer
curl -O http://download.geonames.org/export/dump/allCountries.zip
unzip allCountries.zip
lucene-geo-gazetteer -i geoIndex -b allCountries.txt
```
make sure it is working
```
ucene-geo-gazetteer -s Pasadena Texas
[
{"Texas" : [
"Texas",
"-91.92139",
"18.05333"
]},
{"Pasadena" : [
"Pasadena",
"-74.06446",
"4.6964"
]}
]
```
.Run Dajgno server

```
python manage.py runserver
```

3.Open in browser [http://localhost:8000/](http://localhost:8000/)

## Technologies we Use
- [Apache Tika](https://github.com/chrismattmann/tika-python)
- [Geograpy](https://github.com/ushahidi/geograpy)
- [Geopy](https://github.com/geopy/geopy)


