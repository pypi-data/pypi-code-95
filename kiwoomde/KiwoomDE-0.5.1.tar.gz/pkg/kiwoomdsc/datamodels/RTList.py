# -*- coding: utf-8 -*-
from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd
from bson.objectid import ObjectId


from idebug import *
from kiwoomde import *
from kiwoomde.models import *
from kiwoomde.dba import *


from kiwoomdsc import stat


def PureFIDs(realtype):
    filter = {'realtypes':{'$size':1, '$in':[realtype]}}
    fids = db.RealtimeFID.distinct('colName', filter)
    return fids


def FullFIDs(realtype):
    filter = {'realtypes':{'$in':[realtype]}}
    fids = db.RealtimeFID.distinct('colName', filter)
    return fids


@funcIdentity
def fids_cnt_each_realtype():
    """
    realtype 별로 PureFID 개수를 계산.
    개수가 0 이면, 다른 realtype 와 전부 중복된다는 의미.
    """
    realtypes = db.RTList.distinct('realtype')
    data = []
    for realtype in realtypes:
        pure_fids = PureFIDs(realtype)
        full_fids = FullFIDs(realtype)
        data.append({'realtype':realtype, 'n_pure_fids':len(pure_fids), 'n_full_fids':len(full_fids)})
    return pd.DataFrame(data).sort_values('n_pure_fids', ascending=False).reset_index(drop=True)


def n_docs_each_realtype(issueName):
    # realtype 별로 독자적FID 컬럼을 가진 Realtime__CID 문서개수를 계산.
    # 모든 realtypes 에 대해 실시간데이터 수집이 잘 되는지 확인하는데 사용.
    realtypes = db.RTList.distinct('realtype')
    data = []
    for realtype in realtypes:
        model = RTModel(realtype, 'test', name=issueName)
        n = model.count_documents()
        data.append({'realtype':realtype, 'n_docs':n})
    return pd.DataFrame(data).sort_values('n_docs', ascending=False).reset_index(drop=True)


def companies_having_realdata():
    # 실시간데이타 컬렉션 리스트의 종목정보를 보여줌
    df = dba.RealtimeCollectionList()
    df = df.query('collmode == "Test"')
    print(df)
    cids = list(df.param.unique())
    data = KWModel('Company').load({'_id':{'$in':cids}}, {'_id':0}, sort=[('name',ASCENDING)])
    return pd.DataFrame(data)
