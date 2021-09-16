# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *
from kiwoomde import *


from kiwoomdsc import stat



def view_TRList_detail(**filter):
    model = SelectorModel('TRList').repr()
    af = AutoFilter(model.modelName).search(filter).repr()
    data = model.load(af.filter)

    for k,v in data[0].items():
        if k == 'input':
            print(k, ':')
            for line in v.splitlines():
                print(line)
        else:
            print(k, ':', v)



def unique_values_each_column():
    model = TRModel('opt10080', collmode='test', name='하이브').repr()
    data = model.load({}, {'_id':0, 'dt':0})
    # return pd.DataFrame(data)
    cols = model.schema.get_columns({'dtype':{'$ne':'boolean'}})
    data = []
    for c in cols:
        values = model.distinct(c)
        data.append({'colName':c, 'cnt':len(values)})
    return pd.DataFrame(data).sort_values('cnt', ascending=False).reset_index(drop=True)
