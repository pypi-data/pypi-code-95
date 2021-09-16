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


from kiwoomde import config



def _parse_collection_list(names):
    # pp.pprint(sorted(names))
    pat = f'_*(Schema|Test)*_*([a-zA-Z0-9]+)_*([a-z\d]+)*$'
    data = []
    for name in names:
        m = re.search(pat, name)
        # print(m.groups(), name)
        li = list(m.groups())
        li.append(name)
        data.append(li)

    df = pd.DataFrame(data, columns=['collmode','modelName','param','collName'])
    df = df.fillna(value={'collmode':'Real'})
    return df.sort_values(['collmode','modelName','param']).reset_index(drop=True)


@funcIdentity
def CollectionList(modelName):
    # 모델명에 해당하는 컬렉션리스트를 반환
    pat = f'_*([Schema|Test]*)_*({modelName})_*([\d|a-z]+)*$'
    names = db.list_collection_names(filter={'name':{'$regex':pat}})
    df = _parse_collection_list(names)
    logger.info(f"{modelName}-> len:{len(df)}")
    return df


@funcIdentity
def AllCollectionList():
    names = db.list_collection_names(filter=None)
    df = _parse_collection_list(names)
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def SchemaCollectionList():
    df = AllCollectionList()
    df = df.query('collmode == "Schema"').reset_index(drop=True)
    names = list(df.collName)
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def RealCollectionList():
    df = AllCollectionList()
    df = df.query('collmode == "Real"').reset_index(drop=True)
    names = list(df.collName)
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def TestCollectionList():
    df = AllCollectionList()
    df = df.query('collmode == "Test"').reset_index(drop=True)
    names = list(df.collName)
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def RealtimeCollectionList():
    df = CollectionList('Realtime')
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def TRCollectionList():
    names = db.list_collection_names(filter={'name':{'$regex':'op[tw]\d+', '$options':'i'}})
    df = _parse_collection_list(names)
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def AssetCollectionList():
    filter = {'name':{'$regex':'opw0', '$options':'i'}}
    names = db.list_collection_names(filter=filter)
    df = _parse_collection_list(names)
    logger.info(f"len:{len(df)}")
    return df


@funcIdentity
def StaticSchemaModels(n=2):
    if n == 0:
        names = db.list_collection_names(filter={'name':{'$regex':'^[A-Z]'}})
        p = re.compile('^[opt|opw|config]', flags=re.I)
        names = [name for name in names if p.search(name) is not None]
    elif n == 1:
        names = ['TRList','TRInput','TRItem','RTList','RealtimeFID']
    elif n == 2:
        names = []
        with os.scandir(config.SchemaCSVPath) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    # print(entry.name, entry)
                    root, ext = os.path.splitext(entry.name)
                    names.append(root)

    return sorted(names)


@funcIdentity
def DevGuideModels():
    # 텍스트파일이므로 확장자명은 필요없다
    names = []
    with os.scandir(config.DevGuideTextPath) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                # print(entry.name, entry)
                root, ext = os.path.splitext(entry.name)
                names.append(root)

    return sorted(names)


@funcIdentity
def ManDataModels():
    # 파일타입이 CSV/JSON/등등 을 모두 커버해야하므로, 확장자명까지 함께 남긴다
    names = []
    with os.scandir(config.ManDataJSONPath) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                # print(entry.name, entry)
                root, ext = os.path.splitext(entry.name)
                names.append(root)

    return sorted(names)
