
<p align="center">
  <img src="https://raw.githubusercontent.com/MBoustani/GeoParser/master/logo.png"  width="250"/>
</p>
# GeoParser
Extract and Visualize location from any text file

##How to Install 

###Requirements
-Python 2.7 

-pip 

-Girder

###Instructions

1. pip install -r requirements.txt
2. [Install Girder] (http://girder.readthedocs.org/en/latest/prerequisites.html)

###How to Run the Application
1- Run the app
```
python app.py
```

2. Make sure MongoDB is running
```
Mongod &
```
3. Run Girder:
```
girder-server -p 8081
```
4. Open in browser [http://localhost:8080/](http://localhost:8080/)

## Technologies we Use
- [Apache Tika](https://github.com/chrismattmann/tika-python)
- [Geograpy](https://github.com/ushahidi/geograpy)
- [Geopy](https://github.com/geopy/geopy)


