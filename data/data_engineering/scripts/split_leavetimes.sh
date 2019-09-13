#!/bin/bash
OFFSET=25000000
for i in {2}
do
	FILENAME=test
	NAME=${FILENAME}_${i}.txt
	tail -n +$OFFSET rt_leavetimes_DB_2018.txt | head -n 25000001 | awk -F";" '{print $2"," $3"," $4"," $5"," $6"," $7"," $8"," $9}' > $NAME
	zip $NAME.zip $NAME
	rm $NAME 
	OFFSET=$((OFFSET+25000000))
done
