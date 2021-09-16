# -*- coding: utf-8 -*-
import re
from datetime import datetime, date, timedelta, time, tzinfo, timezone


from bson.objectid import ObjectId
import pandas as pd


from idebug import *


from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.database import *
from kiwoomde.utils.dt import last_tradeday
from kiwoomde.utils.vparser import DatetimeParser


class AutoFilter(BaseClass):

    def __init__(self, schema):
        self.schema = schema
        # 스키마와 별도로 컬렉션상 모든 컬럼들
        self.collcols = list(set(self.schema.get_columns() + ['_id']))
        self.strcols = self.schema.get_columns({'dtype':'str'})
        self.dtcols = self.schema.get_columns({'dtype':'date|time|dt'})
        self.boolcols = self.schema.get_columns({'dtype':'boolean'})
        self.filter = {}

    @funcIdentity
    def search(self, filter):
        for k,v in filter.items():
            if k in self.collcols:
                if isinstance(v, dict):
                    # MongoDB 오퍼레이터를 그대로 이용하라
                    self.filter.update({k:v})
                else:
                    if k in ['_id']:
                        self.filter.update({k: ObjectId(v)})
                    elif isinstance(v, bool):
                        self.filter.update({k:v})
                    elif k in self.strcols:
                        v = self.schema.parse_value(k, v)
                        self.filter.update({k: {'$regex':v, '$options':'i'}})
                    elif k in self.dtcols:
                        v = self.schema.parse_value(k, v)
                        self.filter.update({k:v})
                    else:
                        logger.critical('예상 못한 경우이기 때문에 개발 에러~')
                        raise
            else:
                logger.error(f'{k}컬럼은 스키마에 존재하지 않는다')
        return self

    @funcIdentity
    def today(self):
        t = datetime.today().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
        filters = []
        for c in self.dtcols:
            filters.append({c:{'$gte':t}})
        if len(filters) > 0:
            self.filter.update({'$or':filters})
        return self

    @funcIdentity
    def oneday(self, **kw):
        print(kw)
        for k,v in kw.items():
            if k in self.dtcols:
                fromdt = self.schema.parse_value(k, v)
                todt = fromdt + timedelta(days=+1)
                self.filter.update({k:{'$gte':fromdt, '$lt':todt}})
        return self

    @funcIdentity
    def period(self, fromdt, todt):
        fromdt = DatetimeParser(fromdt)
        todt = DatetimeParser(todt)
        filters = []
        for c in self.dtcols:
            filters.append({c:{'$gte':fromdt, '$lt':todt}})
        if len(filters) > 0:
            self.filter.update({'$or':filters})
        return self

    @funcIdentity
    def lastday(self):
        filters = []
        for c in self.dtcols:
            filters.append({c:{'$gte':last_tradeday()}})
        if len(filters) > 0:
            self.filter.update({'$or':filters})
        return self


class FidAutoFilter(BaseClass):
    # self.filter: DB검색에 최종 제공할 필터
    # self._fixed_filter: FidAutoFilter 클래스의 모든 메소드 실행시 반드시 실행할 기본 필터

    def __init__(self, schema):
        self._af = AutoFilter(schema)
        self.filter = {}

    def set_fixed_filter(self, f):
        f = self._translate_fid(f)
        self._fixed_filter = f

    def unset_fixed_filter(self):
        delattr(self, '_fixed_filter')

    def _apply_fixed_filter(self):
        if hasattr(self, '_fixed_filter'):
            self.filter.update(self._fixed_filter)
        return self

    def _termdict(self):
        dic = {}
        data = self._af.schema.mdb.loc[:, ['column','desc']].to_dict('records')
        for d in data:
            if d['desc'] is not None:
                dic.update({d['column']: d['desc']})
        return dic

    def _translate_fid(self, filter):
        # 컬럼명이 fid 숫자형태로 저장되어 있으므로, 문자열로 검색하도록 인터페이스를 제공하고
        # 이 함수에서 문자열을 fid로 자동변환하여 DB검색할 수 있어야 한다.
        d = self._termdict()
        rd = {v:k for k,v in d.items()}
        f = {}
        for k,v in filter.items():
            if k in rd:
                f.update({rd[k]: v})
            else:
                f.update({k: v})
        return f

    @funcIdentity
    def search(self, filter):
        filter = {} if filter is None else filter
        filter = self._translate_fid(filter)
        self._af.search(filter)
        self.filter.update(self._af.filter)
        return self._apply_fixed_filter()

    def today(self):
        self._af.today()
        self.filter.update(self._af.filter)
        return self._apply_fixed_filter()

    def oneday(self, **kw):
        self._af.oneday(**kw)
        self.filter.update(self._af.filter)
        return self._apply_fixed_filter()

    def period(self, fromdt, todt):
        self._af.period(fromdt, todt)
        self.filter.update(self._af.filter)
        return self._apply_fixed_filter()

    def lastday(self):
        self._af.lastday()
        self.filter.update(self._af.filter)
        return self._apply_fixed_filter()


class FidAutoProjection(BaseClass):

    def __init__(self, schema):
        self.schema = schema
        # 기본 프로젝션
        self.projection = {c:1 for c in list(self.schema.mdb.column)}

    def set_fixed_proj(self, p):
        self._fixed_proj = p
        return self

    def _apply_fixed_proj(self):
        if hasattr(self, '_fixed_proj'):
            self.projection.update(self._fixed_proj)
        return self

    def set_pure_fids(self):
        cols = self.schema.get_columns({'extra':False})
        self.projection = {c:1 for c in cols}
        return self._apply_fixed_proj()

    def set(self, proj):
        if proj is not None:
            self.projection = proj
        return self._apply_fixed_proj()


@funcIdentity
def assign_dtype(collName, column):
    # collName: dtype 을 정의할 컬렉션명
    # column: regex을 적용할 타겟컬럼
    tbl = db[collName]

    # 요청된 모델에 대해 컬렉션-컬럼의 dtype 초기값을 문자타입으로 일괄 업데이트.
    tbl.update_many({}, {'$set':{'dtype':'str'}})

    cursor = db.WordDtype.find().sort('order', ASCENDING)
    for d in list(cursor):
        pat = "|".join(d['regex'])
        filter = {column:{'$regex':pat}}
        update = {'$set':{'dtype':d['dtype']}}
        tbl.update_many(filter, update)

    logger.info(f'Done. collName: {collName}')
