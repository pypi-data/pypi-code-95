# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat.fama_french import *

ff3_betas=reg_ff3_betas('AAPL','2018-1-1','2019-4-30','US')
ff3_betas=reg_ff3_betas('BILI','2018-1-1','2019-4-30','US')

ff3_betas=reg_ff3_betas('BMW.DE','2018-1-1','2019-4-30','Europe')
ff3_betas=reg_ff3_betas('AEM','2018-3-1','2019-8-31','US')

reg_ffc4_betas('JD','2018-1-1','2019-4-30','US')
reg_ffc4_betas('BABA','2018-1-1','2019-4-30','US')
reg_ffc4_betas('MSFT','2018-1-1','2019-4-30','US')
reg_ffc4_betas('TAL','2018-1-1','2019-4-30','US')

get_ff5_factors('2019-5-20','2019-5-31','US','daily')
get_ff5_factors('2018-1-1','2019-4-30','US','monthly')

reg_ff5_betas('PTR','2018-1-1','2019-4-30','US')
reg_ff5_betas('QCOM','2018-1-1','2019-4-30','US')
