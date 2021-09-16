# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime


import pandas as pd


from idebug import *
from kiwoomde import *


from kiwoomdsc.viewer import *



def count_coluniquevalues(datamodel):
    # 컬럼별 유일값의 개수.
    # datamodel: 컬렉션 데이타 모델

    # 에러조건 검사
    if not hasattr(datamodel, 'collName'):
        logger.critical('datamodel 은 컬렉션 데이타 모델이어야 한다')
        raise

    # 분석결과 생성
    cols = datamodel.schema.get_columns()
    data = []
    for c in cols:
        values = datamodel.distinct(c)
        data.append({'colName':c, 'cnt':len(values)})

    # 분석결과 리포트
    df = pd.DataFrame(data).sort_values('cnt', ascending=False).reset_index(drop=True)
    print_title(f'{datamodel.collName} 컬럼별 유일값 개수')
    print(df)
    return df


def colvalue_freq_dist(datamodel):
    # Collection의 각 컬럼별 값의 빈도수 분포를 데이터프레임으로 프린트한다.

    cols = datamodel.schema.get_columns()
    for c in cols:
        data = datamodel.load({c:{'$ne':None}}, projection={c:1})
        if len(data) > 0:
            df = pd.DataFrame(data).applymap(lambda x: int(x) if x in [True, False] else x)
            g = df.groupby(c).count()
            SectionGubun(c)
            print(g.sort_values('_id', ascending=False))
