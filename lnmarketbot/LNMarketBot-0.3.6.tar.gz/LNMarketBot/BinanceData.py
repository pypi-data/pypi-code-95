import aiohttp
import asyncio
import requests
from .Data import Data


class BinanceData(Data):

    def __init__(self, window=1000, interval='1m', **params):
        self.klineurl = '/api/v3/klines'
        self.baseurl = 'https://api2.binance.com'
        self.window = window
        self.interest = interval

        params = {
            'symbol': 'BTCUSD',
            'interval': interval,
            }
        data = requests.get(self.baseurl+self.klineurl, params=params)
        self.since = data[-2][0]
        self.ohlc = self.convertData(data)
