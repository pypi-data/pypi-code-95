# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:34:00 2021

@author: Tensor
"""

try:
    import numpy as np
except:
    raise ImportError("Numpy is not installed")
    
try:
    import pandas as pd
except:
    raise ImportError("Pandas is not installed")

try:
    import datetime as dt
except:
    raise ImportError("datetime is not installed")
    
try:
    import scipy as scipy 
except:
    raise ImportError("Scipy is not installed")

def data(ticker, start_date = None, end_date = None):
    import yfinance 
    import datetime
    if start_date:
        start_date = start_date
    else:
        start_date = "1800-01-01"
    if end_date:
        end_date = end_date
    else: 
        end_date = datetime.date.today()
    df = yfinance.download(ticker, start_date = start_date, end_date = end_date)
    df.dropna(inplace = True)
    df = df["Adj Close"]
    return df

class TimeSeriesTests(object):
    def __init__(self, data):
        self.data = data
    
    def plot(self):
        self.data.plot(figsize = (16, 6), style = "+-")
        
    def check(self, ignore = False):
        if isinstance(self.data, pd.DataFrame) == False:
            print("Passed data is not dataframe format. Coverting into dataframe")
            data = pd.DataFrame(self.data)
        
        if (self.data.isna().sum() > 0).any() == True:
            raise ValueError("data contains nan values")
        else:
            return self.data
        
        if ignore == True:
            data = data.fillna(method = "bfill")
            data = data.fillna(method = "pad")
            data.dropna(inplace = True)
            return data      
    
    def normaltest(self):
        from scipy.stats import jarque_bera
        data = self.check()
        columns = data.columns
        for i in range(data.shape[1]):
            stats, p_values = jarque_bera(data.iloc[:, i])
            print(f"Jarque_beta statistics for : {columns[i], stats}, p_values: {p_values}")
            print("Data is normally distributed") \
                if p_values < 0.05 else print("Data is not normallly distributed")
        
    def Adfuller(self, regression = None):
        from arch.unitroot import ADF
        data = self.check()
        self.regression = str(regression)
        self.columns = data.columns
        
        if regression is not None:
            for i in range(data.shape[1]):
                print("ADF test for", self.columns[i])
                print(ADF(data.iloc[:, i], trend = self.regression))
        else:
            for i in range(data.shape[1]):
                print("ADF test for", self.columns[i])
                print(ADF(data.iloc[:, i], trend = "n"))
            
    def KPSS(self, regression = None):    
        from statsmodels.tsa.stattools import kpss
        data = self.check()
        self.regression = str(regression)
        self.columns = data.columns
        if regression is not None:
            for i in range(data.shape[1]):
                t_stat, p_value, _, critical_values = \
                kpss(data.iloc[:, i].values, nlags='auto', regression = "ct")
                print(f'ADF Statistic: {t_stat:.2f} for', data.columns[i])
                
                for key, value in critical_values.items():
                    print('Critial Values:')
                    print(f'   {key}, {value:.2f}')
                    print(f'\np-value: {p_value:.2f}')
                    print("Stationary") if p_value > 0.05 else print("Non-Stationary")
        
        else:
            for i in range(data.shape[1]):
                t_stat, p_value, _, critical_values = \
                kpss(data.iloc[:, i].values, nlags='auto', regression = "c")
                print(f'ADF Statistic: {t_stat:.2f} for', data.columns[i])
                
                for key, value in critical_values.items():
                    print('Critial Values:')
                    print(f'   {key}, {value:.2f}')
                    print(f'\np-value: {p_value:.2f}')
                    print("Stationary") if p_value > 0.05 else print("Non-Stationary")
          
    def Cointegration(self, regression = None):
        from arch.unitroot import engle_granger
        data = self.check()
        self.regression = str(regression)
        self.columns = data.columns
        if regression is not None:
            for i in range(data.shape[1] - 1):
                print("Conintegration Test for", data.columns[0], "And", data.columns[i + 1], "\n")
                print(engle_granger(data.iloc[:, 0], data.iloc[:, i + 1], trend = regression))
        else:
            for i in range(data.shape[1] - 1):
                print("Conintegration Test for", data.columns[0], "And", data.columns[i + 1], "\n")
                print(engle_granger(data.iloc[:, 0], data.iloc[:, i + 1], trend = "n"))

    def Seasonal(self, model, period):
        from statsmodels.tsa.seasonal import seasonal_decompose
        data = self.check()
        index = data.index
        self.model = str(model)
        self.period = int(period)
        if (data.shape[1] >= 1):
            print("Only First Column will be passed")
        sd = seasonal_decompose(data.iloc[:, 0], model = self.model, period = self.period)
        sd.plot()
        
        residuals = sd.resid
        seasonal = sd.seasonal
        trend = sd.trend
        dataframe = pd.DataFrame(pd.concat([residuals, seasonal, trend], axis = 1), \
                                 index = index, columns = ["residuals", "seasonal", "trend"])
        return dataframe