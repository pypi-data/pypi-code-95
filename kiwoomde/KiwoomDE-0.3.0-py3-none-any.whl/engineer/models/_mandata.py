# -*- coding: utf-8 -*-
import re


import pandas as pd


from idebug import *


from kiwoomde.conf import config
from kiwoomde.engineer.database import *
from kiwoomde.engineer.models.base import KWModel


def ManDataModel(modelName):
    if modelName == 'ScreenNumber':
        return ScreenNumber()
    elif modelName == 'TRInputInitValueSetRules':
        return TRInputInitValueSetRules()
    else:
        return BaseMDModel(modelName)


# 수작업으로 작성한 데이타를 생성하는 모델
class BaseMDModel(KWModel):

    def __init__(self, modelName):
        super().__init__(modelName)
        self._find_file()

    def _find_file(self):
        # 파일 찾기
        with os.scandir(config.datapath.ManDataJSONPath) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    root, ext = os.path.splitext(entry.name)
                    if root == self.modelName: break

        # 모델명에 해당하는 파일명이 없다면 에러발생
        if root == self.modelName:
            self._filetype = ext.replace('.','')
            self._fpath = config.clean_path(f'{config.datapath.ManDataJSONPath}/{entry.name}')
        else:
            logger.critical(f'해당 모델({self.modelName})에 대한 수동데이타 파일이 존재하지 않는다')
            raise

    def _read_data(self, dtype=True):
        dtype = self.schema.get_dtypeDict() if dtype else None
        if self._filetype == 'json':
            df = pd.read_json(self._fpath, orient='records', lines=True, dtype=dtype)
        elif self._filetype == 'csv':
            df = pd.read_csv(self._fpath, dtype=dtype)
        else:
            raise
        # 'None'문자열을 'NoneType'으로 변경
        df = df.applymap(lambda x: None if x == 'None' else x)
        return df.to_dict('records')

    @funcIdentity
    def create_collection(self):
        data = self._read_data(True)
        self.drop()
        self.insert_many(data)
        logger.info(f'Done. modelName: {self.modelName}')

    @funcIdentity
    def emit_collection(self, filetype='json', filter=None, **kw):
        # TypeError: Object of type ObjectId is not JSON serializable
        cursor = self.find(filter, **kw)
        df = pd.DataFrame(list(cursor))
        df = df.reindex(columns=self.schema.get_columns())
        # 파일 쓰기
        if filetype == 'json':
            df.to_json(self._fpath, force_ascii=False, orient='records', lines=True)

        logger.info(f'Done. modelName: {self.modelName}')


class TRInputInitValueSetRules(BaseMDModel):

    @funcIdentity
    def __init__(self):
        super().__init__(modelName=self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        data = self._read_data(False)
        self.drop()
        self.insert_many(data)
        logger.info(f'Done. modelName: {self.modelName}')


class ScreenNumber(KWModel):

    @funcIdentity
    def __init__(self):
        super().__init__(modelName=self.__class__.__name__)
        self.model = BaseMDModel(self.modelName)

    @funcIdentity
    def create_collection(self):
        # PartGubun('단계1: BY ManData 생성')
        self.model.create_collection()

        # PartGubun('단계2: BY TRList 생성')
        self.TRList = KWModel('TRList')

        def _by_TRList(filter, n):
            data = self.TRList.load(filter, {'trname':1, '_id':0}, sort=[('trname',ASCENDING)])
            df = pd.DataFrame(data)
            df.index = df.index + n
            df.index = df.index.astype('str')
            df = df.reset_index(drop=False).rename(columns={'index':'code', 'trname':'name'})
            self.insert_many(df.to_dict('records'))

        # TR-계열
        _by_TRList({'trcode':{'$regex':'^opt', '$options':'i'}}, 1000)
        # ACCT-계열
        _by_TRList({'trcode':{'$regex':'^opw', '$options':'i'}}, 2000)

        logger.info('Done.')

    @funcIdentity
    def emit_collection(self):
        self.model.emit_collection()
        logger.info('Done.')
