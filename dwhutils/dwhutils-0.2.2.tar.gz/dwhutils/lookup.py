import pandas as pd
from dwhutils.db_connection import connect_to_db
from sqlalchemy import MetaData


def get_lkp_value(lkp_name: str):
    db_con = connect_to_db(layer='biz')

    res = pd.read_sql_table(table_name=lkp_name.upper(), con=db_con)
    results = res.to_dict('records')

    lkp = {}
    for i in results:
        key = i['auspraegung']
        val = i['ID']
        if val != 99:
            lkp[key] = val
        else:
            lkp[''] = 99
            lkp[' '] = 99
            lkp[None] = 99

    return lkp


def get_reverse_lkp_value(lkp_name: str, lkp_id):
    '''

    :param lkp_name: welches lkp soll verwendet werden
    :param lkp_id: welche id soll gelookupt werden
    :return: gibt die auspaegung des lkp values zurück
    '''
    db_con = connect_to_db(layer='biz')
    schema = 'biz'
    metadata = MetaData(bind=db_con)
    metadata.reflect(bind=db_con, schema=schema)

    lkp = pd.read_sql_table(con=db_con, schema=schema, table_name='lkp_' + lkp_name)

    lkp = lkp[lkp['ID'] == lkp_id]

    return lkp['auspraegung'].values[0]
