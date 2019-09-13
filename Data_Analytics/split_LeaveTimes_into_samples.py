import os
import pandas as pd
df = pd.read_csv('trainIDs.csv',  keep_default_na=True, sep=',\s+', delimiter=',')
chunks=10**6
for chunk in pd.read_csv('rt_leavetimes_DB_2018.txt', chunksize=chunks,delimiter=';',keep_default_na=True):
    try:
        save=pd.DataFrame()
        for d in chunk.DAYOFSERVICE.unique():
            trips=list(df.loc[df.DayOfService==d]['TripID'])
            save=save.append(chunk.loc[(chunk['DAYOFSERVICE']==d)&chunk.TRIPID.isin(trips)])
        if len(save)!=0:
            # if file does not exist write header
            save=save.drop(['DATASOURCE', 'PASSENGERS', 'PASSENGERSIN','PASSENGERSOUT','DISTANCE','SUPPRESSED',
       'JUSTIFICATIONID','LASTUPDATE','NOTE'],1)
            save=pd.merge(save, df, left_on=['DAYOFSERVICE', 'TRIPID'], right_on=['DayOfService', 'TripID']).drop(['DayOfService', 'TripID'], 1)
            if not os.path.isfile('trainDataSmall.csv'):
               save.to_csv('trainDataSmall.csv', header='column_names', index=False)
            else: # else it exists so append without writing the header
               save.to_csv('trainDataSmall.csv', mode='a', header=False, index=False)
    except Exception as e:
        print(e)