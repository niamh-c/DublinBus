import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split,cross_validate, cross_val_score, TimeSeriesSplit
import math
from datetime import datetime
import pickle
import sys
import numpy as np
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
engine = db.create_engine('mysql+pymysql://'+os.getenv("USER")+':'+os.getenv("PASSWORD")+'@'+os.getenv("HOST")+':3306/website')

def clampLB(minV,maxV, Q3, Q1):
    return max(minV, Q1-1.5*(Q3-Q1))
def clampUB(minV, maxV, Q3, Q1):
    return min(maxV, Q3+1.5*(Q3-Q1))

#results=pd.DataFrame(columns = ['route','<60','<120', '>120', 'overall'])
#results.to_csv('linear_regression_total_journey_tt_scores.csv', header=True, index=False)

files=['102r.csv', '104r.csv', '111r.csv', '114r.csv', '116r.csv', '118r.csv', '11r.csv', '120r.csv', '122r.csv', '123r.csv', '130r.csv', '13r.csv', '140r.csv', '142r.csv', '145r.csv', '14Cr.csv', '14r.csv', '150r.csv', '151r.csv', '15Ar.csv', '15Br.csv', '15Dr.csv', '15r.csv', '161r.csv', '16Cr.csv', '16Dr.csv', '16r.csv', '17Ar.csv', '17r.csv', '184r.csv', '185r.csv', '18r.csv', '1r.csv', '220r.csv', '236r.csv',  '238r.csv', '239r.csv', '25Ar.csv', '25Br.csv', '25Dr.csv', '25r.csv','25Xr.csv','26r.csv','270r.csv','27Ar.csv','27Br.csv','27.csv','27r.csv','27Xr.csv','29Ar.csv','31Ar.csv','31Br.csv','31Dr.csv','31r.csv','32r.csv','32Xr.csv','33Ar.csv','33Br.csv', '33Dr.csv', '33Er.csv', '33r.csv', '33Xr.csv', '37r.csv','38Ar.csv','38Br.csv','38Dr.csv','38r.csv','39Ar.csv','39r.csv','39Xr.csv','40Br.csv','40Dr.csv','40Er.csv','40r.csv','41Ar.csv','41Br.csv','41Cr.csv','41Dr.csv','41r.csv','41Xr.csv','42Dr.csv','42r.csv','43r.csv','44Br.csv','44r.csv','45Ar.csv','46Ar.csv','46Er.csv','47r.csv','49r.csv','4r.csv','51Dr.csv','51Xr.csv','53r.csv','54Ar.csv','56Ar.csv','59r.csv','61r.csv','63r.csv','65Br.csv','65r.csv','66Ar.csv','66Br.csv','66r.csv','66Xr.csv','67r.csv','67Xr.csv','68Ar.csv','68r.csv','68Xr.csv','69r.csv','69Xr.csv','70Dr.csv','70r.csv','75r.csv','76Ar.csv','76r.csv','77Ar.csv','77Xr.csv','79Ar.csv','79r.csv','7Ar.csv','7Br.csv','7Dr.csv','7r.csv','83Ar.csv','83r.csv','84Ar.csv','84r.csv','84Xr.csv','9r.csv', 'all_routes_model.csv']

for route in files:
    if route=='all_routes_model.csv':
        total=pd.read_csv('./files/all_routes_model.csv', names=['DAYOFSERVICE', 'TRIPID', 'PROGRNUMBER', 'STOPPOINTID', 'PLANNEDTIME_ARR', 'PLANNEDTIME_DEP', 'ACTUALTIME_ARR', 'ACTUALTIME_DEP', 'LineID', 'RouteID', 'Direction', 'weekday'], parse_dates=['DAYOFSERVICE'])
    else:
        try:
            total=pd.read_csv('files/'+route, names=['DAYOFSERVICE','TRIPID','PROGRNUMBER','STOPPOINTID','PLANNEDTIME_ARR', 'PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP','LineID','RouteID', 'Direction'], parse_dates=['DAYOFSERVICE'])
        except:
            continue
    total=total.drop(total.loc[total.DAYOFSERVICE=='DAYOFSERVICE'].index, errors='ignore')
    total.DAYOFSERVICE=pd.to_datetime(total.DAYOFSERVICE)
    total[['TRIPID', 'PROGRNUMBER']]=total[['TRIPID', 'PROGRNUMBER']].astype(int)
    total=total.sort_values(['DAYOFSERVICE', 'TRIPID', 'PROGRNUMBER'])
    total[['PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']] = total[['PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']].astype(int)
    #Target Feature
    total['DIFFERENCE_PLANNED_ACTUAL_ARR']=total['ACTUALTIME_ARR']-total['PLANNEDTIME_ARR']
    UB=clampUB(total.DIFFERENCE_PLANNED_ACTUAL_ARR.min(), total.DIFFERENCE_PLANNED_ACTUAL_ARR.max(), total.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.75), total.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.25))
    total.loc[(total['DIFFERENCE_PLANNED_ACTUAL_ARR']>=UB),'DIFFERENCE_PLANNED_ACTUAL_ARR']=UB
    LB=clampLB(total.DIFFERENCE_PLANNED_ACTUAL_ARR.min(), total.DIFFERENCE_PLANNED_ACTUAL_ARR.max(), total.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.75), total.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.25))
    total.loc[(total['DIFFERENCE_PLANNED_ACTUAL_ARR']<=LB), 'DIFFERENCE_PLANNED_ACTUAL_ARR']=LB
    df=total.loc[total.groupby(['TRIPID', 'DAYOFSERVICE'])['PROGRNUMBER'].idxmax()]
    df=df.append(total.loc[total.groupby(['TRIPID', 'DAYOFSERVICE'])['PROGRNUMBER'].idxmin()])
    df=df.sort_values(['DAYOFSERVICE', 'TRIPID', 'PROGRNUMBER'])
    df=df.reset_index(drop=True)
    X = df
    y = df['DIFFERENCE_PLANNED_ACTUAL_ARR']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, shuffle=False)
    X_test=X_test.reset_index(drop=True)
    y_test=y_test.reset_index(drop=True)
    df=X_test
    X=None
    y=None
    X_train=None
    Y_train=None

    df['day']=df['DAYOFSERVICE'].dt.dayofweek
    df['month']=df['DAYOFSERVICE'].dt.month #school term

    #Merge with historical weather
    df['TIMESTAMP']=pd.to_datetime(df.DAYOFSERVICE)+pd.to_timedelta(df.ACTUALTIME_ARR, unit='second')
    #merge weather
    min_date=df.DAYOFSERVICE.min()
    max_date=df.DAYOFSERVICE.max()
    sql='Select * from HistoricalWeather where Timestamp >= "'+str(min_date)+'" and Timestamp <= "'+str(max_date)+'";'
    df1=pd.read_sql_query(sql, con=engine, parse_dates={'DayOfService':'%Y-%m-%d %H:%M:%S'})
    df=df.sort_values('TIMESTAMP')
    df=pd.merge_asof(df, df1, left_on='TIMESTAMP', right_on='Timestamp', direction='backward')
    df=df.drop('TIMESTAMP',1, errors='ignore')


    #Add in national hols
    nathols=['2018-01-01', '2018-03-17',  '2018-03-30',  '2018-04-01',  '2018-04-02',  '2018-05-07',  '2018-06-04',
     '2018-08-06',  '2018-10-29',  '2018-12-21',  '2018-12-24', '2018-12-25', '2018-12-26', '2018-12-31']
    df['OBSERVENCE/NATIONALHOL']=0
    df.loc[df.DAYOFSERVICE.isin(nathols), 'OBSERVENCE/NATIONALHOL']=1

    #drop all unneccessary features
    df=df.drop(['Timestamp',  'LineID_y'], 1, errors='ignore')

    chosen_features = ["temperature", "PROGRNUMBER", "month", "day"]
    df[['month', 'day']]=df[['month', 'day']].astype('float64')

    #opening the model
    i=route.find('r')
    route=route[:i]

    try:
        model_dict = pickle.load(open('./pickles_linear_regression/'+route,'rb'))
    except:
        model_dict = pickle.load(open('./pickles_linear_regression/all_routes_model','rb'))
    model=model_dict['model']

    #Get scores for test set
    predictions_list=model.predict(df[chosen_features])
    df['predicted_arrival_diff']=np.array(predictions_list)
    df['predicted_arrival_time']=round(df['PLANNEDTIME_ARR']+df['predicted_arrival_diff'])
    df=df.drop(['DIFFERENCE_PLANNED_ACTUAL_ARR','predicted_arrival_diff', 'PLANNEDTIME_ARR', 'PLANNEDTIME_DEP', 'day', 'month', 'temperature'],1, errors='ignore')

    df['ACTUAL_TT']=df.groupby(['TRIPID', 'DAYOFSERVICE'])['ACTUALTIME_ARR'].diff()
    df['PREDICTED_TT']=df.groupby(['TRIPID', 'DAYOFSERVICE'])['predicted_arrival_time'].diff()
    df['DIFF']=abs(df['ACTUAL_TT']-df['PREDICTED_TT'])
    df=df.dropna()

    mean_errors={3600:None,7200:None,'greater_than_2_hours':None}
    last_key=0
    for key in mean_errors:
        if key!='greater_than_2_hours':
            mean_errors[key]=(df.loc[(df.ACTUAL_TT<=key)&(df.ACTUAL_TT>last_key)]['DIFF'].mean())
            last_key=key
        elif key=='greater_than_2_hours':
            mean_errors[key]=df.loc[df.ACTUAL_TT>7200]['DIFF'].mean()
    mean_errors['overall']=df.DIFF.mean()
    errors=pd.DataFrame(mean_errors, index=[route,])

    errors.to_csv('linear_regression_total_journey_tt_scores.csv', mode='a', header=False, index=True)
