#!/bin/bash

CORE=${1:-covid19}

CMD="cd /home/Solr/solr-5.3.1/ && ./bin/solr create_core -c $CORE"
docker exec -it docker_memex-geoparser_1 bash -c "$CMD"
