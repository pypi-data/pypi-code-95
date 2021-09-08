#! /usr/bin/python3

from datetime import datetime, timedelta, date
import sys
import pandas as pd
import os
import sqlite3

from pandas.core.arrays import boolean
from holidays import Holidays
import numpy as np

class Instrument:
       
    tencent_addr = "https://market-data-1302861777.cos.ap-shanghai.myqcloud.com/"
    public_addr = "public/promisedland/"
    
    def __init__(self, dt:str, morning:boolean = False):
        self.dt = Holidays.to_datetime(dt)
        self.morning = morning
        self._cache_instrument_db()

    def __del__(self):
        try:
            os.remove(self.cache)
        except FileNotFoundError:
            pass
        except OSError:
            pass

    def _cache_instrument_db(self) -> int:
        if Holidays.tradingday(self.dt):
            dt_str = self.dt.strftime("%Y-%m-%d")
            sub_dir = self.dt.strftime("%Y/%m/")
        else:
            dt_str = Holidays.prev_tradingday(self.dt).strftime("%Y-%m-%d")
            sub_dir = Holidays.prev_tradingday(self.dt).strftime("%Y/%m/")
        if self.morning:
            remote_db_name = f"instrument_{dt_str}_8am.db"
        else:
            remote_db_name = f"instrument_{dt_str}_prod.db"
        local_db_name = f"tmp_{remote_db_name}"
        remote_url = f"{self.tencent_addr}{self.public_addr}{sub_dir}{remote_db_name}"
        if not os.path.exists(local_db_name):
            cmd = f"curl -o {local_db_name} {remote_url}"
            print(cmd)
            os.system(cmd)
        self.cache = local_db_name
        if os.path.getsize(self.cache) < 1024:
            self.__del__()
            raise FileNotFoundError(f"Remote instrument db cache failed, check remote URL:{remote_url}")
        return 0

    def get_contract_mapping(self, 
                            tab='Options',
                            col=['code', 'type', 'strike', 'expiration', 'unit'],
                            colnames=['code', 'type', 'strike', 'expiration', 'unit']) -> pd.DataFrame:
        conn = sqlite3.connect(self.cache)
        cur = conn.cursor()
        columns = ', '.join(col)
        cur.execute(f"SELECT {columns} FROM Options;")
        opt_df = pd.DataFrame.from_records(cur.fetchall(), columns=col)
        cur.execute(f"SELECT code, type, expiration, unit FROM Futures;")
        fut_df = pd.DataFrame.from_records(cur.fetchall(), columns=['code', 'type', 'expiration', 'unit'])
        fut_df['strike'] = np.nan
        ret = pd.concat([opt_df, fut_df])
        ret['expiration'] = pd.to_datetime(ret['expiration'], format='%Y%m%d')
        ret['expiration'] = ret['expiration'].astype(str)
        ret.columns = colnames
        return ret

    def get_tradable_contracts(self):
        conn = sqlite3.connect(self.cache)
        cur = conn.cursor()
        cur.execute(f"SELECT code FROM Futures ORDER BY code DESC LIMIT 4;")
        ret = cur.fetchall()
        return ret