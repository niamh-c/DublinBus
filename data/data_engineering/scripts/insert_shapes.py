import sqlalchemy as db
import pandas as pd
import os
import sys
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

engine = db.create_engine('mysql+pymysql://'+os.getenv("USER")+':'+os.getenv("PASSWORD")+'@'+os.getenv("HOST")+':3306/website')
df=pd.read_csv('shapes.txt',delimiter=',', dtype=str)
try:
    df.to_sql('shapes', con=engine, index=False, if_exists='append')
except Exception as e:
    print(e)
