# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *


from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.engineer.database import *
from kiwoomde.utils.viewer import pretty_title


class BaseModel(BaseClass):
    # 스키마 기반 베이스모델

    def __init__(self, modelName, collmode='real'):
        self._modeltype = self.__class__.__name__
        self.modelName = modelName
        self.collName = modelName
        self.apply_collmode(collmode)
        self.schema = SchemaModel(modelName)

    def apply_collmode(self, mode):
        self.collmode = mode
        if mode == 'real': pass
        elif mode == 'test': self.collName = f"_Test_{self.collName}"
        elif mode == 'sample': self.collName = f"_Sample_{self.collName}"
        else: raise

    def insert_one(self, doc):
        db[self.collName].insert_one(doc)

    def insert_many(self, data):
        try:
            db[self.collName].insert_many(data)
        except Exception as e:
            logger.exception(e)

    def distinct(self, col, filter=None):
        return db[self.collName].distinct(col, filter=filter)

    def find(self, filter=None, projection=None, **kw):
        return db[self.collName].find(filter, projection, **kw)

    def count_documents(self, filter={}):
        n = db[self.collName].count_documents(filter)
        logger.info(f"count_documents: {n}")
        return n

    def n_returned(self, cursor):
        n = cursor.explain()['executionStats']['nReturned']
        logger.info(f"nReturned: {n}")
        return n

    def update_one(self, filter, update, upsert=False):
        db[self.collName].update_one(filter, update, upsert)

    def update_many(self, filter, update, upsert=False):
        db[self.collName].update_many(filter, update, upsert)

    def delete_one(self, filter):
        db[self.collName].delete_one(filter)

    def delete_many(self, filter):
        db[self.collName].delete_many(filter)

    def drop(self):
        db[self.collName].drop()


class DataModel(BaseModel):

    def __init__(self, modelName, collmode='real'):
        super().__init__(modelName, collmode)

    def parse_data(self, data):
        return self.schema.parse_data(data)

    def insert_data(self, data):
        data = self.schema.parse_data(data)
        self.insert_many(data)

    def upsert_data(self, data):
        keycols = list(self.schema.get_columns({'role':'key'}))
        for d in data:
            if len(keycols) > 0:
                filter = {k:v for k,v in d.items() if k in keycols}
            else:
                filter = d.copy()
            self.update_one(filter, {'$set':d}, True)

    """여기서 필요한 메소드는 아닌듯"""
    def _schema_projection(self, proj=None):
        projection = {c:1 for c in list(self.schema.mdb.column)}
        if isinstance(proj, dict):
            projection.update(proj)
        return projection

    def load(self, filter=None, projection=None, **kw):
        cursor = self.find(filter, projection, **kw)
        return self.schema.astimezone(list(cursor))

    def view(self, filter=None, projection=None, **kw):
        data = self.load(filter, projection, **kw)
        df = pd.DataFrame(data)
        pretty_title(self.collName)
        df.info()
        return df

    def dedup(self, subset=None):
        subset = self.schema.get_columns({'role':'key'}) if subset is None else subset
        data = self.load()
        df = pd.DataFrame(data)
        cols = list(df.columns)
        subset = [e for e in subset if e in cols]
        TF = df.duplicated(subset=subset, keep='first')
        dup_ids = list(df[TF]._id)
        self.delete_many({'_id':{'$in':dup_ids}})
        logger.info('Done.')

    def select(self, filter=None, projection=None, **kw):
        try:
            data = self.load(filter, projection, **kw)
            self.selected = BaseDataClass(dataname='Selected', **data[0])
        except Exception as e:
            logger.info(e)
        return self

    def backup(self):
        cursor = self.find()
        bkdb[self.collName].drop()
        bkdb[self.collName].insert_many(list(cursor))
        logger.info(f"{self.collName} 백업 완료.")

    def rollback(self):
        cursor = bkdb[self.collName].find()
        self.drop()
        self.insert_many(list(cursor))
        logger.info(f"{self.collName} 원복 완료.")


class SelectorModel(BaseModel):

    def __init__(self, modelName, collmode='real'):
        super().__init__(modelName, collmode)

    def select(self, **filter):
        try:
            cursor = self.find(filter).limit(1)
            self.attr(list(cursor)[0])
        except Exception as e:
            logger.exception(f'{e} | filter: {filter}')
        return self

    @funcIdentity
    def repr_selected(self):
        cols = list(self.schema.mdb.column) + ['_id']
        pretty_title(f'Selected doc in {self.modelName}')
        pp.pprint({k:v for k,v in self.__dict__.items() if k in cols})

    def parse_selected(self):
        cols = list(self.schema.mdb.column)
        for k,v in self.__dict__.items():
            if k in cols:
                v = self.schema.parse_value(k,v)
                setattr(self, k, v)
        return self

    def upsert(self):
        cols = list(self.schema.mdb.column)
        datum = {k:v for k,v in self.__dict__.items() if k in cols}
        filter = {'_id':self._id}
        update = {'$set':datum}
        self.update_one(filter, update, True)
