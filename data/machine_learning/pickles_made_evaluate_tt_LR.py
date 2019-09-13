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

files=['102r.csv', '104r.csv', '111r.csv', '114r.csv', '116r.csv', '118r.csv', '11r.csv', '120r.csv', '122r.csv', '123r.csv', '130r.csv', '13r.csv', '140r.csv', '142r.csv', '145r.csv', '14Cr.csv', '14r.csv', '150r.csv', '151r.csv', '15Ar.csv', '15Br.csv', '15Dr.csv', '15r.csv', '161r.csv', '16Cr.csv', '16Dr.csv', '16r.csv', '17Ar.csv', '17r.csv', '184r.csv', '185r.csv', '18r.csv', '1r.csv', '220r.csv', '236r.csv',  '238r.csv', '239r.csv', '25Ar.csv', '25Br.csv', '25Dr.csv', '25r.csv','25Xr.csv','26r.csv','270r.csv','27Ar.csv','27Br.csv','27.csv','27r.csv','27Xr.csv','29Ar.csv','31Ar.csv','31Br.csv','31Dr.csv','31r.csv','32r.csv','32Xr.csv','33Ar.csv','33Br.csv', '33Dr.csv', '33Er.csv', '33r.csv', '33Xr.csv', '37r.csv','38Ar.csv','38Br.csv','38Dr.csv','38r.csv','39Ar.csv','39r.csv','39Xr.csv','40Br.csv','40Dr.csv','40Er.csv','40r.csv','41Ar.csv','41Br.csv','41Cr.csv','41Dr.csv','41r.csv','41Xr.csv','42Dr.csv','42r.csv','43r.csv','44Br.csv','44r.csv','45Ar.csv','46Ar.csv','46Er.csv','47r.csv','49r.csv','4r.csv','51Dr.csv','51Xr.csv','53r.csv','54Ar.csv','56Ar.csv','59r.csv','61r.csv','63r.csv','65Br.csv','65r.csv','66Ar.csv','66Br.csv','66r.csv','66Xr.csv','67r.csv','67Xr.csv','68Ar.csv','68r.csv','68Xr.csv','69r.csv','69Xr.csv','70Dr.csv','70r.csv','75r.csv','76Ar.csv','76r.csv','77Ar.csv','77Xr.csv','79Ar.csv','79r.csv','7Ar.csv','7Br.csv','7Dr.csv','7r.csv','83Ar.csv','83r.csv','84Ar.csv','84r.csv','84Xr.csv','9r.csv']

for route in files:
    if route=='all_routes_model.csv':
        df=pd.read_csv('./files/all_routes_model.csv', names=['DAYOFSERVICE', 'TRIPID', 'PROGRNUMBER', 'STOPPOINTID', 'PLANNEDTIME_ARR', 'PLANNEDTIME_DEP', 'ACTUALTIME_ARR', 'ACTUALTIME_DEP', 'LineID', 'RouteID', 'Direction', 'weekday'], parse_dates=['DAYOFSERVICE'])
    else:
        try:
            df=pd.read_csv('files/'+route, names=['DAYOFSERVICE','TRIPID','PROGRNUMBER','STOPPOINTID','PLANNEDTIME_ARR', 'PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP','LineID','RouteID', 'Direction'], parse_dates=['DAYOFSERVICE'])
        except:
            continue
    df=df.drop(df.loc[df.DAYOFSERVICE=='DAYOFSERVICE'].index, errors='ignore')
    df.DAYOFSERVICE=pd.to_datetime(df.DAYOFSERVICE)
    df[['TRIPID', 'PROGRNUMBER']]=df[['TRIPID', 'PROGRNUMBER']].astype(int)

    #day, weekday, month
    df=df.sort_values(['DAYOFSERVICE', 'TRIPID', 'PROGRNUMBER'])
    df[['PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']] = df[['PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']].astype(int)
    #Target Feature
    df['DIFFERENCE_PLANNED_ACTUAL_ARR']=df['ACTUALTIME_ARR']-df['PLANNEDTIME_ARR']
    UB=clampUB(df.DIFFERENCE_PLANNED_ACTUAL_ARR.min(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.max(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.75), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.25))
    df.loc[(df['DIFFERENCE_PLANNED_ACTUAL_ARR']>=UB),'DIFFERENCE_PLANNED_ACTUAL_ARR']=UB
    LB=clampLB(df.DIFFERENCE_PLANNED_ACTUAL_ARR.min(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.max(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.75), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.25))
    df.loc[(df['DIFFERENCE_PLANNED_ACTUAL_ARR']<=LB), 'DIFFERENCE_PLANNED_ACTUAL_ARR']=LB
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

    #Get scores
    predictions_list=model.predict(df[chosen_features])
    df['predicted_arrival_diff']=np.array(predictions_list)
    df['predicted_arrival_time']=round(df['PLANNEDTIME_ARR']+df['predicted_arrival_diff'])
    df=df.drop(['DIFFERENCE_PLANNED_ACTUAL_ARR','predicted_arrival_diff', 'PLANNEDTIME_ARR', 'PLANNEDTIME_DEP', 'day', 'month', 'temperature'],1, errors='ignore')

    df_temp=pd.DataFrame(df.groupby(['TRIPID', 'DAYOFSERVICE'])['ACTUALTIME_DEP'].quantile(.25, interpolation='nearest'))
    df_temp.columns=['tt_quarter']
    df=pd.merge(df, df_temp, on=['TRIPID', 'DAYOFSERVICE'])
    df['tt_quarter']=df['ACTUALTIME_ARR']-df['tt_quarter']
    df_temp=pd.DataFrame(df.groupby(['TRIPID', 'DAYOFSERVICE'])['ACTUALTIME_DEP'].quantile(.5, interpolation='nearest'))
    df_temp.columns=['tt_mid']
    df=pd.merge(df, df_temp, on=['TRIPID', 'DAYOFSERVICE'])
    df['tt_mid']=df['ACTUALTIME_ARR']-df['tt_mid']
    df_temp=pd.DataFrame(df.groupby(['TRIPID', 'DAYOFSERVICE'])['ACTUALTIME_DEP'].quantile(.75, interpolation='nearest'))
    df_temp.columns=['tt_3quarter']
    df=pd.merge(df, df_temp, on=['TRIPID', 'DAYOFSERVICE'])
    df['tt_3quarter']=df['ACTUALTIME_ARR']-df['tt_3quarter']
    df.loc[(df['tt_quarter'] < 0), 'tt_quarter'] = None
    df.loc[(df['tt_mid'] < 0), 'tt_mid'] = None
    df.loc[(df['tt_3quarter'] < 0), 'tt_3quarter'] = None

    df_temp=pd.DataFrame(df.groupby(['TRIPID', 'DAYOFSERVICE'])['predicted_arrival_time'].quantile(.25, interpolation='nearest'))
    df_temp.columns=['pred_tt_quarter']
    df=pd.merge(df, df_temp, on=['TRIPID', 'DAYOFSERVICE'])
    df['pred_tt_quarter']=df['predicted_arrival_time']-df['pred_tt_quarter']
    df_temp=pd.DataFrame(df.groupby(['TRIPID', 'DAYOFSERVICE'])['predicted_arrival_time'].quantile(.5, interpolation='nearest'))
    df_temp.columns=['pred_tt_mid']
    df=pd.merge(df, df_temp, on=['TRIPID', 'DAYOFSERVICE'])
    df['pred_tt_mid']=df['predicted_arrival_time']-df['pred_tt_mid']
    df_temp=pd.DataFrame(df.groupby(['TRIPID', 'DAYOFSERVICE'])['predicted_arrival_time'].quantile(.75, interpolation='nearest'))
    df_temp.columns=['pred_tt_3quarter']
    df=pd.merge(df, df_temp, on=['TRIPID', 'DAYOFSERVICE'])
    df['pred_tt_3quarter']=df['predicted_arrival_time']-df['pred_tt_3quarter']
    df.loc[(df['pred_tt_quarter'] < 0), 'pred_tt_quarter'] = None
    df.loc[(df['pred_tt_mid'] < 0), 'pred_tt_mid'] = None
    df.loc[(df['pred_tt_3quarter'] < 0), 'pred_tt_3quarter'] = None

    df['diff_from_quarter']=abs(df['tt_quarter']-df['pred_tt_quarter'])
    df['diff_from_mid']=abs(df['tt_mid']-df['pred_tt_mid'])
    df['diff_from_3quarter']=abs(df['tt_3quarter']-df['pred_tt_3quarter'])

    mean_errors={180:None,600:None,1800:None,3600:None,7200:None,'greater_than_2_hours':None, 'overall':None}
    last_key=0
    for key in mean_errors:
        if key!='greater_than_2_hours' and key!='overall':
            mean_errors[key]=(df.loc[(df.tt_quarter<=key)&(df.tt_quarter>last_key)]['diff_from_quarter'].mean()+
                              df.loc[(df.tt_mid<=key)&(df.tt_mid>last_key)]['diff_from_mid'].mean()+
                              df.loc[(df.tt_3quarter<=key)&(df.tt_3quarter>last_key)]['diff_from_3quarter'].mean())//3
            last_key=key
        elif key=='greater_than_2_hours':
            mean_errors[key]=(df.loc[(df.tt_quarter>7200)]['diff_from_quarter'].mean()+
                              df.loc[(df.tt_mid>7200)]['diff_from_mid'].mean()+
                              df.loc[(df.tt_3quarter>7200)]['diff_from_3quarter'].mean())//3
    mean_errors['overall']=(df.diff_from_quarter.mean()+df.diff_from_mid.mean()+df.diff_from_3quarter.mean())//3
    df=pd.DataFrame(mean_errors, index=[route,])
    df.to_csv('linear_regression_tt_scores.csv', mode='a')
