#!/bin/bash

DEPLOY_HOME=/home
mkdir /home/logs

pushd $DEPLOY_HOME
nohup lucene-geo-gazetteer -server  &
/home/Solr/solr-5.3.1/bin/solr start -p 8983 -h 127.0.0.1 &
python /home/manage.py runserver 0.0.0.0:8000 > $DEPLOY_HOME/logs/geoparser-server.log 2>&1&
java -classpath /home/location-ner-model:/home/geotopic-mime:/home/tika/tika-server/target/tika-server-2.0.0-SNAPSHOT.jar org.apache.tika.server.TikaServerCli -p 8001 -h 127.0.0.1 > $DEPLOY_HOME/logs/tika-server-geotopic.log 2>&1&
popd

tail -f $DEPLOY_HOME/logs/*

