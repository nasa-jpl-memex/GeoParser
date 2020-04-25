#!/bin/bash

wait_file() {
  local file="$1"; shift
  local wait_seconds="${1:-10}"; shift # 10 seconds as default timeout

  until test $((wait_seconds--)) -eq 0 -o -f "$file" ; do sleep 1; done

  ((++wait_seconds))
}

DEPLOY_HOME=/home
mkdir -p $DEPLOY_HOME/logs

pushd $DEPLOY_HOME
nohup lucene-geo-gazetteer -server &
/home/Solr/solr-5.3.1/bin/solr start -p 8983 -h 127.0.0.1 &
python /home/manage.py runserver 0.0.0.0:8000 > $DEPLOY_HOME/logs/geoparser-server.log 2>&1&
java -classpath /home/location-ner-model:/home/geotopic-mime:/home/tika/tika-server/target/tika-server-2.0.0-SNAPSHOT.jar org.apache.tika.server.TikaServerCli -p 8001 -h 127.0.0.1 > $DEPLOY_HOME/logs/tika-server-geotopic.log 2>&1&
popd

# Wait at most 5 seconds for the server.log file to appear
server_log=$DEPLOY_HOME/logs/geoparser-server.log
wait_file "$server_log" 5 || {
  echo "Geoparser log file missing after waiting for $? seconds: '$server_log'"
  exit 1
}

tail -f $DEPLOY_HOME/logs/*

