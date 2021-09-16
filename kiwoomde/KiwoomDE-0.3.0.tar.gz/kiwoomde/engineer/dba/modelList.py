# -*- coding: utf-8 -*-
from datetime import datetime
import math
import os, sys
import re
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *
from kiwoomde.engineer.database import *


from kiwoomde.engineer.dba._collectionList import *


def modify_database(n):
    if n == 1:
        names = db.list_collection_names(filter={'name':{'$regex':'_Schema_op', '$options':'i'}})
        for name in names:
            db[name].drop()


def modify_collection(n):
    if n == 1:
        filter = {'colName':'input'}
        update = {'$set':{'colName':'id'}}
        SchemaModel('TRInput').update_one(filter, update)
    elif n == 2:
        update = {'$set':{'updated_dt':datetime(2021,5,4).astimezone()}}
        db.Company.update_many({}, update)



def postparse_data(model):
    cursor = model.find()
    data = model.schema.parse_data(list(cursor))
    for d in data:
        try:
            filter = {'_id':d['_id']}
            update = {'$set':d}
            model.update_one(filter, update)
        except Exception as e:
            logger.exception(e)
            pp.pprint(d)
    print('Done')


def drop_duplicates(modelName):
    model = DataModel(modelName)
    keycols = model.schema.distinct('colName', {'role':'key'})
    projection = {k:1 for k in keycols}
    data = model.load(None, projection)
    df = pd.DataFrame(data)
    print(len(df))
    # return df
    TF = df.duplicated(subset=keycols, keep=False)
    print(len(df[TF]))
    # return df[TF]
    TF = df.duplicated(subset=keycols, keep='last')
    print(len(df[TF]))
    # return df[TF]

    if len(df[TF]) > 0:
        ids = list(df[TF]._id)
        model.delete_many({'_id':{'$in':ids}})





def view_TR_rawdata(trcode):
    filter = {'input':{'$regex':trcode, '$options':'i'}}
    projection = {'input':1, 'output':1}
    cursor = db.TRList.find(filter, projection)
    for d in list(cursor):
        for k,v in d.items():
            if k == 'input':
                for line in v.splitlines():
                    print(line)
            else:
                print(v)
