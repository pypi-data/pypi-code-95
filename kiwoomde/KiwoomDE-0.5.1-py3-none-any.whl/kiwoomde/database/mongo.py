# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


from idebug import *


from kiwoomde.conf import config as cf

def generate_mongodb():
    try:
        client = MongoClient(host=cf.db.host, port=cf.db.port,
                            document_class=dict,
                            tz_aware=cf.db.tz_aware,
                            connect=True,
                            maxPoolSize=cf.db.maxPoolSize,
                            minPoolSize=cf.db.minPoolSize,
                            connectTimeoutMS=cf.db.connectTimeoutMS,
                            waitQueueMultiple=None, retryWrites=True)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
    except ConnectionFailure:
        logger.exception(f'ConnectionFailure: {ConnectionFailure}')
        raise
    else:
        db = client[cf.db.DatabaseName]
        bkdb = client[cf.db.BackupDatabaseName]
        return db, bkdb
