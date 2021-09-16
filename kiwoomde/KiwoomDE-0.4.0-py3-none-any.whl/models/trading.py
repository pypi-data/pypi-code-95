# -*- coding: utf-8 -*-
import re


import pandas as pd


from idebug import *


from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.database import *
from kiwoomde.models.base import KWModel


class TradingSourceRealData(KWModel):
    # 주식당일거래원(Realtype) 실시간데이타를 재구조화해서 저장하는 모델.
    # 거래원(TradingSource) 1개당 컬렉션 하나를 가지며, 여러개의 종목들을 포함한다
    # RealtypeModel 로부터 데이터를 가져와서 재구조화해서 저장하는 함수를 포함
    # 단일 정적스키마를 모든 거래원이 동일하게 가진다
    # source: SourceName, 거래원을 특정하는 파라미터

    def __init__(self, source, collmode='real'):
        super().__init__(modelName='TradingSourceRealData', collmode=collmode)
        self.SecurityInfo = SelectorModel('SecurityInfo').select(name=source)
        self.Company = SelectorModel('Company')
        self.collName = f"{self.collName}_{self.SecurityInfo.code}"
        self.issueList = self.Company.distinct('name', {'_id':{'$in':self.distinct('cid')}})
        # 자동계산으로 추가되는 스키마컬럼들은 동적으로 할당해야 할 것 같은데?

    @funcIdentity
    def switch_issue(self, **cid):
        self.Company.select(**cid)
        return self

    def _default_filter(self, filter):
        filter = {} if filter is None else filter
        filter.update({'cid':self.Company._id})
        return filter

    def _default_projection(self, projection):
        projection = {'_id':0, 'cid':0, 'name':0} if projection is None else projection
        return projection

    def _default_kw(self, **kw):
        kw.update({'sort':[('dt',DESCENDING)]})
        return kw

    @funcIdentity
    def load(self, filter=None, projection=None, **kw):
        filter = self._default_filter(filter)
        projection = self._default_projection(projection)
        kw = self._default_kw(**kw)
        cursor = self.find(filter, projection, **kw)
        data = self.schema.astimezone(list(cursor))
        data = self._dropna(data)
        return data
