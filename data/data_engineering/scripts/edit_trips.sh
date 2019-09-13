#!/bin/bash
FILENAME=test
NAME=${FILENAME}_${i}.txt
awk -F";" '{print $2"," $3"," $4"," $5"," $6"," $7"," $8"," $9}' > $NAME

 

