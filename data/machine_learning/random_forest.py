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
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
results=pd.DataFrame(columns = ['route','features','n_est','max_depth','train/test/CV','mae', 'mean_squared_error', 'r2', 'date'])

results.to_csv('RFScores.csv', mode='a', header=True, index=False)

engine = db.create_engine('mysql+pymysql://'+os.getenv("USER")+':'+os.getenv("PASSWORD")+'@'+os.getenv("HOST")+':3306/DublinBus')

def clampLB(minV,maxV, Q3, Q1):
    return max(minV, Q1-1.5*(Q3-Q1))
def clampUB(minV, maxV, Q3, Q1):
    return min(maxV, Q3+1.5*(Q3-Q1))

files=['116r.csv', '118r.csv', '11r.csv', '120r.csv', '122r.csv', '123r.csv', '130r.csv', '13r.csv', '140r.csv', '142r.csv', '145r.csv', '14Cr.csv', '14r.csv', '150r.csv', '151r.csv', '15Ar.csv', '15Br.csv', '15Dr.csv', '15r.csv', '16Cr.csv', '16Dr.csv', '16r.csv', '17Ar.csv',  '1r.csv', '25Ar.csv', '25Br.csv', '25Dr.csv', '25r.csv', '25Xr.csv', '26r.csv', '27Ar.csv', '27Br.csv', '27r.csv', '27Xr.csv', '29Ar.csv', '31Ar.csv', '31Br.csv', '31Dr.csv', '31r.csv', '32r.csv', '32Xr.csv' , '33Dr.csv', '33Er.csv', '33r.csv', '33Xr.csv', '37r.csv', '38Ar.csv', '38Br.csv', '38Dr.csv', '38r.csv', '39Ar.csv', '39r.csv', '39Xr.csv', '40Br.csv', '40Dr.csv', '40Er.csv', '40r.csv', '41Ar.csv', '41Br.csv', '41Cr.csv', '41Dr.csv', '41r.csv', '41Xr.csv', '42Dr.csv', '42r.csv', '43r.csv', '44Br.csv', '44r.csv', '46Ar.csv', '46Er.csv', '47r.csv', '49r.csv', '4r.csv', '51Dr.csv', '51Xr.csv', '53r.csv', '54Ar.csv', '56Ar.csv',  '61r.csv', '65Br.csv', '65r.csv', '66Ar.csv', '66Br.csv', '66r.csv', '66Xr.csv', '67r.csv', '67Xr.csv', '68Ar.csv', '68r.csv', '68Xr.csv', '69r.csv', '69Xr.csv', '70Dr.csv', '70r.csv', '77Ar.csv', '77Xr.csv', '79Ar.csv', '79r.csv', '7Ar.csv', '7Br.csv', '7Dr.csv', '7r.csv', '83Ar.csv', '83r.csv', '84Ar.csv', '84r.csv', '84Xr.csv', '9r.csv',  'all_routes_model.csv']

for route in files:
    try:
        df=pd.read_csv(route, names=['DAYOFSERVICE','TRIPID','PROGRNUMBER','STOPPOINTID','PLANNEDTIME_ARR', 'PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP','LineID','RouteID', 'Direction'], parse_dates=['DAYOFSERVICE'])
        if df.shape[0]>1000000:
            df=df.sample(n=1000000)
        df=df.drop(df.loc[df.DAYOFSERVICE=='DAYOFSERVICE'].index, errors='ignore')
        df.DAYOFSERVICE=pd.to_datetime(df.DAYOFSERVICE)

        #day, weekday, month
        df=df.sort_values(['DAYOFSERVICE', 'TRIPID','PROGRNUMBER'])
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

        df[['PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']] = df[['PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']].astype(int)
        #Target Feature
        df['DIFFERENCE_PLANNED_ACTUAL_ARR']=df['ACTUALTIME_ARR']-df['PLANNEDTIME_ARR']
        UB=clampUB(df.DIFFERENCE_PLANNED_ACTUAL_ARR.min(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.max(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.75), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.25))
        df.loc[(df['DIFFERENCE_PLANNED_ACTUAL_ARR']>=UB),'DIFFERENCE_PLANNED_ACTUAL_ARR']=UB
        LB=clampLB(df.DIFFERENCE_PLANNED_ACTUAL_ARR.min(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.max(), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.75), df.DIFFERENCE_PLANNED_ACTUAL_ARR.quantile(.25))
        df.loc[(df['DIFFERENCE_PLANNED_ACTUAL_ARR']<=LB), 'DIFFERENCE_PLANNED_ACTUAL_ARR']=LB

        #drop all unneccessary features
        df=df.drop(['Timestamp', 'TRIPID', 'LineID_y'], 1, errors='ignore')

        chosen_features = ["temperature","rain","PROGRNUMBER","month","day","OBSERVENCE/NATIONALHOL"]
        df[['month', 'day']]=df[['month', 'day']].astype('float64')

        X = df[chosen_features]
        y = df['DIFFERENCE_PLANNED_ACTUAL_ARR']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, shuffle=False)
        X_test=X_test.reset_index(drop=True)
        y_test=y_test.reset_index(drop=True)

        X_train = scaler.fit_transform(X_train);
        X_test = scaler.fit_transform(X_test);

        #Fitting the model
        n_est=100
        max_dep=15
        model= RandomForestRegressor(n_estimators=n_est, max_depth=max_dep, oob_score=True, random_state=1)
        model.fit(X_train, y_train);

        #pickling the model
        outfile = open('pickle_'+route,'wb')
        pickle.dump({'model':model, 'features':list(chosen_features)},outfile)
        outfile.close()

        results=pd.DataFrame(columns = ['route','features','n_est','max_depth','train/test/CV','mae', 'mean_squared_error', 'r2', 'date'])
        #Get scores
        scoring = {'abs_error': 'neg_mean_absolute_error', 'squared_error': 'neg_mean_squared_error', 'r2':'r2'}
        scores = cross_validate(model, X_test, y_test, cv= TimeSeriesSplit(n_splits=3), scoring=scoring, return_train_score=True)
        results = results.append(pd.Series([route, chosen_features, n_est, max_dep, 'train', (abs(scores['test_abs_error'].mean())), (math.sqrt(abs(scores['test_squared_error'].mean()))), (scores['test_r2'].mean()), datetime.today().strftime('%Y-%m-%d')], index=results.columns ), ignore_index=True)
        results.to_csv('RFScores.csv', mode='a', header=False, index=False)
    except Exception as e:
        print(route)
        print(e)
