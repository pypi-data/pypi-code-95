from sqlalchemy import create_engine
import pandas as pd
import time


def convert_to_DF(data_name, file_out : str, to_csv : bool):
    '''
    

    '''
    compounds_data = pd.DataFrame(data_name)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
        if to_csv == True:
            compounds_data.to_csv(file_out + '.csv')
        else:
            pass

        return compounds_data
    
def import_to_SQL(name='compounds_dataset'):
    '''
    Imports the output as an SQL database

    '''
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'localhost'
    USER = 'postgres'
    PASSWORD = 'kenya123'
    DATABASE = 'Compounds_databse'
    PORT = 5432
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    compounds_data.to_sql(name, engine, if_exists='replace')