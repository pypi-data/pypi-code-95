# -*- coding: utf-8 -*-

import os; os.chdir("S:\siat")
from siat import *
#==============================================================================
p=security_price("BB","2015-1-10","2015-1-24",power=0)
p=security_price("LLY","2000-1-1","2003-12-31",power=10)
#==============================================================================
dfyf=get_prices_yf('AAPL','2020-1-1','2021-4-8',threads=False)

dfak=get_prices_ak('600519.SS','2020-1-1','2021-4-8')
dfak=get_prices_ak(['600519.SS','000002.SZ'],'2020-1-1','2021-4-8')


df=get_prices('AAPL','2020-1-1','2021-4-8',adj=False)
dfa=get_prices('AAPL','2020-1-1','2021-4-8',adj=True)
dfa_dif=dfa[dfa['Close']!=dfa['Adj Close']]

dfhy=get_prices('300401.SZ','2018-5-1','2018-5-30',adj=True)
dfyfhy=get_prices_yf('300401.SZ','2018-5-1','2018-5-30',threads=False)



ticker=['600011.SS']
start='2020-1-1'
end='2020-6-30'
pak=get_prices_ak(ticker,start,end)

pyf=get_price_yf(ticker,start,end)

pyh=p=get_prices_yahoo(ticker,start,end)

p=get_prices(ticker,start,end)

tickerlist=['600011.SS']
sharelist=[1]
p1=get_price_portfolio(tickerlist,sharelist,start,end)


if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'

p2=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)


if __name__=='__main__':
    tickerlist=['INTC','MSFT','uvwxyz']
    sharelist=[0.6,0.3,0.1]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp1=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)
    dfp2=get_prices_yf(tickerlist,fromdate,todate)
    dfp3=get_prices(tickerlist,fromdate,todate)
    
    prices=get_prices_yf(tickerlist,fromdate,todate)
    

if __name__=='__main__':
    df1=get_prices('INTC','2020-10-1','2021-1-31')
    df2=get_prices(['INTC'],'2020-10-1','2021-1-31')
    df3=get_prices(['XYZ'],'2020-10-1','2021-1-31')
    df4=get_prices(['INTC','MSFT'],'2020-10-1','2021-1-31')
    df5=get_prices(['INTC','UVW'],'2020-10-1','2021-1-31')
    df6=get_prices(['0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df7=get_prices(['INTL','MSFT','0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df8=get_prices(['000858.SZ','600519.SS'],'2020-10-1','2021-1-31')


#==============================================================================
import akshare as ak

#上证综指
sh_df = ak.stock_zh_index_daily(symbol="sh000001")

#上证50指数
sh50_df = ak.stock_zh_index_daily(symbol="sh000016")

#上证100指数
sh100_df = ak.stock_zh_index_daily(symbol="sh000132")

#上证150指数
sh150_df = ak.stock_zh_index_daily(symbol="sh000133")

#上证180指数
sh180_df = ak.stock_zh_index_daily(symbol="sh000010")

#科创50指数
kc50_df = ak.stock_zh_index_daily(symbol="sh000688")

#沪深300指数
hs300_df = ak.stock_zh_index_daily(symbol="sh000300")

#大盘，中证100指数
zz100_df = ak.stock_zh_index_daily(symbol="sh000903")

#中盘，中证200指数
zz200_df = ak.stock_zh_index_daily(symbol="sh000904")

#小盘，中证500指数
zz500_df = ak.stock_zh_index_daily(symbol="sh000906")

#深证成指
sz_df = ak.stock_zh_index_daily(symbol="sz399001")

#交易所概况
sse_summary_df = ak.stock_sse_summary()
szse_summary_df = ak.stock_szse_summary()

stock_zh_index_daily_tx_df = ak.stock_zh_index_daily_tx(symbol="sh000001")

#==============================================================================
import os; os.chdir("S:/siat")
from siat.security_prices import *

df1=get_prices(['600519.SS','000858.SZ'],'2020-10-1','2021-1-31')
df2=get_prices(['0700.HK','000858.SZ'],'2020-10-1','2021-1-31')
df3=get_prices(['AAPL','MSFT'],'2020-10-1','2021-1-31')
df4=get_prices('399001.SZ','2020-10-1','2021-1-31')
df5=get_prices('000016.SS','2020-10-1','2021-1-31')

dfp1=get_prices_portfolio(['600519.SS','000858.SZ'],[1,2],'2020-10-1','2021-1-31')
dfp2=get_prices_portfolio(['0700.HK','000858.SZ'],[1,2],'2020-10-1','2021-1-31')
dfp3=get_prices_portfolio(['AAPL','MSFT'],[1,2],'2020-10-1','2021-1-31')


df600519=get_price_ak('600519.SS','2020-12-1','2021-2-5',adjust='none')
df600519hfq=get_price_ak('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
df399001=get_price_ak('399001.SZ','2020-12-1','2021-2-5')
df000688=get_price_ak('000688.SS','2020-12-1','2021-2-5')
dfaapl=get_price_ak('AAPL','2020-12-1','2021-2-5')

df3=get_prices_yf(['AAPL','MSFT'],'2020-12-1','2021-1-31')



if __name__=='__main__':
    df1=get_prices('INTC','2020-10-1','2021-1-31')
    df2=get_prices(['INTC'],'2020-10-1','2021-1-31')
    df3=get_prices('XYZ','2020-10-1','2021-1-31')
    df3b=get_prices(['XYZ'],'2020-10-1','2021-1-31')
    df4=get_prices(['INTC','MSFT'],'2020-10-1','2021-1-31')
    df5=get_prices(['INTC','UVW123'],'2020-10-1','2021-1-31')
    df6=get_prices(['0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df7=get_prices(['INTL','MSFT','0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    
if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)    
    
    
    
    
    