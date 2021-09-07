import logging
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, text, select
from sqlalchemy.pool import NullPool

__all__=['connect_to_db','get_data_from_db','get_pandas_df_from_db']


logger = logging.getLogger(__name__)
connection = None
table = None

def connect_to_db(DB_HOST,DB_PORT,DB_USER,DB_PASS,DB_NAME,TABLE_NAME):
    global connection
    global table
    logger.info('Connecting to MySql LileadsDB Database')
    try:
        lileads_engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASS}@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
            echo=False, poolclass=NullPool,
            connect_args={'read_timeout': 3600, 'write_timeout': 600}
        )
        engine_metadata = MetaData(bind=lileads_engine)
        connection = lileads_engine.connect()

        table = Table(f'{TABLE_NAME}', engine_metadata, autoload=True)
        logger.info('Connecting to MySql LileadsDB Database successfully')
    except Exception as exception:
        error_message = f'Connect to MySql LileadsDB Database - {repr(exception)}'
        logger.error(f"{error_message}")

def get_pandas_df_from_db(sql_select_query):
    data = []
    try:
        data = text(sql_select_query)
        print('fetcheando')
        data = connection.execute(data).fetchall()
        'print armando diccionario'
        data = [dict(zip(row.keys(), row)) for row in data]
        print(f"- Total leads to work: {len(data)}")
    except Exception as exception:
        print(f"Get leads to work - {repr(exception)}")
    return pd.DataFrame(data)

def get_data_from_db(sql_select_query):
    data = []
    try:
        data = text(sql_select_query)
        print('fetcheando')
        data = connection.execute(data).fetchall()
        print('print armando diccionario')
        data = [dict(zip(row.keys(), row)) for row in data]
        print(f"- Total leads to work: {len(data)}")
    except Exception as exception:
        print(f"Get leads to work - {repr(exception)}")
    return data

if __name__ == "__main__":
    connect_to_db(DB_HOST='',
                  DB_USER='',
                  DB_PASS='',
                  DB_NAME='',
                  TABLE_NAME='')

    sql_query = '''select * from leads limit 100'''

    df = get_data_from_db(sql_select_query=sql_query)
    print(df.head())
