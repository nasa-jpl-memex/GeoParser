#!/bin/bash

CORE=${1:-covid19}

curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field":{"name":"text","type":"text_ws","stored":true, "multiValued":true }}' http://localhost:8983/solr/$CORE/schema
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field":  {"name":"points","type":"point","multiValued":true,"stored":true}}' http://localhost:8983/solr/$CORE/schema
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field":{"name":"locations","type":"string","multiValued":true,"stored":true}}' http://localhost:8983/solr/$CORE/schema
