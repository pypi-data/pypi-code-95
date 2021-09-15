from datetime import datetime

import pandas as pd
from sqlalchemy import MetaData

#from dwhutils.Logger import logger


def read_raw_sql_hub(db_con, t_name: str, date: str, schema: str):
    metadata = MetaData(bind=db_con)
    metadata.reflect(bind=db_con, schema=schema)

    for table in [i for i in reversed(metadata.sorted_tables) if i.name == t_name]:
        target_table = table
    cols = target_table.columns
    cols = [i.name.replace(t_name + ".", "") for i in cols]
    data = db_con.execute(target_table.select()).fetchall()
    df = pd.DataFrame(columns=cols, data=data)
    df = df.reset_index()
    return df


def read_raw_sql_sat(db_con, t_name: str, date: str, schema: str, log_cli: bool = True, log_file: bool = True,
                     log_class: str = ""):

    #logger(logging_str="Lese tabelle {0}".format(t_name), logging_class=log_class, log_to_cli=log_cli,
    #       log_to_file=log_file, log_lvl='info')
    metadata = MetaData(bind=db_con)
    metadata.reflect(bind=db_con, schema=schema)

    for table in [i for i in reversed(metadata.sorted_tables) if i.name == t_name]:
        target_table = table

    date_date = datetime.strptime(date, '%Y-%m-%d').date()
    cols = target_table.columns
    cols = [i.name.replace(t_name + ".", "") for i in cols]
    data = db_con.execute(target_table.select()).fetchall()
    df = pd.DataFrame(columns=cols, data=data)

    df = df[df['processing_date_start'] <= date_date]
    df = df[df['processing_date_end'] > date_date]
    df = df.reset_index()
    # logger(logging_str='es wurden {0} datensaetze aus der Tabelle {1} gelesen'.format(df.shape[0], t_name),
    #       logging_class=log_class, log_to_cli=log_cli,
    #       log_to_file=log_file, log_lvl='info')
    return df


def readTableFromDB(db_con, t_name: str, date: str, schema: str):
    hist_table_name = t_name + "_hist"

    select_main = "select * from {schema}.{table};".format(schema=schema, table=t_name)
    select_hist = "select * from {schema}.{table};".format(schema=schema, table=hist_table_name)

