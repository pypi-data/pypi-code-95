# -*- coding: utf-8 -*-
import re


import pandas as pd


from idebug import *


from kiwoomde.engineer.database import *
from kiwoomde.engineer.models.base import KWModel


def MetaModel(modelName):
    if modelName == 'TRInput':
        return TRInput()
    elif modelName == 'TRItem':
        return TRItem()
    elif modelName == 'RealtimeFID':
        return RealtimeFID()


class TRInput(KWModel):
    # TRList 컬렉션의 inputs 컬럼의 데이타를 재해석한 INPUT 중심 컬렉션

    def __init__(self):
        super().__init__(self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        # PartGubun('Phase-1: 신규 컬렉션 생성')
        data = self._structure_data()
        self.drop()
        self.insert_many(data)

        # PartGubun('Phase-2: 초기값 결정해서 value 컬럼에 업데이트')
        self._update_initvalue()

        logger.info("Done.")

    def _structure_data(self):
        # 실전투자에서 사용가능한 TR만 대상이다.
        data = []
        cursor = db.TRList.find({'real_active':True}, {'inputs':1, 'trcode':1})
        for d in list(cursor):
            trcode = d['trcode']
            inputs = d['inputs']
            gubun = d['markettype'] if 'markettype' in d else None
            for input in inputs:
                id = input['id']
                value_info = input['value']
                values = self._parse_inputValueStr(value_info)
                data.append({
                    'tr':trcode, 'id':id,
                    'value_info':value_info, 'values':values, 'markettype':gubun
                })
        return data

    def _parse_inputValueStr(self, value_info):
        values = []
        if value_info is None:
            pass
        else:
            p_value = "[A-Za-z\d]+"
            p_desc = "[0-9A-Z가-힣\(\)\s\+~]+"
            pairs = re.findall(f"({p_value})\s*:\s*({p_desc})", value_info)
            if len(pairs) > 0:
                for v in pairs:
                    values.append({'value':v[0], 'desc':v[1]})
            else:
                pairs = re.findall(f"({p_desc})\s*:\s*({p_value})", value_info)
                if len(pairs) > 0:
                    for v in pairs:
                        values.append({'value':v[1], 'desc':v[0]})
                else:
                    pass
        return values

    def _update_initvalue(self):
        # PartGubun('단계0: 초기값 컬럼을 일괄 제거')
        self.update_many({}, {'$unset':{'value':''}})

        # PartGubun('단계1: values 의 첫번째 값을 무조건 초기값으로 설정')
        cursor = self.find({'values':{'$ne':[]}}, {'values':1})
        for d in list(cursor):
            value = d['values'][0]
            update = {'$set':{'value':value['value']}}
            self.update_one({'_id':d['_id']}, update)

        # PartGubun('단계2: TRInput InitValue SetRules 에 따라 초기값을 설정')
        cursor = db.TRInputInitValueSetRules.find(None, {'_id':0}, sort=[('order',ASCENDING)])
        for rule in list(cursor):
            colName, colPat, initVal = rule['target'], rule['pat'], rule['value']

            # 초기값 설정할 대상 도큐먼트를 로딩
            # 단, 초기값이 이미 할당된 대상은 제외
            cursor = self.find({'value':None, colName:{'$regex':colPat}})
            data = list(cursor)
            if len(data) > 0:
                if isinstance(initVal, dict):
                    # TRInput컬렉션으로부터 타겟컬럼값으로부터 값을 추출해서 초기값 설정
                    # print(pd.DataFrame(data).drop(columns=['_id','markettype','values']))
                    for d in data:
                        m = re.search(initVal['pat'], d[colName])
                        v = m.group(1)
                        self.update_one({'_id':d['_id']}, {'$set':{'value':v}})
                else:
                    # 정해진 초기값이면 DB에 일괄 업데이트
                    filter = {'_id':{'$in':list(pd.DataFrame(data)._id)}}
                    update = {'$set':{'value':initVal}}
                    self.update_many(filter, update)
            else:
                logger.info('초기값 설정할 대상 도큐먼트는 없다')


class TRItem(KWModel):
    # TRModel 에게 동적스키마모델을 제공하기 위한 메타데이터.

    def __init__(self):
        super().__init__(self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        # PartGubun('Phase-1: 컬렉션 생성')
        # self.drop()
        cursor = db.TRList.find({'real_active':True, 'outputs':{'$ne':None}}, {'trcode':1, 'outputs':1})
        data = []
        for d in list(cursor):
            for item in d['outputs']:
                data.append({'item':item, 'tr':d['trcode']})

        df = pd.DataFrame(data)
        # print(df)
        for n, g in df.groupby('item'):
            # print(g)
            filter = {'item':n}
            doc = filter.copy()
            doc.update({'trs':list(g.tr)})
            self.update_one(filter, {'$set':doc}, True)

        # PartGubun('Phase-2: item의 dtype 결정 및 dtype컬럼 업데이트')
        assign_dtype('TRItem', 'item')

        logger.info("Done.")


class RealtimeFID(KWModel):
    # RealtimeModel 에게 동적 스키마모델을 제공하는 메타데이터.

    def __init__(self):
        super().__init__(self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        # PartGubun('단계1: 신규 컬렉션 생성')
        data = self._structure_data()
        self.drop()
        self.insert_many(data)

        # PartGubun('단계2: FID별 dtype 정의 및 업데이트')
        assign_dtype(self.collName, 'name')

        logger.info('Done.')

    def _transform_RTList_data(self):
        cursor = db.RTList.find(None, {'_id':0, 'realtype':1, 'fid_data':1})
        return pd.json_normalize(list(cursor), 'fid_data', ['realtype'])

    def _structure_data(self):
        df = self._transform_RTList_data()
        data = []
        for n, g in df.groupby(['fid','name']):
            data.append({'fid':n[0], 'name':n[1], 'realtypes':list(g.realtype)})
        return data
