import pandas as pd

def download_data():
    raw = pd.read_csv('http://hilpisch.com/pyalgo_eikon_eod_data.csv', index_col=0, parse_dates=True).dropna() 
    return raw.info()

def say_hello():
    return "Hello"