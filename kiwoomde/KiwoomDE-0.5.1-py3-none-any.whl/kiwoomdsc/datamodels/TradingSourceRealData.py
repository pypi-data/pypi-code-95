# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
import re


import pandas as pd


from idebug import *
from kiwoomde import *
from kiwoomde.dba import *

from kiwoomdsc import stat
from kiwoomdsc.datamodels.base import *



class Analyzer(KWModelBaseAnalyzer):
    # 'TradingSourceRealData'모델에 대한 분석클랙스
    # 관여한 모든 거래원에 대해서 분석해야한다
    # 종목을 변경해가면서 분석할 수 있어야 한다 ==> 과연? 종목은 고정시키면 안되나?
    # TradingSourceRealData 모델 스키마 자체가 설계시부터 거래원 중심으로 분석하는 것이 목적이므로
    # (예를들어, 특정거래원이 다수의 종목에서 얼마만큼의 매수/매도를 하고 있는지 분석하는 것)
    # 종목을 고정시키면 안된다
    # 해당 종목에 대한 주식당일거래원 리스트를 보유하고 있어야 한다

    def __init__(self, collmode='real'):
        self.collmode = collmode

    def _set_sourceList(self):
        df = CollectionList('TradingSourceRealData').query('collmode == "Test"')
        source_codes = list(df.param)
        names = SelectorModel('SecurityInfo').distinct('name', {'code':{'$in':source_codes}})
        self._sourceList = names

    @funcIdentity
    def switch_source(self, source):
        self.model = TradingSourceRealData(source, collmode=self.collmode)
        # 현재 셋업된 거래원명
        self.sourceName = self.model.SecurityInfo.name
        return self

    @funcIdentity
    def switch_issue(self, **cid):
        self.model.switch_issue(**cid)
        # 현재 셋업된 종목명
        self.issueName = self.model.Company.name
        return self

    def _auto_calc(self, data):
        # 순매수증감 계산을 위해서 시간-오름차순으로 정렬해야한다
        df = pd.DataFrame(data).sort_values('dt')
        df = df.assign(순매수증감= lambda x: x.매수증감 - x.매도증감)
        return df.to_dict('records')

    def load_data(self, filter=None, projection=None, limit=60, sort=[('dt',ASCENDING)], **kw):
        # 기본값으로 당일 거래데이타만 로딩한다
        af = AutoFilter(self.model.schema).search(filter)
        af.lastday().repr()
        data = self.model.load(af.filter, limit=limit, sort=sort, **kw)
        data = self._auto_calc(data)
        return data

    def rank(self, data):
        df = pd.DataFrame(data)
        rv = df.rank(method='max')
        print(rv)

    def describe(self, data):
        df = pd.DataFrame(data)
        rv = df.describe()
        rv = rv.applymap(lambda x: int(x))
        rv = rv.style.format(formatter='{:,}')
        return rv

    def vis(self, data):
        # 증감은  막대그래프, 수량은 선그래프로 나타낸다
        pass
