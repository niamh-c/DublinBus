import time
import requests
import json
import pymysql
import requests
import json
import time
import requests, zipfile, io
import numpy
import pandas as pd
import sqlalchemy as db
import xmltodict
import pandas as pd
import dateutil.parser
from dateutil.tz import gettz
import datetime as dt
import pickle

def check_for_new_feed(timestamp):
    """
    use this to see if we have the latest version of GTFS
    """
    api='https://api.transitfeeds.com/v1/getFeeds?key=78a26227-1a3f-4601-9026-d3f7b038c6ea&location=579&descendants=1&page=1&limit=10&type=gtfs'
    response=requests.get(api)
    if response.status_code != 200:
        print('GET /tasks/ {}'.format(response.status_code))
        return False
    else:
        data = response.json()
        for transit in data['results']['feeds']:
            #find DublinBus id
            if transit['id']=='transport-for-ireland/782':
                if transit['latest']['ts']>timestamp:
                    api='https://api.transitfeeds.com/v1/getLatestFeedVersion?key=78a26227-1a3f-4601-9026-d3f7b038c6ea&feed='+transit['id']
                    response=requests.get(api)
                    if response.status_code != 200:
                        print('GET /tasks/ {}'.format(response.status_code))
                    r = requests.get(api)
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    z.extractall()
                    timestamp=transit['latest']['ts']
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(transit['latest']['ts'])))
                    return timestamp
                return False

def insert_data_into_stops(engine):
    """
    used to insert data into stops as there is editing to be done
    """
    dateparse = lambda x: pd.datetime.strptime(x, '%d-%b-%y  %H:%M:%S')
    Data=pd.read_csv('stops.txt', delimiter=',')
    Data=Data.drop(['zone_id', 'location_type'], errors='ignore')
    Data['stopID_short']=None
    for i in Data.index:
        try:
            index=Data.at[i, 'stop_id'].find('DB')+2
            stop=Data.at[i, 'stop_id'][index:]
            stop=int(stop)
            Data.at[i, 'stopID_short']=stop
        except Exception as e:
            exception_dict = {
        "gen:57102:7730:0:1" : "7682",
        "gen:57102:7732:0:1" : "7676",
        "gen:57102:7743:0:1" : "7690",
        "gen:57102:7943:0:1" : "7703",
        "gen:57102:7731:0:1" : "7674",
        "gen:57102:7733:0:1" : "7677",
        "gen:57102:7948:0:1" : "7701",
        "8220B007612":"7612",
        "en:57102:8021:0:1":"7705",
        'en:57102:8022:0:1':'7706',
        'en:57102:8023:0:1':'7707',
        'en:57102:8024:0:1':'7708',
        'en:57102:8025:0:1':'7709',
        'en:57102:8026:0:1':'7710',
        'en:57102:8027:0:1':'7711',

    }
            print(e)
            if Data.at[i, 'stop_id'] in exception_dict.keys():
                Data.at[i, 'stopID_short']=exception_dict[Data.at[i, 'stop_id']]
            else:
                #Data=Data.drop(i, errors='ignore')
                pass

    try:
        Data.to_sql('stops', con=engine, index=False, if_exists='append')
    except Exception as e:
        print(e)

def insert_data_into_table(text_file, engine):
    """
    dictionary with keys file_name, table, drop, dtypes
    """
    if text_file['file_name']=='stop_times.txt':
        insert_stop_times(engine)
    else:
        chunks = 10**6
        for chunk in pd.read_csv(text_file['file_name'], chunksize=chunks,delimiter=','):
            if text_file['drop']!=None:
                chunk=chunk.drop(text_file['drop'],1, errors='ignore')
            try:
                chunk.to_sql(text_file['table'], con=engine, index=False, if_exists='append')
            except Exception as e:
                print(e)

def reset_tables(engine, sql_text):
    """
    used to reset tables but keep keys
    """
    connection = engine.raw_connection()
    cursor = connection.cursor()

    # Open and read the file as a single buffer
    fd = open(sql_text, 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            if command.rstrip() != '':
                cursor.execute(command)
        except ValueError as msg:
            print ("Command skipped: ", msg)
    connection.commit()
    cursor.close()
    connection.close()

def insert_stop_times(engine):
    reset_tables(engine, 'reset_stop_times.sql')
    chunks = 10**5
    for chunk in pd.read_csv('stop_times.txt', chunksize=chunks,delimiter=','):
        chunk=chunk.drop(['pickup_type','drop_off_type'],1, errors='ignore')
        df=pd.read_csv('trips.txt',delimiter=',')
        chunk=chunk.merge(df, on=['trip_id'], how='left', validate='m:1')
        chunk=chunk.drop(['shape_id', 'trip_headsign', 'direction_id'], 1)
        df=pd.read_csv('routes.txt',delimiter=',')
        chunk=chunk.merge(df, on=['route_id'], how='left', validate='m:1')
        chunk=chunk.drop(['agency_id', 'route_type', 'route_id', 'route_long_name'], 1)
        for n in range(0,10):
            date=str(numpy.datetime64('today') + numpy.timedelta64(n, 'D'))
            date=dt.datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            sqldate=dt.datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
            chunk['date']=date
            chunk['month']=pd.to_datetime(chunk['date']).dt.month
            chunk['day']=pd.to_datetime(chunk['date']).dt.dayofweek
            nathols=['2019-10-28', '2019-12-24',  '2019-12-25',  '2019-12-26',  '2019-12-31',  '2020-01-01']
            chunk['OBSERVENCE/NATIONALHOL']=0
            chunk.loc[chunk.date.isin(nathols), 'OBSERVENCE/NATIONALHOL']=1
            #Merge with historical weather
            chunk.loc[chunk.arrival_time>='24:00:00', 'arrival_time'] = chunk.loc[chunk.arrival_time>='24:00:00', 'arrival_time'].apply(change_time)

            #chunk.arrival_time = pd.to_datetime(chunk.arrival_time,format='%H:%M:%S')
            chunk['TIMESTAMP']=pd.to_datetime(chunk['date'] + ' ' + chunk['arrival_time'])
            #merge weather
            sql='Select * from forecast where date = "'+str(sqldate)+'";'
            df1=pd.read_sql_query(sql, con=engine, parse_dates={'date':'%d-%m-%Y', 'start_time': '%H:%M'})
            df1['date']=df1['date'].dt.strftime('%Y-%m-%d')
            df1['start_time']=df1['start_time'].dt.strftime('%H:%M')
            chunk=chunk.sort_values('TIMESTAMP')
            df1['Timestamp']= pd.to_datetime(df1['date'] + ' ' + df1['start_time'])
            chunk=pd.merge_asof(chunk, df1, left_on='TIMESTAMP', right_on='Timestamp', direction='backward')
            chunk=chunk.drop('TIMESTAMP',1, errors='ignore')
            chunk=chunk.fillna(0)

            for route in chunk.route_short_name.unique():
                if route in ['25X', '32X', '40E', '41X', '51X', '66X', '68A', '70D', '130', '53', '68X', '116', '11', '38B', '70']:
                    model = pickle.load(open("./pickles_random_forest/all_routes_model",'rb'))
                else:
                    try:
                        model = pickle.load(open("./pickles_random_forest/"+route,'rb'))
                    except:
                        model = pickle.load(open("./pickles_random_forest/all_routes_model",'rb'))
                chosen_feat=['temperature', 'rain', 'stop_sequence', 'month', 'day', 'OBSERVENCE/NATIONALHOL']
                model=model['model']
                df=chunk.loc[chunk.route_short_name==route]
                df = df.reindex(columns = chosen_feat)
                chunk.loc[chunk.route_short_name==route,'predictions']=model.predict(df)

            chunk['predicted_arrival_times_'+str(n)]= (pd.to_datetime(chunk['arrival_time']) + pd.to_timedelta( chunk['predictions'], unit='s')).dt.strftime("%H:%M")
            chunk=chunk.drop(['date_x', 'date_y', 'Unnamed: 0', 'start_time', 'end_time', 'cloud_percent', 'rain', 'Description', 'Timestamp', 'month', 'day', 'predictions', 'temperature', 'OBSERVENCE/NATIONALHOL'],1, errors='ignore')
        #chunk=chunk.drop(['date_x', 'date_y', 'Unnamed: 0', 'start_time', 'end_time', 'cloud_percent', 'rain', 'Description', 'Timestamp', 'month', 'day', 'predictions', 'temperature', 'temperature_NORM'],1, errors='ignore')
        try:
            chunk.to_sql('stop_times', con=engine, index=False, if_exists='append')
        except Exception as e:
            print(e)

def update_weather(engine):
    #Dublin Airport
    api='http://metwdb-prod.ichec.ie/metno-wdb2ts/locationforecast?lat=53.4264;long=-6.2499'
    response=requests.get(api)
    data=xmltodict.parse(response.content)
    #To hold weather data
    df=pd.DataFrame(columns=['date', 'start_time', 'end_time', 'temperature', 'cloud_percent', 'rain', 'Description'])
    #format api response
    forecast=data['weatherdata']['product']['time']
    row=dict()
    for i in range(0, len(forecast)):
        if forecast[i]['@from']==forecast[i]['@to']:#harmonie model
            row['temperature']=forecast[i]['location']['temperature']['@value']
            row['cloud_percent']=forecast[i]['location']['cloudiness']['@percent']
        else:#eptc model
            row['date']=dateutil.parser.parse(forecast[i]['@from']).astimezone(gettz("Europe/Dublin")).strftime('%d-%m-%y')
            row['start_time']=dateutil.parser.parse(forecast[i]['@from']).astimezone(gettz("Europe/Dublin")).strftime('%H:%M')
            row['end_time']=dateutil.parser.parse(forecast[i]['@to']).astimezone(gettz("Europe/Dublin")).strftime('%H:%M')
            row['Description']=forecast[i]['location']['symbol']['@id']
            row['rain']=forecast[i]['location']['precipitation']['@value']
            df=df.append(row,ignore_index=True)
            row=dict()
    df.to_sql('forecast', con=engine, index=False, if_exists='replace')

def update_stop_route_json():
    busStopInfo=dict()
    sql = "select stop_id, stopID_short from stops where stopID_short is not null"
    db = pymysql.connect(host="127.0.0.1", port=3306 , user="niamh", passwd="comp47360jnnd", db="website")
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    data = cursor.fetchall()
    for i in range(0, len(data)):
        sql = "SELECT distinct(route_short_name) FROM website.stop_times where stop_id='"+data[i][0]+"';"
        cursor.execute(sql)
        db.commit()
        row = cursor.fetchall()
        temp=[]
        for r in row:
            temp+=r[0],
        busStopInfo[data[i][1]]=temp
    with open('../DublinBusProject/DublinBus/backend/stop_with_routes.json', 'w') as fp:
        json.dump(busStopInfo, fp)
    cursor.close()

def change_time(row):
    a=row.split(':', 1)
    a[0]=int(a[0])-24
    return str(a[0])+":"+a[1]

def is_time_between(begin_time, end_time, check_time=None):
    check_time = dt.datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time
