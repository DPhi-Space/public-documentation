#!/bin/sh

echo "Hello from the container !"
ls -al /data

echo "I WANT TO DOWNLINK THIS FOR WHATEVER REASON" >/data/downlink.txt
echo "JOJO IS SO HANDSOME\n" >>/data/downlink.txt
wget -O - http://satellite-telemetry.dphi-tm:8000/health >>/data/downlink.txt
sleep 30

exit 0
