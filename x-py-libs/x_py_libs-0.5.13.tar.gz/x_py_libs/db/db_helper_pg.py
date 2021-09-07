# -*- coding=utf-8 -*-

from enum import Enum
import sys
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor

from x_py_libs.db import BaseDBHelper

class PgDBHelper(BaseDBHelper):

    def connect(self):
        try:
            conn = psycopg2.connect(self.connect_string, cursor_factory=DictCursor)
            conn.set_client_encoding('UTF8')
            # print(conn)
            return conn
        except psycopg2.Error as e:
            print('psycopg2 error:', e.pgerror)
            return None

    
    def fetch_returning_id(self, sql, *params, **kw):
        sql = sql + """ RETURNING id;"""

        def callback(cur):
            rst = cur.fetchone()
            id = rst.get('id')
            return 0 if id is None else id

        return self.execute_sql(sql, callback, *params, **kw)

    def execute_many(self, sql, callback, *params, **kw):
        conn = self.connect()

        if conn == None:
            return None

        cur = conn.cursor(cursor_factory=RealDictCursor)
        # cur = conn.cursor()
        rst = None

        psycopg2.extras.execute_values(cur, sql, params, page_size=9999)

        rst = callback(cur)
        conn.commit()
        conn.close()
        # print('rst:',rst)
        return rst
        
    def execute_sql(self, sql, callback, *params, **kw):
        conn = self.connect()

        if conn == None:
            return None

        # print(sql, *params, type(params), len(params), **kw)
        is_multiple = False if kw.get('is_multiple') == None else kw['is_multiple']
        # print('--kw--:', kw, kw.get('is_multiple'), is_multiple)

        cur = conn.cursor(cursor_factory=RealDictCursor)
        # cur = conn.cursor()
        rst = None

        if is_multiple:
            psycopg2.extras.execute_values(cur, sql, params, page_size=9999)
        else:
            if params is not None:
                # print('sql:', cur.mogrify(sql, *params))
                cur.execute(sql, *params)
            else:
                cur.execute(sql)

        # rst = cur.fetchone()

        rst = callback(cur)
        conn.commit()
        conn.close()
        # print('rst:',rst)
        return rst

    def callproc(self, proc_name, *params):
        conn = self.connect()

        if conn == None:
            return None

        cur = conn.cursor()
        cur.callproc(proc_name, *params)
        rst = cur.fetchall()

        conn.commit()
        conn.close()
        return rst


"""
    # def execute_values(self, sql, *params):
    #     conn = db_helper.connect()

    #     if conn == None:
    #         return None

    #     print(params, type(params), list(params))

    #     cur = conn.cursor()
    #     psycopg2.extras.execute_values(cur, sql, params)
    #     rst = cur.rowcount
    #     conn.commit()
    #     conn.close()
    #     return rst
"""
