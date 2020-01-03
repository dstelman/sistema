#!/bin/bash

now=$(date)
echo "$now" >> oi.txt
curl -o diego.txt -s -w "%{time_total}" http://192.168.0.68/ >> oi.txt && echo "quebra" >> oi.txt && echo "$now" >> oi.txt

#curl -o diego.txt -s -w "%{time_total}" -L http://192.168.0.58/ >> oi.txt && echo "quebra" >> oi.txt
#curl -L http://192.168.0.70:8080/
#curl --max-time 2 -L http://192.168.0.57/
