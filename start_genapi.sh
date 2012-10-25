#!/bin/bash

CWD=`dirname $0`
python $CWD/genapi/genapi_runner.py $*
