# -*- coding: utf-8 -*-

import os; os.chdir("D:/siat")
from siat import *

df_all=oef_rank_china(info_type='单位净值',fund_type='全部类型',rank=15)

df_z=oef_rank_china(info_type='单位净值',fund_type='债券型')
df_g=oef_rank_china('单位净值','股票型',rank=5)
df_e=etf_rank_china(info_type='单位净值',fund_type='全部类型',rank=10)
