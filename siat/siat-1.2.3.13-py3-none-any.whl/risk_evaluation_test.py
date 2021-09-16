# -*- coding: utf-8 -*-


import os; os.chdir("S:/siat")
from siat.risk_evaluation import *

var,ratio=stock_VaR_normal_standard('BABA',1000,'2019-8-8',1,0.99)

tlcps=series_VaR_tlcp(['GOOG','MSFT','AAPL'],'2020-7-20',0.99,model='montecarlo')

from siat.var_model_validation import *
backtest_VaR(['AAPL'],[1000],'2020-7-20',1,model="normal_standard")


from siat.holding_risk import *

portfolio={'Market':('China','000001.SS'),'000661.SZ':2,'603392.SS':3,'300601.SZ':4}
vl,rl=get_VaR_portfolio(portfolio,'2020-7-20',1,0.99,model='all')
