import pymysql
import logging
import pandas as pd
from flask import g, jsonify, make_response, current_app as app


def _connect_db(db_key):
    db = app.config['DATABASE'][db_key]
    return pymysql.connect(
        host=db['host'],
        user=db['user'],
        password=db['password'],
        database=db['dbname'],
        autocommit=True,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def get_db_rekonsiliasi():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_rekonsiliasi'):
        g.db_rekonsiliasi = _connect_db('db_rekonsiliasi')
    return g.db_rekonsiliasi


def get_db_sso():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_sso_gdcpay'):
        g.db_sso = _connect_db('db_sso_gdcpay')
    return g.db_sso

def get_db_admin():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_admin'):
        g.db_admin = _connect_db('db_admin')
    return g.db_admin


def get_db_ppob():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_ppob'):
        g.db_ppob = _connect_db('db_ppob')
    return g.db_ppob

def get_db_member_gdc():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_member_gdc'):
        g.db_member_gdc = _connect_db('db_member_gdc')
    return g.db_member_gdc

def get_db_admin_ppob():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_admin_ppob'):
        g.db_admin_ppob = _connect_db('db_admin_ppob')
    return g.db_admin_ppob

def get_db_helpdesk():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_customer_service'):
        g.db_helpdesk = _connect_db('db_customer_service')
    return g.db_helpdesk

def get_db_member():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_member_gdc'):
        g.db_member = _connect_db('db_member_gdc')
    return g.db_member

def get_db_gdcpay():
    # tambahkan di __init__.py bagian function close_db
    if not hasattr(g, 'db_gdcpay'):
        g.db_gdcpay = _connect_db('db_gdcpay')
    return g.db_gdcpay

def db_con():
    g.db_rekonsiliasi = _connect_db()
    return g.db_rekonsiliasi


def db_fetch(sql, param=None, rows=1):
    """
        rows = 1, return 1 row
        rows >1, return lebih dari 1 row
        return value berbentuk Pandas DataFrame
    """
    try:
        return pd.read_sql(sql, con=db_con(), params=param)
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def db_exec(sql, param, insert_many=False):
    """ Untuk Insert, Update & Delete """
    try:
        with db_con() as con:
            with con.cursor() as cursor:
                if insert_many is True:
                    cursor.executemany(sql, param)
                else:
                    cursor.execute(sql, param)
                # lakukan commit bila tanpa row
                con.commit()
                return True
    except Exception as e:
        logging.error(e, exc_info=True)
        return False

def exec_query(sql, params, db, t=1):
    # t = 0 / 1
    # 0 = expecting row affected
    # 1 = expecting return data
    
    try:
        connection=_connect_db(db)
        cursor = connection.cursor()
        cursor.execute(sql, params)

        if t == 0:
            row = cursor.rowcount

        elif t == 1:
            row = dictfetchall(cursor)

        cursor.close
    except Exception as e:
        print("Error executing query: ", e)
        print("Query : ", sql)
        row = 0

    return row


def to_client(data, new_token=None):
    # logging.info(f"[RETURN TO CLIENT] {data}")
    # return jsonify(data)
    resp = make_response(jsonify(data))
    return resp

def is_valid_element(prime_fields, client_request):
    # Melakukan pengecekan mandatory field harus ada pada saat client request
    return not set(prime_fields) <= set(client_request)