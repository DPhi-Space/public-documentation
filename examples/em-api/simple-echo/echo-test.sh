#!/bin/sh

echo "Hello from the container !"
ls -al /data

echo "Is this the final frontier?" >/data/downlink.txt
wget -O - http://satellite-telemetry.dphi-tm/health >>/data/downlink.txt
wget -O - http://satellite-telemetry.dphi-tm/api/telemetry/latest	 >>/data/orbital.json
sleep 30

exit 0
