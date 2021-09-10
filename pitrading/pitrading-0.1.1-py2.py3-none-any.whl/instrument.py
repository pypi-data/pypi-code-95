#! /usr/bin/python3

from datetime import datetime, timedelta, date
import sys
import pandas as pd
import os
import sqlite3

from pandas.core.arrays import boolean
from .holidays import Holidays
import numpy as np

class Instrument:
    """
    Handy wrapper of instrument.db files
    """
       
    tencent_addr = "https://market-data-1302861777.cos.ap-shanghai.myqcloud.com/"
    public_addr = "public/promisedland/"
    
    def __init__(self, dt:str, morning:boolean = False):
        """
        Returns an instance of Instrument class for instrument.db

        Parameters
        ----------
        dt: date string for an instrument
        morning: set True for instrument_%Y%m%d_8am.db
                 set False for instrument_%Y%m%d_prod.db
                 default is False

        Raises
        ----------
        FileNotFoundError
            * If the specified instrument is not on COS

        Examples
        --------
        >>> ins = Instrument("20210908", morning=True)
        >>> ins = Instrument("20210908")
        """
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
        
        """
        Return the contract mapping of an Instrument instance

        Parameters
        ----------
        tab : table that select {col} from, default is 'Options'
        col: columns that select from {tab}, default is '['code', 'type', 'strike', 'expiration', 'unit']'
        colnames: column names of the returned Pandas DataFrame

        Examples
        --------
        >>> ins = Instrument("20210908", morning=True)
        >>> ins.get_contract_mapping()
        >>> 	code	type	strike	expiration	unit
            0	IO2009-C-3100	1.0	3100.0	2020-09-18	100
            1	IO2009-C-3200	1.0	3200.0	2020-09-18	100
            2	IO2009-C-3300	1.0	3300.0	2020-09-18	100
            3	IO2009-C-3400	1.0	3400.0	2020-09-18	100
            4	IO2009-C-3500	1.0	3500.0	2020-09-18	100
            ...	...	...	...	...	...
            11	IF2112	0.0	NaN	2021-12-17	300
            12	IF2107	0.0	NaN	2021-07-16	300
            13	IF2108	0.0	NaN	2021-08-20	300
            14	IF2203	0.0	NaN	2022-03-18	300
            15	IF2110	0.0	NaN	2021-10-15	300
            948 rows × 5 columns
        """
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
        """
        Return 4 tradable Futures codes of an Instrument instance

        Examples
        --------
        >>> ins = Instrument("20210908", morning=True)
        >>> ins.get_tradable_contracts()
        >>> [('IF2203',), ('IF2112',), ('IF2110',), ('IF2109',)]
        """
        conn = sqlite3.connect(self.cache)
        cur = conn.cursor()
        cur.execute(f"SELECT code FROM Futures ORDER BY code DESC LIMIT 4;")
        ret = cur.fetchall()
        return ret