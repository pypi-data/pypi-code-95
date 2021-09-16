# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime, timedelta


import pandas as pd


from idebug import *
from kiwoomde import *


from kiwoomdsc.viewer import print_title



FILTER = {'lst_dt':{'$gte':datetime(1970,1,1)}}


def get_df(markets=None):
    filter = FILTER.copy()
    if isinstance(markets, list):
        filter.update({'mktcd':{'$in':markets}})

    model = BaseModel('Company')
    data = model.load(filter, {'lst_dt':1})
    return pd.DataFrame(data)


def listed_issues_cnt_dist(markets=None, period='H'):
    """
    주기별 상장종목 개수의 분포.
    """
    df = get_df(markets).set_index('lst_dt').sort_index().rename(columns={'_id':'cnt'})
    g = df.resample(period).count()

    print_title('일자별 상장종목 개수의 분포')
    g = g.reset_index(drop=False)
    g.lst_dt = g.lst_dt.apply(lambda x: x.isoformat()[:10])
    print(g)
    g.plot.bar(x='lst_dt', y='cnt', figsize=(30,8))



def issues_cnt_by_market_category():
    """
    시장종류별 종목수.
    """
    model = BaseModel('Company')
    filter = FILTER.copy()
    mktcds = model.distinct('mktcd', filter)
    data = []
    for mktcd in mktcds:
        filter.update({'mktcd':mktcd})
        n = model.count_documents(filter)
        data.append({'market':mktcd, 'cnt':n})

    selector = SelectorModel('MarketGubun')
    # selector.view(projection={'_id':0})

    df = pd.DataFrame(data)
    df.market = df.market.apply(lambda x: selector.select(code=x).name)
    print_title('시장종류별 종목수')
    print(df)
    df.plot.bar(x='market', y='cnt', figsize=(30,8))
    # 파이그래프로 점유율 표시
