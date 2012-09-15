#!/bin/bash

# check scripts/debian-init.d
# for 'daemon' version

export PYTHONPATH=`dirname $0`
twistd -n cyclone -p 8888 -l 0.0.0.0 \
       -r pbserver.web.Application -c pbserver.conf $*
