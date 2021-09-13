# from requests import get 
# from bs4 import BeautifulSoup
# from datetime import datetime
# import pickle
# from pathlib import Path
# import pandas as pd
# from GoogleNews import GoogleNews
# from base import Ticker

# # url = 'https://api.stocktwits.com/api/2/streams/symbol/AAPL.json'
# # for i in [message['body'] for message in get(url).json()['messages']]:
# #     print(i)
# #     print('*' * 50)

# class Stock:

#     def __init__(self, ticker, interval='1m', period='1d', target_prices=None, price_invested=None):
#         try:
#             self.ticker = ticker
#             # self.df = Ticker(ticker).get_data(interval, period)
#             # self.prev_close = Ticker(ticker).get_data('1d', '2d').iloc[0]['Close']
#             try:
#                 self._last_updated_price = self.df.iloc[-1]['Close']
#             except:
#                 pass
#             self.target_prices = target_prices
#             self.price_invested = price_invested
#         except:
#             raise Exception('Sorry, we could not find this stock!')
    
#     def __str__(self):
#         return self.ticker
    
# print(Stock('TSM'))        
        
import requests as _requests
import os 
import pandas as pd
from datetime import datetime

key = os.environ.get('ALPHA_VANTAGE_KEY')
# Need any proxies or anything?
def _get_json(url):
    request = _requests.get(url)
    json = request.json()
    return json

def get_data(ticker):
    # Quicker version? url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo'
    # Can access more data but will cost a lot of time
    data = _get_json(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={key}')['Time Series (Daily)']
    df = pd.DataFrame([[datetime.strptime(date, '%Y-%m-%d'), data[date]['4. close'], data[date]['2. high'], data[date]['3. low'], data[date]['1. open'], data[date]['6. volume']] for date in data.keys()], columns=['date', 'close', 'high', 'low', 'open', 'volume'])
    df = df.set_index('date')
            
    return df.iloc[:90]

def get_company_info(self):
    url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo'

print(get_data('AMD'))