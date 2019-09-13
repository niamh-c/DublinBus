import pymysql
import os
import sys
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
sql = "select stop_lat, zone_id, stop_lon, stop_id, stop_name, location_type, stopID_short from stops"
db = pymysql.connect(host=os.getenv("HOST"), port=3306 , user=os.getenv("USER"), passwd=os.getenv("PASSWORD"), db="website")
cursor = db.cursor()
cursor.execute(sql)
db.commit()
Data = cursor.fetchall()
for i in range(0, len(Data)):
    try:
        index=Data[i][3].find('DB')+2
        stop=Data[i][3][index:]
        stop=int(stop)
        sql = 'UPDATE stops SET stopID_short ='+str(stop)+' WHERE stop_id ="'+Data[i][3]+'"'
        db = pymysql.connect(host="csi420-01-vm9.ucd.ie", port=3306 , user="niamh", passwd="comp47360jnnd", db="website")
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(i)
        print(e)
cursor.close()
