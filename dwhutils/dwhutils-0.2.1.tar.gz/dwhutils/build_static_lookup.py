import pandas as pd
from sqlalchemy import MetaData

from dwhutils.db_connection import connect_to_db
import os
from dotenv import load_dotenv

class static_lookup:
    def __init__(self):
        load_dotenv()

    def build_lkp(self,lookup_name: str, lkp_data):
        pd.DataFrame(data=lkp_data).to_sql(schema='biz', con=connect_to_db('biz'), if_exists='replace', name=lookup_name, index=False)

