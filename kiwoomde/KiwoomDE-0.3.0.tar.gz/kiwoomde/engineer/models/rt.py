# -*- coding: utf-8 -*-
import re
from itertools import product

import pandas as pd


from idebug import *
from kiwoomde.engineer.database import *


from kiwoomde.engineer.models.base import KWModel
from kiwoomde.engineer.models._util import AutoFilter, FidAutoFilter, FidAutoProjection
from kiwoomde.utils.viewer import *


def RTModel(realtype=None, collmode='real', **cid):
    # if modelName == 'Realtime':
    #     return RealtimeModel(collmode, **cid)
    # elif modelName == 'Realtype':
    #     return RealtypeModel(realtype, collmode, **cid)
    # elif modelName == 'Chejan':
    #     return ChejanModel(collmode)
    if realtype is None:
        return RealtimeModel(collmode, **cid)
    else:
        return RealtypeModel(realtype, collmode, **cid)


class BaseRTModel(KWModel):

    def __init__(self, modelName, collmode):
        super().__init__(modelName, collmode)

    @funcIdentity
    def find(self, filter=None, projection=None, **kw):
        self.af.search(filter)
        self.ap.set(projection)
        return db[self.collName].find(self.af.filter, self.ap.projection, **kw)

    def _termdict(self):
        dic = {}
        data = self.schema.mdb.loc[:, ['column','desc']].to_dict('records')
        for d in data:
            if d['desc'] is not None:
                dic.update({d['column']: d['desc']})
        return dic

    def _reverse_termdict(self):
        return {v:k for k,v in self._termdict().items()}

    def translate(self, data):
        return pd.DataFrame(data).rename(columns=self._termdict()).to_dict('records')

    def view(self, filter=None, projection=None, **kw):
        data = self.load(filter, projection, **kw)
        # FID는 반드시 번역해야한다
        data = self.translate(data)
        df = pd.DataFrame(data)
        pretty_title(f"{self.collName} [{self.schema.collName}]")
        return df


class RealtimeModel(BaseRTModel):
    # FID 총 336개를 단 하나의 컬렉션에 저장한다.

    def __init__(self, collmode='real', **cid):
        super().__init__(modelName='Realtime', collmode=collmode)
        self._extend_cidmodel(**cid)
        self.schema.create_dynamic(schemaName='RealtimeFID',
                                filter=None,
                                rename={'fid':'column','name':'desc'},
                                extra=[{'column':'dt'}])
        self.af = FidAutoFilter(self.schema)
        self.ap = FidAutoProjection(self.schema)


class RealtypeModel(BaseRTModel):
    # realtype 을 결정지은 RealtimeModel.

    def __init__(self, realtype, collmode='real', **cid):
        self.realtype = realtype
        super().__init__(modelName='Realtime', collmode=collmode)
        self._extend_cidmodel(**cid)
        self.schema.create_dynamic(schemaName='RealtimeFID',
                                filter={'realtypes':{'$in':[self.realtype]}},
                                rename={'fid':'column','name':'desc'},
                                extra=[{'column':'dt'}])
        self.af = FidAutoFilter(self.schema)
        self.ap = FidAutoProjection(self.schema)
        self._set_fixed_filter_projection()

    def _set_fixed_filter_projection(self):
        if self.realtype in ['종목프로그램매매']:
            self.af.set_fixed_filter({'체결시간':{'$ne':None}, '매수금액':{'$ne':None}})
        elif self.realtype in ['주식호가잔량']:
            self.af.set_fixed_filter({'호가시간':{'$ne':None}})
        elif self.realtype in ['주식당일거래원']:
            self.af.set_fixed_filter({'매도거래원1':{'$ne':None}})

        self.ap.set_fixed_proj({'_id':0}).set_pure_fids()

    @funcIdentity
    def load_one(self, **kw):

        # 방법1
        # self.ap.set({'dt':1})
        # cursor = self.find()
        # data = self.schema.astimezone(list(cursor))
        # df = pd.DataFrame(data)
        # df.dt = df.dt.apply(lambda x: x.replace(hour=0,minute=0,second=0))
        # dts = list(df.dt.unique())

        # 방법2
        dts = self.distinct('dt', self.af.filter)
        dts = [self.schema.parse_value('dt', dt) for dt in dts]
        dts = sorted(set([dt.replace(hour=0,minute=0,second=0) for dt in dts]), reverse=True)

        pp.pprint(dts)

        if len(kw) == 0:
            self.af.today()
        else:
            self.af.oneday(**kw)
        cursor = self.find()
        return self.schema.astimezone(list(cursor))

    @funcIdentity
    def load_more(self):
        # 하루씩 더 로딩하도록 필터를 업데이트
        """filter.update({})"""
        cursor = self.find()
        return self.schema.astimezone(list(cursor))


class ChejanModel(BaseRTModel):
    def __init__(self, collmode='real'):
        super().__init__(modelName='Chejan', collmode=collmode)
        self.schema.create_dynamic(schemaName='ChejanFID',
                                filter=None,
                                rename={'fid':'column','name':'desc'},
                                extra=[{'column':'dt'}])
        self.af = FidAutoFilter(self.schema)
        self.ap = FidAutoProjection(self.schema)
        # self.af.search({'주문/체결시간':None})
        self.ap.set_fixed_proj({'_id':0}).set({'dt':0})


class RealtypeTradingSource(KWModel):
    # 실시간타입(주식당일거래원) 중 거래원별 매매수량 모델
    # 주식당일거래원(Realtype) 실시간데이타를 재구조화해서 저장
    # 종목 1개당 컬렉션 하나를 가지며, 여러개의 거래원(TradingSource)들을 포함한다

    def __init__(self, collmode='real', **cid):
        super().__init__(modelName=self.__class__.__name__, collmode=collmode)
        self._extend_cidmodel(**cid)

        # PartGubun('거래원정보 셋업')
        self.SecurityInfo = SelectorModel('SecurityInfo')
        # 컬렉션에 존재하는 거래원 리스트
        self._sourceList = self.SecurityInfo.view({'code':{'$in':self.distinct('src')}}, {'_id':0})
        # 가장최근일(오늘) 기준 컬렉션에 존재하는 거래원 리스트
        af = AutoFilter(self.schema).lastday()
        self._lastSourceList = self.SecurityInfo.view({'code':{'$in':self.distinct('src',af.filter)}}, {'_id':0})

        # 일자별 데이타 저장소
        self._storage = {}

    @funcIdentity
    def switch_source(self, **src):
        # 주식거래원을 변경
        self.SecurityInfo.select(**src)
        self._current_source = self.SecurityInfo.name
        return self

    def get_last_dt(self):
        # RealtypeTradingSource 모델에 저장된 가장 최근 dt를 반환
        dts = self.distinct('dt')
        return dts[-1].astimezone() if len(dts) > 0 else None

    def _restructure_realdata(self, doc):
        # 주식당일거래원(=realtype) 실시간데이타를 재구조화

        # PartGubun('재구조화된 data 생성')
        pats = []
        for type, i in product(['매수','매도'], range(1,6)):
            pats.append(re.compile(f'^({type})거래원(.+)*({i})$'))

        data = []
        for p in pats:
            d = {}
            for k,v in doc.items():
                m = p.search(k)
                if m is not None:
                    type, info, rank = m.groups()
                    info = '명' if info is None else info
                    info = '증감' if info == '별증감' else info
                    d.update({'dt':doc['dt'], 'rank':rank})
                    if info in ['수량','증감']:
                        d.update({f'{type}{info}':v})
                    elif info in ['명','코드']:
                        d.update({info:v})
                    data.append(d)

        df = pd.DataFrame(data)

        # PartGubun('동일 거래원으로 데이타를 병합')
        gs = []
        for n,g in df.groupby(['명','코드']):
            g = g.fillna(method='ffill').fillna(method='bfill').drop_duplicates(keep='first')
            gs.append(g)
        df = pd.concat(gs).fillna(0)

        # PartGubun('스키마에 맞게 변환')
        df = df.rename(columns={'코드':'src'})
        df = df.reindex(columns=self.schema.get_columns())
        return self.schema.parse_data(df.to_dict('records'))

    def _default_filter(self, filter):
        filter = {} if filter is None else filter
        if 'src' in filter:
            if re.search('\d+', filter['src']) is None:
                self.SecurityInfo.select(name=filter['src'])
                filter['src'] = self.SecurityInfo.code

        return filter

    def _default_projection(self, projection):
        projection = {'_id':0} if projection is None else projection
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

    @funcIdentity
    def load_last(self, filter=None, projection=None, **kw):
        # 가장최근일 데이터를 로딩
        filter = {} if filter is None else filter
        af = AutoFilter(self.schema).lastday()
        filter.update(af.filter)
        data = self.load(filter, projection, **kw)

        return

    @funcIdentity
    def load_more(self, filter=None, projection=None, **kw):
        # 하루씩 로딩
        filter = {} if filter is None else filter

        return self.load(filter, projection, **kw)
