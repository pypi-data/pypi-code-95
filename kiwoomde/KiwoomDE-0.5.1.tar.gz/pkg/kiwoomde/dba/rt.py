# -*- coding: utf-8 -*-
import re


import pandas as pd


from idebug import *
from kiwoomde.database import *


from kiwoomde.models import *


def compare_fid(n):
    PartGubun(n)
    if n == 0:
        A = db.ChejanFID.distinct('fid')
        print('A집합:', len(A), A)

        B = db.RealtimeFID.distinct('fid')
        print('B집합:', len(B), B)

        A_x_B = db.RealtimeFID.distinct('fid', {'fid':{'$in':A}})
        print('A 교집합 B:', len(A_x_B), A_x_B)

        A_cha_B = db.ChejanFID.distinct('fid', {'fid':{'$nin':B}})
        print('A 차집합 B:', len(A_cha_B), A_cha_B)

        B_cha_A = db.RealtimeFID.distinct('fid', {'fid':{'$nin':A}})
        print('B 차집합 A:', len(B_cha_A), B_cha_A)

    elif n == 1:
        SectionGubun('ChejanFID')
        cursor = db.ChejanFID.find(None, {'_id':0, 'fid':1, 'name':1})
        df = pd.DataFrame(list(cursor)).sort_values('fid').reset_index(drop=True)
        print(df)

        SectionGubun('ChejanFID 에 없지만, 저장된 FID 컬럼들')
        projection = {fid:0 for fid in list(df.fid)}
        projection.update({'_id':0, 'dt':0})
        cursor = db['_Test_Chejan'].find(None, projection).limit(10)
        df = pd.DataFrame(list(cursor))
        df.info()
        print(df)

        if len(df.columns) > 0:
            SectionGubun('해당 FID 정보를 RealtimeFID에서 가져옴')
            cursor = db.RealtimeFID.find({'fid':{'$in':list(df.columns)}}, {'_id':0, 'fid':1, 'name':1, 'dtype':1})
            df_ = pd.DataFrame(list(cursor)).sort_values('fid').reset_index(drop=True)
            print(df_)

            SectionGubun('여전히 FID 정보가 없는 FIDs 는 어떻게 처리할것인가?')
            projection.update({fid:0 for fid in list(df_.fid)})
            cursor = db['_Test_Chejan'].find(None, projection).limit(10)
            df = pd.DataFrame(list(cursor))
            df.info()
            print(df)
