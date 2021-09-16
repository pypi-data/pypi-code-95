# -*- coding: utf-8 -*-

import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *
from kiwoomde import *



def create_DayTradingTarget(issueNames):
    c = BaseModel('Company')
    cursor = c.load({'name':{'$in':issueNames}}, {'_id':0, 'name':1, 'code':1})
    model = BaseModel('DayTradingTarget')
    model.drop(True)
    model.insert_data(list(cursor))
    logger.info('Done.')


def add(issueNames):
    c = BaseModel('Company')
    cursor = c.load({'name':{'$in':issueNames}}, {'_id':0, 'name':1, 'code':1})
    model = BaseModel('DayTradingTarget')
    for d in list(cursor):
        model.update_one(d, {'$set':d}, True)
    logger.info('Done.')
