# -*- coding: utf-8 -*-


import os; os.chdir("S:/siat")
from siat.markowitz import *

Market={'Market':('US','^GSPC')}
Stocks={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09,'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
portfolio=dict(Market,**Stocks)

pf_info=portfolio_cumret(portfolio,'2019-12-31')
portfolio_covar(pf_info)
portfolio_corr(pf_info)
portfolio_expectation(pf_info)

es_info=portfolio_es(pf_info,simulation=50000)

df=portfolio_MSR_GMV(es_info)

stocks=['IBM','WMT','AAPL','C','MSFT']
ef=portfolio_ef(stocks,'2019-1-1','2020-8-1')





_,_,tickerlist,sharelist=decompose_portfolio(portfolio)

today='2020-12-31'
pastyears=1

pf_info=portfolio_cumret(portfolio,'2020-12-31')

portfolio_covar(pf_info)

portfolio_corr(pf_info)


















#定义投资组合
Market={'Market':('US','^GSPC')}
Stocks={'BABA':.4,'JD':.3,'PDD':.2,'VIPS':.1}
portfolio=dict(Market,**Stocks)

#搜寻该投资组合中所有成分股的价格信息，默认观察期为一年，pastyears=1
pf_info=portfolio_cumret(portfolio,'2020-11-30',pastyears=1)

#生成了投资组合的可行集
es_info=portfolio_es(pf_info,simulation=50000)
es_info10=portfolio_es(pf_info,simulation=100000)

#寻找投资组合的MSR优化策略点和GMV优化策略点
psr=portfolio_MSR_GMV(es_info)
