#!/bin/bash

CORE=${1:-covid19}

./create-core.sh $CORE
./add-fields.sh $CORE
