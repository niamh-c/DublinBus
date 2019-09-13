import xmltodict
import requests
import pandas as pd
import dateutil.parser
from dateutil.tz import gettz
import os
import sys
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
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
        row['date']=dateutil.parser.parse(forecast[i]['@from']).astimezone(gettz("Europe/Dublin")).strftime('%d-%m-%Y')
        row['start_time']=dateutil.parser.parse(forecast[i]['@from']).astimezone(gettz("Europe/Dublin")).strftime('%H:%M')
        row['end_time']=dateutil.parser.parse(forecast[i]['@to']).astimezone(gettz("Europe/Dublin")).strftime('%H:%M')
        row['Description']=forecast[i]['location']['symbol']['@id']
        row['rain']=forecast[i]['location']['precipitation']['@value']
        df=df.append(row,ignore_index=True)
        row=dict()
#df.to_csv('weather')
#send data to db
import sqlalchemy as db
engine = db.create_engine('mysql+pymysql://'+os.getenv("USER")+':'+os.getenv("PASSWORD")+'@'+os.getenv("HOST")+'/website')
df.to_sql('forecast', con=engine, index=False, if_exists='replace')
