import warnings

import pandas as pd
import pymysql


class MysqlPool:

    def __init__(self, config):
        self._conn = pymysql.connect(**config)

    def fetch_data(self, sql):
        data = pd.read_sql(sql, self._conn)
        return data

    def execute_sql(self, sql):
        cursor = self._conn.cursor()
        cursor.execute(sql)
        self._conn.commit()

    def insert_df(self, table, df: pd.DataFrame):
        if df.empty:
            warnings.warn("EMPTY DATAFRAME!")
            return
        cols = "(`{}`)".format("`,`".join(df.columns.to_list()))
        for idx, row in df.iterrows():
            tmp = []
            for r in row:
                if pd.isna(r):
                    tmp.append("null")
                elif isinstance(r, str):
                    tmp.append("'{}'".format(r))
                else:
                    tmp.append("'{}'".format(r))
            v = "({})".format(",".join(tmp))
            sql = "INSERT INTO {} {} VALUES {}".format(table, cols, v)
            self.execute_sql(sql)

    def close(self):
        if self._conn:
            self._conn.close()


def mysql_fetch_data(db_config, sql):
    db = MysqlPool(db_config)
    res = db.fetch_data(sql)
    db.close()
    return res


def mysql_execute(db_config, sql):
    db = MysqlPool(db_config)
    db.execute_sql(sql)
    db.close()


def mysql_insert_df(db_config, table, df):
    db = MysqlPool(db_config)
    db.insert_df(table, df)
    db.close()
