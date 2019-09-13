import os
import pandas as pd
df = pd.read_csv('rt_trips.txt',  keep_default_na=True, sep=',\s+', delimiter=',', names=['DayOfService','TripID','LineID','RouteID','Direction','PlannedTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP'])
df=df.drop(['PlannedTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP'], axis=1)
chunks=10**6
for chunk in pd.read_csv('test_{2}.txt', chunksize=chunks,delimiter=',',keep_default_na=True, header=None, names=['DAYOFSERVICE','TRIPID','PROGRNUMBER','STOPPOINTID','PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']):
    try:
        save=pd.DataFrame()
        for d in chunk.DAYOFSERVICE.unique():
            trips=list(df.loc[df.DayOfService==d]['TripID'])
            save=save.append(chunk.loc[(chunk['DAYOFSERVICE']==d)&chunk.TRIPID.isin(trips)])
        if len(save)!=0:
            # if file does not exist write header
            save=pd.merge(save, df, left_on=['DAYOFSERVICE', 'TRIPID'], right_on=['DayOfService', 'TripID']).drop(['DayOfService', 'TripID'], 1)
            if not os.path.isfile('LeaveTrips.csv'):
               save.to_csv('LeaveTrips.csv', header='column_names', index=False)
            else: # else it exists so append without writing the header
               save.to_csv('LeaveTrips.csv', mode='a', header=False, index=False)
    except Exception as e:
        print(e)

