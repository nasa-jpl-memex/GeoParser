
<p align="center">
  <img src="https://raw.githubusercontent.com/MBoustani/GeoParser/master/logo.png"  width="250"/>
</p>
# GeoParser
The Geoparser is a software tool that can process information from any type of file, extract geographic coordinates, and visualize locations on a map. Users who are interested in seeing a geographical representation of information or data can choose to search for locations using the Geoparser, through a search index or by uploading files from their computer. The Geoparser will parse the files and visualizes cities or latitude-longitude points on the map. After the information is parsed and points are plotted on the map, users are able to filter their results by density, or by searching a key word and applying a "facet" to the parsed information. On the map, users can click on location points to reveal more information about the location and how it is related to their search.

##Installation (manually)

###Requirements
-Python 2.7

-pip 

-Django 

-Apache Tika

###Instructions

Install python requirements
```
pip install -r requirements.txt
```

###How to Run the Application

1.Run Solr

Change directory to where you cloned the project
```
cd Solr/solr-5.3.1/
./bin/solr start
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
usage: lucene-geo-gazetteer
 -b,--build <gazetteer file>           The Path to the Geonames
                                       allCountries.txt
 -h,--help                             Print this message.
 -i,--index <directoryPath>            The path to the Lucene index
                                       directory to either create or read
 -s,--search <set of location names>   Location names to search the
                                       Gazetteer for
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
lucene-geo-gazetteer -s Pasadena Texas
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
Now start lucene-geo-gazetteer server
```
lucene-geo-gazetteer -server
```
4.Run tika server as mentioned in `https://wiki.apache.org/tika/GeoTopicParser` on port `8001`. Port can be configured via [config.txt](https://github.com/MBoustani/GeoParser/blob/master/config.txt)   

5.MAKE SURE YOU ARE ABLE TO EXTRACT LOCATIONS FROM TIKA SERVER   

`curl -T /path/to/polar.geot -H "Content-Disposition: attachment; filename=polar.geot" http://localhost:8001/rmeta`   

You can obtain [file here] (https://raw.githubusercontent.com/chrismattmann/geotopicparser-utils/master/geotopics/polar.geot)   

Output should be this
```
[
   {
      "Content-Type":"application/geotopic",
      "Geographic_LATITUDE":"39.76",
      "Geographic_LONGITUDE":"-98.5",
      "Geographic_NAME":"United States",
      "Optional_LATITUDE1":"27.33931",
      "Optional_LONGITUDE1":"-108.60288",
      "Optional_NAME1":"China",
      "X-Parsed-By":[
         "org.apache.tika.parser.DefaultParser",
         "org.apache.tika.parser.geo.topic.GeoParser"
      ],
      "X-TIKA:parse_time_millis":"1634",
      "resourceName":"polar.geot"
   }
]
```
6.Run Django server

```
python manage.py runserver
```

7.Open in browser [http://localhost:8000/](http://localhost:8000/)

## Technologies we Use
- [Apache Tika](https://github.com/chrismattmann/tika-python)
- [Lucene Geo Gazetteer] (https://github.com/chrismattmann/lucene-geo-gazetteer)
- Apache Solr


