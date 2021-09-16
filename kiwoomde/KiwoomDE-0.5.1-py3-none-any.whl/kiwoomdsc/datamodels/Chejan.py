# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime


import pandas as pd


from idebug import *
from kiwoomde import *



def f00():
    """
    _Schema_Chejan, RealtimeFID 둘의 FID 를 비교대조한다.
    """
    # A집합
    model = ChejanModel(collmode='test')
    fids = model.schema.distinct('fid')
    A = pd.Series(fids)

    # B집합
    fids = db.RealtimeFID.distinct('colName')
    B = pd.Series(fids)

    # A 차집합 B
    A_B = A[~A.isin(list(B))]

    # B 차집합 A
    B_A = B[~B.isin(list(A))]

    print(pd.DataFrame({'구분':['A집합','B집합','A-B','B-A'], 'cnt':[len(A),len(B),len(A_B),len(B_A)]}))
