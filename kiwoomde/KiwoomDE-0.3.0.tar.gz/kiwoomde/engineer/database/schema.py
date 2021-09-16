# -*- coding: utf-8 -*-
import re
from datetime import datetime, date, time
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *


from kiwoomde import config
from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.utils.vparser import ValueDtypeParser
from kiwoomde.utils.viewer import pretty_title
from kiwoomde.engineer.database import *




class SchemaModel(BaseClass):
    # 정적 스키마: 미리 정의되어 저장되어 있는 컬렉션
    # 동적 스키마: 일반 컬렉션 데이타에 필터를 적용하여 스키마로 재생성하는 메모리DB
    # schemaName: 스키마로 사용할 컬렉션명.
    # filter: 스키마 MDB 생성을 위한 고정필터.
    # rename: 스키마용 컬렉션의 정규화된 스키마 MDB로 변환하기 위한 컬럼명 매핑 정보.
    # mdb: 스키마를 저장할 MemoryDB(DataFrame)

    # column: 컬럼명
    # dtype: 데이터 타입
    # role: 역할
    # desc: 설명
    # extra: 추가 스키마 여부
    SchemaStructure = ['column','dtype','role','desc','extra']
    # SchemaStructure = 'column,dtype,role,desc,extra'.split(',')

    def __init__(self, modelName):
        self.modelName = modelName
        self.collName = f"_Schema_{self.modelName}"
        self.schemaType = 'Static'
        self.filter = {}
        self._setup_mdb()

    def find(self, filter=None, projection=None, **kw):
        filter = {} if filter is None else filter
        filter.update(self.filter)
        return db[self.collName].find(filter, projection, **kw)

    def distinct(self, key, filter=None):
        filter = {} if filter is None else filter
        filter.update(self.filter)
        return db[self.collName].distinct(key, filter)

    def get_fpath(self):
        fpath = f'{config.datapath.SchemaCSVPath}/{self.modelName}.csv'
        return config.clean_path(fpath)

    @funcIdentity
    def create(self):
        # 정적-스키마 생성
        fpath = self.get_fpath()
        df = pd.read_csv(fpath)
        db[self.collName].drop()
        db[self.collName].insert_many(df.to_dict('records'))
        logger.info(f'Done. fpath: {fpath}')

    @funcIdentity
    def emit(self):
        fpath = self.get_fpath()
        self.mdb.to_csv(fpath, index=False)
        logger.info(f'Done. fpath: {fpath}')

    @funcIdentity
    def create_dynamic(self, schemaName, filter, rename, extra=[], keycols=[]):
        # 동적-스키마 생성
        self.collName = schemaName
        self.schemaType = 'Dynamic'
        self.filter = {} if filter is None else filter
        self._setup_mdb()

        # 스키마테이블 구조로 정규화한다.
        self.mdb = self.mdb.rename(columns=rename)
        self.mdb = self.mdb.reindex(columns=self.SchemaStructure).assign(extra= False)

        # 추가 스키마를 덧붙인다.
        if len(extra) > 0 and len(self.mdb) > 0:
            for d in extra:
                if d['column'] == 'dt':
                    d.update({'dtype':'dt', 'desc':'dt'})
            df = pd.DataFrame(extra).assign(extra= True)
            self.mdb = df.append(self.mdb.sort_values('column')).reset_index(drop=True)

        # 동적-스키마이므로, 키컬럼을 업데이트해줘야한다
        if len(keycols) > 0:
            df = self.mdb.copy()
            TF = df.column.isin(keycols)
            df = df[TF]
            df.role = 'key'
            self.mdb.update(df)

        return self

    def _setup_mdb(self):
        cursor = self.find(None, {'_id':0})
        self.mdb = pd.DataFrame(list(cursor))
        if len(self.mdb) == 0:
            logger.critical(f"해당 모델({self.modelName}) 스키마데이터({self.collName})가 존재하지 않는다.")
        return self

    @funcIdentity
    def view(self, filter=None, jupyter=True):
        df = self.mdb.copy()
        if filter is not None:
            for k,v in filter.items():
                TF = df[k].str.contains(v)
                df = df[TF]

        pretty_title(f"{self.schemaType}Schema: {self.collName} ({self.modelName})", simbol='#')
        if jupyter:
            return df
        else:
            print(df)

    def get_columns(self, filter=None):
        filter = {} if filter is None else filter
        df = self.mdb.copy()
        # 기본적으로 문자열 검색이기 때문에 모든 None 을 스트링으로 강제변환 후 검색.
        df = df.fillna('_None')

        for k,v in filter.items():
            if isinstance(v, str):
                TF = df[k].str.contains(v)
                df = df[TF]
            elif isinstance(v, bool):
                df = df.query(f'{k} == {v}')
        return list(df.column)

    def get_dtype(self, colName):
        if colName in list(self.mdb.column):
            df = self.mdb.query(f'column == "{colName}"')
            return df.reset_index(drop=True).at[0, 'dtype']
        else:
            logger.critical(f"스키마테이블에 컬럼명 '{colName}' 은 존재하지 않는다.")

    def get_dtypeDict(self):
        dtype = {}
        for d in self.mdb.to_dict('records'):
            dtype.update({d['column']:d['dtype']})
        return dtype

    def parse_value(self, colName, value):
        dtype = self.get_dtype(colName)
        return value if dtype is None else ValueDtypeParser(value, dtype)

    def parse_data(self, data):
        try:
            """Data 청소
            schemaName 이 TRItem, RealtimeFID 일 경우,schemacols 가 동적으로 변화하기 때문에 주의해야 한다.
            드랍 순서 중요 --> 반드시 Row 부터 드랍.
            """
            df = pd.DataFrame(data)
            df = df.dropna(axis=0, how='all')
            df = df.dropna(axis=1, how='all')
            data = df.to_dict('records')
        except Exception as e:
            logger.exception(e)
            raise
        else:
            """Data 파싱."""
            for d in data:
                for k,v in d.items():
                    d[k] = self.parse_value(colName=k, value=v)
            return data

    def astimezone(self, data):
        TF = self.mdb['dtype'].isin(['dt','date','time'])
        dtcols = list(self.mdb[TF].column)

        for d in data:
            for c in dtcols:
                if c in d:
                    d[c] = DatetimeParser(d[c])
        return data

    def get_datacls(self, d):
        # 스키마에 정의된 컬럼만 추출해서 데이타클래스를 생성하여 반환
        cols = list(self.mdb.column)
        d = {k: self.parse_value(k, v) for k,v in d.items() if k in cols}
        return BaseDataClass(**d)

    @funcIdentity
    def dist_per_dtype_pat(self):
        cursor = db[self.collName].find()
        df = pd.DataFrame(list(cursor))

        pretty_title(f"Dist. Per Dtype ({collName})")
        g = df.fillna('_None').groupby('dtype').count()
        print(g)

        pretty_title(f"Dist. Per pat ({collName})")
        g = df.fillna('_None').groupby('pat').count()
        print(g)

    @funcIdentity
    def view_having_pat(self):
        for dtype in ['date','time','dt']:
            PartGubun(f"dtype: {dtype}")

            cursor = db[self.collName].find({'dtype':dtype}, {'_id':0})
            df = pd.DataFrame(list(cursor))

            pretty_title(self.collName)
            print(df)

    @funcIdentity
    def view_groupDF_byDtype(self, projection={'_id':0}, sort=()):
        cursor = db[self.collName].find(None, projection)
        df = pd.DataFrame(list(cursor))

        for n, g in df.groupby('dtype'):
            SectionGubun(n)
            if len(sort) > 0:
                g = g.sort_values(sort[0], ascending=sort[1])
            g = g.reset_index(drop=True).dropna(axis=1, how='all').drop(columns=['dtype'])
            print(g[:60])
            if len(g) > 60: print(g[60:120])
            if len(g) > 120: print(g[120:])
