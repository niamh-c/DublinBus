import pymysql
import json
import sys
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
connection = pymysql.connect(host=os.getenv("HOST"),
                             user=os.getenv("USER"),
                             password=os.getenv("PASSWORD"),
                             db='website',
                             cursorclass=pymysql.cursors.DictCursor)
with open('frontEndBusInfo.json') as json_file:
        data = json.load(json_file)

try:
    with connection.cursor() as cursor:
        for stop in data:
            for route in data[stop]['routes'][0]:
                sql = "INSERT INTO routes_per_stop (route_id, stop_id) VALUES (%s, %s)"
                cursor.execute(sql, (route, stop))
            connection.commit()

finally:
    connection.close()
