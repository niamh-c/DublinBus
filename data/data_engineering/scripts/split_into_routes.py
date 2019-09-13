import os
import pandas as pd
chunks=10**6
for chunk in pd.read_csv('LeaveTrips.csv', chunksize=chunks,delimiter=',',keep_default_na=True):
    try:
        for line in chunk.LineID.unique():
            save=pd.DataFrame()
            save=save.append(chunk.loc[(chunk['LineID']==line)])
            if len(save)!=0:
                # if file does not exist write header
                if not os.path.isfile(str(line)+'r.csv'):
                   save.to_csv(str(line)+'r.csv', header='column_names', index=False)
                else: # else it exists so append without writing the header
                   save.to_csv(str(line)+'r.csv', mode='a', header=False, index=False)
    except Exception as e:
        print(e)
print('Finished')
