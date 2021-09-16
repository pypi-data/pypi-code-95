# -*- coding: utf-8 -*-

import os; os.chdir("S:\siat")
from siat.assets_liquidity import *

portfolio={'Market':('China','000001.SS'),'600011.SS':1}
start='2020-1-1'
end='2020-6-30'
liquidity_type='roll_spread'
l=liquidity_rolling(portfolio,start,end,liquidity_type,30)

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


