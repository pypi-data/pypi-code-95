# -*- coding: utf-8 -*-


import os; os.chdir("D:/siateng")
from siate import *

import os; os.chdir("D:/siat")
from siat import *

#==============================================================================
info=get_stock_profile("MUFG","fin_rates")

wuliu=["002352.SZ","002468.SZ","2057.HK","600233.SS","002120.SZ","603056.SS","601598.SS","603967.SS","603128.SS"]
peg=compare_snapshot(wuliu,"PEG")

tickers=["601398.SS","601988.SS","601988.SS",'601288.SS','601328.SS','601658.SS','600036.SS','000001.SZ']
isgr=compare_igr_sgr(tickers,axisamp=3)
#==============================================================================
tickers=["BABA","JD","VIPS",'PDD','AMZN','WMT','EBAY','SHOP','MELI']
isgr=compare_igr_sgr(tickers)

#==============================================================================
tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
pm=compare_snapshot(tickers,'Profit Margin')
roa=compare_snapshot(tickers,'ROA')
roe=compare_snapshot(tickers,'ROE')
pe=compare_snapshot(tickers,'Trailing PE',axisamp=1.8)
#==============================================================================
tickers=["601808.SS","600583.SS","600968.SS",'600871.SS','600339.SS','601857.SS','600028.SS','0883.HK']
isgr=compare_igr_sgr(tickers)

ticker='0883.HK'
igr,sgr=calc_igr_sgr(ticker)
#==============================================================================
tat=compare_history(['AMZN','JD'],'Total Asset Turnover')
fat=compare_history(['AMZN','JD'],'Fixed Asset Turnover')
cfps_eps=compare_history(['BABA'],['Cashflow per Share','BasicEPS'])

cr=compare_history(['BABA','JD'],'Cashflow per Share')
cr=compare_history(['BABA','PDD'],'Cashflow per Share')
cr=compare_history(['BABA','VIPS'],'Cashflow per Share')

tickers=['600519.SS','000858.SZ','600779.SS','000596.SZ','603589.SS']
df=compare_dupont(tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10)


#==============================================================================
cr=compare_history(['AAPL','MSFT'],'Current Ratio')
cr=compare_history(['601808.SS','600871.SS'],'Current Ratio')
cr=compare_history(['601808.SS','0883.HK'],'Current Ratio')

cr=compare_history(['601808.SS'],['Current Ratio','Quick Ratio'])


#==============================================================================
cosl=compare_history('601808.SS',['Current Ratio','Quick Ratio'])
cosl=compare_history('601808.SS',['Debt to Asset','Debt to Equity'])
cosl=compare_history('601808.SS',['Debt to Asset','Debt to Equity'],twinx=True)
tie=compare_history(['601808.SS'],'Times Interest Earned')
itr=compare_history(['601808.SS','600871.SS'],'Inventory Turnover')
rtr=compare_history(['601808.SS','600871.SS'],'Receivable Turnover')

rtr=compare_history(['601808.SS','600871.SS'],'Total Asset Turnover')
fat=compare_history(['601808.SS','600871.SS'],'Fixed Asset Turnover')
cr=compare_history(['601808.SS','600871.SS'],'Current Ratio')
qr=compare_history(['601808.SS','600871.SS'],'Quick Ratio')
d2a=compare_history(['601808.SS','600871.SS'],'Debt to Asset')

cfps=compare_history(['601808.SS','600871.SS'],'Cashflow per Share')

dtoe=compare_snapshot(tickers,'Dbt to Asset')

tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
dbi=compare_dupont(tickers,fsdate='latest',scale1 = 100,scale2 = 50)

tickers=['601808.SS',"600339.SS",'600583.SS','SLB','HAL']
dbi=compare_dupont(tickers,fsdate='latest',scale1 = 100,scale2 = 50)

igr=compare_snapshot(tickers,'IGR')
#==============================================================================
tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
atr=compare_tax(tickers,graph=True)
dbi=compare_dupont(tickers,fsdate='latest',scale1 = 100,scale2 = 10)
ev2r=compare_snapshot(tickers,'EV to Revenue')
ev2ebitda=compare_snapshot(tickers,'EV to EBITDA')
price=compare_snapshot(tickers,'Current Price')

tickers2=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','BP','RDSA.AS']
fpe=compare_snapshot(tickers2,'Forward PE')
pb=compare_snapshot(tickers,'Price to Book')
roa=compare_snapshot(tickers,'ROA')
roe=compare_snapshot(tickers,'ROE')

pm=compare_snapshot(tickers,'ROE')

tickerlist=['IBM','DELL','WMT'] 
df=compare_dupont(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10)    

tickerlist=['DELL','WMT'] 
df=compare_dupont(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10) 
#==============================================================================
tickers_cn=['600398.SS','300005.SZ','002563.SZ','002193.SZ','002269.SZ']
tickers_hk=['2331.HK','2020.HK','1368.HK','3998.HK','2313.HK']
tickers=tickers_cn+tickers_hk
gmdf=compare_dupont(tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10) 

#==============================================================================
tickers=['AMZN','EBAY','SHOP','MELI','BABA','JD','VIPS','PDD']
dtoe=compare_snapshot(tickers,'Debt to Asset')
#==============================================================================

leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
tpe=compare_snapshot(leadings,'Trailing PE')

mainleadings=['JNJ','PFE','MRK','VRTX','NVS','SNY']
tests=['NBIX','REGN','PRGO']
tpe=compare_snapshot(tests + mainleadings,'Trailing PE')

#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
fpe=compare_snapshot(leadings,'Forward PE')

mainleadings=['JNJ','PFE','VRTX','NVS','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
fpe=compare_snapshot(tests + mainleadings,'Forward PE')
#==============================================================================
cp=compare_snapshot(tests+leadings,'Current Price')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
ptob=compare_snapshot(leadings,'Price to Book')

mainleadings=['JNJ','PFE','MRK','VRTX','NVS','AMGN']
tests=['NBIX','REGN','PRGO']
ptob=compare_snapshot(tests+mainleadings,'Price to Book')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
evtoebitda=compare_snapshot(leadings,'EV to EBITDA')

mainleadings=['JNJ','PFE','VRTX','NVS','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
evtoebitda=compare_snapshot(tests + mainleadings,'EV to EBITDA')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
evtoebitda=compare_snapshot(leadings,'PEG')
#==============================================================================
mainleadings=['MRK','LLY','VRTX','NVS','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
peg=compare_snapshot(tests + mainleadings,'PEG')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
ptos=compare_snapshot(leadings,'TTM Price to Sales')
#==============================================================================
mainleadings=['JNJ','PFE','MRK','LLY','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
ptos=compare_snapshot(tests + mainleadings,'TTM Price to Sales')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
evtorev=compare_snapshot(leadings,'EV to Revenue')
#==============================================================================
mainleadings=['JNJ','PFE','MRK','VRTX','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
evtorev=compare_snapshot(tests + mainleadings,'EV to Revenue')




#==============================================================================
cfps_eps=compare_history('BABA',['Cashflow per Share','BasicEPS'])
cfps_eps=compare_history('JD',['Cashflow per Share','BasicEPS'])
cfps_eps=compare_history('PDD',['Cashflow per Share','BasicEPS'])
cfps_eps=compare_history('VIPS',['Cashflow per Share','BasicEPS'])

cfps_eps=compare_history('WMT',['Cashflow per Share','BasicEPS'])

cfps_eps=compare_history('QCOM',['Cashflow per Share','BasicEPS'])

cr=compare_history(['BABA','JD'],'Cashflow per Share')
cr=compare_history(['BABA','PDD'],'Cashflow per Share')
cr=compare_history(['BABA','VIPS'],'Cashflow per Share')

tickers=['AMZN','EBAY','SHOP','MELI']
cfps=compare_snapshot(tickers,'Cashflow per Share')
cr=compare_history(['AMZN'],['Cashflow per Share','BasicEPS'])
cr=compare_history(['EBAY'],['Cashflow per Share','BasicEPS'])


#==============================================================================
tickers=['AMZN','EBAY','SHOP','MELI','BABA','JD','VIPS','PDD']
roa=compare_snapshot(tickers,'ROA')

tat=compare_history(['AMZN','JD'],'Total Asset Turnover')
fat=compare_history(['AMZN','JD'],'Fixed Asset Turnover')
pper=compare_history(['AMZN','JD'],'PPE Residual')

cr=compare_snapshot(tickers,'Current Ratio')
qr=compare_snapshot(tickers,'Quick Ratio')
dtoe=compare_snapshot(tickers,'Debt to Equity')

pm=compare_snapshot(tickers,'Profit Margin')
gm=compare_snapshot(tickers,'Gross Margin')

gm=compare_snapshot(tickers,'EBITDA Margin')
gm=compare_snapshot(tickers,'Operating Margin')

roe=compare_snapshot(tickers,'ROE')
teps=compare_snapshot(tickers,'Trailing EPS')
rg=compare_snapshot(tickers,'Revenue Growth')

rg=compare_snapshot(tickers,'Earnings Growth')
rg=compare_snapshot(tickers,'Earnings Quarterly Growth')

#==============================================================================
tickers=['AMZN','EBAY','BABA','JD','VIPS']
roa=compare_snapshot(tickers,'ROA')
roe=compare_snapshot(tickers,'ROE')
beta=compare_snapshot(tickers,'beta')

tickers=['AMZN','EBAY','SHOP','BABA','JD','PDD','VIPS']
cr=compare_snapshot(tickers,'Current Ratio')
dtoe=compare_snapshot(tickers,'Debt to Equity')
teps=compare_snapshot(tickers,'Trailing EPS')
roe=compare_snapshot(tickers,'ROE')
hpinst=compare_snapshot(['AAPL','MSFT','BRKB'],'Held Percent Institutions')

#==============================================================================
rates=get_stock_profile('AAPL',info_type='fin_rates')

tickers=['AAPL','MSFT','WMT','FB','QCOM']
cr=compare_snapshot(tickers,'Current Ratio')
beta=compare_snapshot(tickers,'beta')
dtoe=compare_snapshot(tickers,'Debt to Equity')
dtoe=compare_snapshot(tickers,'?')
teps=compare_snapshot(tickers,'Trailing EPS')
tpe=compare_snapshot(tickers,'Trailing PE')

tickers1=['AMZN','EBAY','GRPN','BABA','JD','PDD','VIPS']
gm=compare_snapshot(tickers1,'Gross Margin')
pm=compare_snapshot(tickers1,'Profit Margin')

df1,df2=compare_history('AAPL','Current Ratio')
df1,df2=compare_history('AAPL',['Current Ratio','Quick Ratio'])
df1,df2=compare_history('AAPL',['BasicEPS','DilutedEPS'])
df1,df2=compare_history('AAPL',['Current Ratio','BasicEPS'],twinx=True)
df1,df2=compare_history('AAPL',['BasicPE','BasicEPS'])
df1,df2=compare_history('AAPL',['BasicPE','BasicEPS'],twinx=True)

df1,df2=compare_history(['AAPL','MSFT'],['BasicPE','BasicEPS'])
df1,df2=compare_history(['AAPL','MSFT'],['BasicPE','BasicEPS'],twinx=True)
df1,df2=compare_history(['AAPL','MSFT'],'BasicEPS',twinx=True)

cr=compare_history(['INTL','QCOM'],'Current Ratio',twinx=True)

cr=compare_history(['600519.SS','000002.SZ'],'Current Ratio',twinx=True)
#==============================================================================

Chinabanks = ["1398.HK","0939.HK","3988.HK","1288.HK"]
USbanks=["BAC", "TD","PNC"]
Japanbanks = ["8306.T","7182.T","8411.T"]

esg=compare_snapshot(Chinabanks+USbanks+Japanbanks,'Total ESG')
ep=compare_snapshot(Chinabanks+USbanks+Japanbanks,'Environment Score')
csr=compare_snapshot(Chinabanks+USbanks+Japanbanks,'Social Score')
emp=compare_snapshot(Chinabanks+USbanks+Japanbanks,'Employees')
gov=compare_snapshot(Chinabanks+USbanks+Japanbanks,'Governance Score')
roe=compare_snapshot(Chinabanks+USbanks+Japanbanks,'ROE')


cnnr=['2330.TW','2317.TW','2474.TW','3008.TW','2454.TW']
usnr=['SLB','COP','HAL','OXY','FCX']
otns=['5713.T','1605.T','5020.T']

esg=compare_snapshot(cnnr+usnr+otns,'Total ESG')
ep=compare_snapshot(cnnr+usnr+otns,'Environment Score')
csr=compare_snapshot(cnnr+usnr+otns,'Social Score')
gov=compare_snapshot(cnnr+usnr+otns,'Governance Score')


ep=compare_snapshot(['9988.HK','9618.HK','0700.HK'],'Environment Score')

#==============================================================================

market={'Market':('China','^HSI')}
stocks={'0700.HK':3,'9618.HK':2,'9988.HK':1}
portfolio=dict(market,**stocks)

_,_,stocklist,_=decompose_portfolio(portfolio)
collist=['symbol','totalEsg','environmentScore','socialScore','governanceScore']
sust=pd.DataFrame(columns=collist)
    for t in stocklist:
        try:
            info=stock_info(t).T
        except:
            print("#Error(): esg info not available for",t)
            continue
        if (info is None) or (len(info)==0):
            print("#Error(): failed to get esg info for",t)
            continue
        sub=info[collist]
        sust=pd.concat([sust,sub])
        












