# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime


import pandas as pd


from idebug import *
from kiwoomde import *




def get_df(filter=None, projection=None, **kw):
    model = TRModel('OPT10023', collmode='test')
    data = model.load(filter, projection, **kw)
    return pd.DataFrame(data)


def count_daily_docs(filter=None, **kw):
    """
    일별 개수.
    """
    df = get_df(filter, projection={'dt':1}, **kw)
    df = df.set_index('dt').resample('1D').count()
    return df


def count_daily_unique_issues(filter=None, **kw):
    """
    일별 유일한 종목명 개수.
    """
    df = get_df(filter, {'종목명':1, 'dt':1}, **kw)
    df.dt = df.dt.apply(lambda x: datetime(x.year, x.month, x.day))
    df = df.drop_duplicates(keep='last', subset=['dt','종목명'])
    df = df.set_index('dt').resample('1D').count()
    return df


def upsurge_cnt_dist(filter={}, markets=['0','10'], period='Q', ndigitsX=2):
    """
    거래량급증률 분포.
    """
    params = str(locals())
    colName = '급증률'

    if len(markets) > 0:
        names = db.Company.distinct('name', {'mktcd':{'$in':markets}})
        filter.update({'종목명':{'$in':names}})


    df = get_df(filter, {colName:1})
    df = df.rename(columns={'_id':'cnt'})
    df[colName] = df[colName].apply(lambda x: round(x, ndigitsX))
    # print(df)

    g = df.groupby(colName).count()
    g = g.reset_index(drop=False)
    # print(g)

    # 급증률 단위 %로 변환
    g[colName] = g[colName].apply(lambda x: f"{round(x*100, ndigitsX-2)}%")
    # print(g)

    g.plot.bar(x=colName, y='cnt')
    return g
