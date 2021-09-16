# -*- coding: utf-8 -*-
import re
import os
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *


from kiwoomde import config
from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.engineer.database import *
from kiwoomde.engineer.models._util import AutoFilter, FidAutoFilter, FidAutoProjection, assign_dtype


class KWModel(DataModel):
    # Kiwoom Base Model

    def __init__(self, modelName, collmode='real'):
        super().__init__(modelName, collmode)

    def _extend_cidmodel(self, **cid):
        # eXtended-CID-Model 로 변환 (extend a model to cid-model)
        # modelName에 cid를 추가하여 collName을 만듦으로써, 컬렉션을 확장하는 모델
        if len(cid) > 0:
            cid.update({'active':True})
            self.cidentify(**cid)
            self.collName = f"{self.modelName}__{self.cid}"
            self.apply_collmode(self.collmode)
        else:
            logger.critical(f'{self.modelName} 모델은 반드시 종목을 특정해야 한다')
            raise
        return self

    @funcIdentity
    def cidentify(self, **cid):
        # 빅히트/하이브 처럼 2개 이상 존재할 경우를 고려하라. 종목코드는 같고, cid가 다르다.
        # 나중에 업데이트된 것을 골라야 한다.
        self.Company = SelectorModel('Company').select(**cid)
        self.cid = self.Company._id
        self.issueName = self.Company.name
        self.issueCode = self.Company.code
        return self

    def reindex(self, df, columnPattern):
        cols = list(df.columns)
        cols = [c for c in cols if re.search(columnPattern, string=c) is not None]
        return df.reindex(columns=cols)

    def _dropna(self, data):
        if len(data) > 0:
            df = pd.DataFrame(data)
            len0 = f"({len(df)}, {len(df.columns)})"

            subset = list(df.columns)
            if 'dt' in subset:
                subset.remove('dt')
            df = df.dropna(axis=0, how='all', subset=subset)
            df = df.dropna(axis=1, how='all')

            len1 = f"({len(df)}, {len(df.columns)})"
            logger.debug(f"{len0} --> {len1}")
            return df.to_dict('records')
        else:
            return []

    def select(self, filter=None, projection=None, **kw):
        af = AutoFilter(self.schema).search(filter)
        data = self.load(af.filter, projection, **kw)
        try:
            self.selected = BaseDataClass(dataname=f'{self.modelName}-Selected', **data[0])
        except Exception as e:
            logger.exception(e)
        return self
