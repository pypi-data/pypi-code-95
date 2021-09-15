import ccxt
from datetime import datetime
import plotly.graph_objects as go
from tokens import *

# USDC for usd in the pairs sections

#how could we send this link through discord or something

def chart(pair,timeframe):
    binance = ccxt.binance()
    trading_pair = pair

    candles = binance.fetch_ohlcv(trading_pair, timeframe)


    dates = []
    open_data = []
    high_data = []
    low_data = []
    close_data = []

    for candle in candles:
        dates.append(datetime.fromtimestamp(candle[0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f'))
        open_data.append(candle[1])
        high_data.append(candle[2])
        low_data.append(candle[3])
        close_data.append(candle[4])

    fig = go.Figure(data=[go.Candlestick(x=dates,
                        open=open_data, high=high_data,
                        low=low_data, close=close_data)])
    fig.show()
