files=['102r.csv', '104r.csv', '111r.csv', '114r.csv', '116r.csv', '118r.csv', '11r.csv', '120r.csv', '122r.csv', '123r.csv', '130r.csv', '13r.csv', '140r.csv','142r.csv','145r.csv','14Cr.csv','14r.csv','150r.csv','151r.csv','15Ar.csv','15Br.csv','15Dr.csv',
'15r.csv','161r.csv','16Cr.csv','16Dr.csv','16r.csv','17Ar.csv','17r.csv','184r.csv','185r.csv','18r.csv','1r.csv','220r.csv','236r.csv','238r.csv','239r.csv','25Ar.csv','25Br.csv','25Dr.csv','25r.csv','25Xr.csv','26r.csv','270r.csv','27Ar.csv','27Br.csv','27.csv','27r.csv','27Xr.csv','29Ar.csv','31Ar.csv','31Br.csv','31Dr.csv','31r.csv','32r.csv','32Xr.csv','33Ar.csv','33Br.csv',
'33Dr.csv','33Er.csv','33r.csv','33Xr.csv','37r.csv','38Ar.csv','38Br.csv','38Dr.csv','38r.csv','39Ar.csv','39r.csv','39Xr.csv','40Br.csv','40Dr.csv','40Er.csv','40r.csv','41Ar.csv','41Br.csv','41Cr.csv','41Dr.csv','41r.csv','41Xr.csv','42Dr.csv','42r.csv','43r.csv','44Br.csv','44r.csv','45Ar.csv','46Ar.csv','46Er.csv','47r.csv','49r.csv','4r.csv','51Dr.csv','51Xr.csv','53r.csv','54Ar.csv','56Ar.csv','59r.csv','61r.csv','63r.csv','65Br.csv','65r.csv','66Ar.csv','66Br.csv','66r.csv','66Xr.csv','67r.csv','67Xr.csv','68Ar.csv','68r.csv','68Xr.csv','69r.csv','69Xr.csv','70Dr.csv','70r.csv','75r.csv','76Ar.csv','76r.csv','77Ar.csv','77Xr.csv','79Ar.csv','79r.csv','7Ar.csv','7Br.csv','7Dr.csv','7r.csv','83Ar.csv','83r.csv','84Ar.csv','84r.csv','84Xr.csv','9r.csv']

import os
import pandas as pd
df = pd.read_csv('testIDs.csv',  keep_default_na=True, sep=',\s+', delimiter=',')
chunks=10**6
for file in files:
    for chunk in pd.read_csv(file, names=['DAYOFSERVICE','TRIPID','PROGRNUMBER','STOPPOINTID','PLANNEDTIME_ARR', 'PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP','LineID','RouteID', 'Direction'],chunksize=chunks,delimiter=',',keep_default_na=True):
        try:
            save=pd.DataFrame()
            for d in chunk.DAYOFSERVICE.unique():
                trips=list(df.loc[df.DayOfService==d]['TripID'])
                save=save.append(chunk.loc[(chunk['DAYOFSERVICE']==d)&chunk.TRIPID.isin(trips)])
            if len(save)!=0:
                save=pd.merge(save, df, left_on=['DAYOFSERVICE', 'TRIPID'], right_on=['DayOfService', 'TripID']).drop(['DayOfService', 'TripID'], 1)
                if not os.path.isfile('trainDataSmall.csv'):
                   save.to_csv('testDataSmall.csv', header='column_names', index=False)
                else: # else it exists so append without writing the header
                   save.to_csv('testDataSmall.csv', mode='a', header=False, index=False)
        except Exception as e:
            print(e)
