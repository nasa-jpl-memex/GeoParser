
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

2.Run Dajgno server

```
python manage.py runserver
```

3.Open in browser [http://localhost:8080/](http://localhost:8080/)

## Technologies we Use
- [Apache Tika](https://github.com/chrismattmann/tika-python)
- [Geograpy](https://github.com/ushahidi/geograpy)
- [Geopy](https://github.com/geopy/geopy)


