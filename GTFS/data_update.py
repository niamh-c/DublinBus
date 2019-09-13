import sqlalchemy as db
import time
import datetime as dt
from insert_GTFS import *
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
engine = db.create_engine('mysql+pymysql://'+os.getenv("USER")+':'+os.getenv("PASSWORD")+'@'+os.getenv("HOST")+':3306/website')
timestamp=0
files=[{'file_name':'calendar.txt', 'table':'calendar', 'drop':None,
        'dtypes':{'service_id':db.String(45), 'start_date':db.String(45), 'end_date':db.String(45),
                  'monday':db.Integer(),'tuesday':db.Integer(), 'wednesday':db.Integer(), 'thursday':db.Integer(),
                  'friday':db.Integer(), 'saturday':db.Integer(), 'sunday':db.Integer()}},
       {'file_name':'calendar_dates.txt','table':'calendar_dates', 'drop':None,
        'dtypes':{'service_id':db.String(45),'date':db.String(45),'exception_type':db.Integer()}},
       {'file_name':'routes.txt','table':'routes', 'drop':['agency_id', 'route_type'],
        'dtypes':{'route_id':db.String(45),'route_short_name':db.String(45),'route_long_name':db.String(100)}},
       {'file_name':'stop_times.txt', 'table':'stop_times', 'drop':['pickup_type','drop_off_type'],
        'dtypes':{'trip_id':db.String(45),'arrival_time':db.String(45),'departure_time':db.String(45),
                  'stop_id':db.String(45), 'stop_sequence':db.Integer(),'stop_headsign':db.String(45),
                  'shape_dist_traveled':db.String(45)}},
       {'file_name':'trips.txt', 'table':'trips', 'drop':'shape_id',
        'dtypes':{'route_id':db.String(45),'direction':db.Integer(),'trip_headsign':db.String(100),
                  'service_id':db.String(45), 'trip_id':db.String(45)}}]
while True:
    while not is_time_between(dt.time(2,00), dt.time(4,00)):
        time.sleep(1800)
    print('Checking for new feed: %s' %time.ctime())
    check=check_for_new_feed(timestamp)
    if check:
        timestamp=check
        update_weather(engine)
        reset_tables(engine, 'reset_GTFS_table.sql')
        insert_data_into_stops(engine)
        for text_file in files:
            insert_data_into_table(text_file, engine)
            print(text_file['file_name']+" complete")
        print('new data inserted')
        update_stop_route_json()
    else:
        update_weather(engine)
        insert_stop_times(engine)
    time.sleep( 80000 )
