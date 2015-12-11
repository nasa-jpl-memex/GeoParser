
<p align="center">
  <img src="https://raw.githubusercontent.com/MBoustani/GeoParser/master/logo.png"  width="250"/>
</p>
# GeoParser
Geoparser extracts locations, such as cities or geographic coordinates expressed as latitude-longitude from any file and visualizes the points on a map. 

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


