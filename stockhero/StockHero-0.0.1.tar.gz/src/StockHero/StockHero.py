# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 15:26:33 2021

@author: RobWen
"""
import pandas as pd
import requests

class Ticker:
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = self.__get_data()
        self.__laenge()
    
    def __repr__(self):
        return(self.ticker)
        
    def __str__(self):
        return(self.ticker)
       
    @property
    def financials(self):
        return self.__morningstar_financials()
    
    @property
    def marginofsales(self):
        return self.__morningstar_margins_of_sales()
    
    @property
    def profitability(self):
        return self.__morningstar_profitability()
    
    @property
    def growth_rev(self):
        return self.__morningstar_growth_revenue()
    
    @property
    def growth_op_inc(self):
        return self.__morningstar_growth_operating_income()
    
    @property
    def growth_net_inc(self):
        return self.__morningstar_growth_net_income()
    
    @property
    def growth_eps(self):
        return self.__morningstar_growth_eps()
    
    @property
    def cf_ratios(self):
        return self.__morningstar_cashflow_ratios()
    
    @property
    def bs(self):
        return self.__morningstar_finhealth_bs()
    
    @property
    def li_fin(self):
        return self.__morningstar_finhealth_health()
    
    @property
    def efficiency(self):
        return self.__morningstar_effiency_ratios()
    
    
    def __get_data(self):
        
        headers = {'Referer': f'http://financials.morningstar.com/ratios/r.html?t={self.ticker}'}
        r = requests.get(f"http://financials.morningstar.com/finan/ajax/exportKR2CSV.html?&t={self.ticker}", headers=headers)
        csvdatei = r.content
        
        my_decoded_str = csvdatei.decode()
        my_decoded_str = my_decoded_str.split()
        
        return my_decoded_str
    
    def __laenge(self):
        if len(self.data) == 304:
            self.length = 0
        else:
            self.length = 1
       
    def __morningstar_financials(self):
                
        data = self.data
        length = self.length
            
        df_morningstar_financials = pd.DataFrame([Ticker.__data_list(data[12+length]), Ticker.__data_list(data[15+length])
                                        , Ticker.__data_list(data[19+length]), Ticker.__data_list(data[22+length])
                                        , Ticker.__data_list(data[26+length]), Ticker.__data_list(data[30+length])
                                        , Ticker.__data_list(data[32+length]), Ticker.__data_list(data[36+length])
                                        , Ticker.__data_list(data[38+length]), Ticker.__data_list(data[44+length])
                                        , Ticker.__data_list(data[49+length]), Ticker.__data_list(data[53+length])
                                        , Ticker.__data_list(data[58+length]), Ticker.__data_list(data[65+length])
                                        , Ticker.__data_list(data[69+length])]
                      , index =[Ticker.__index(data[10+length] + ' ' + data[11+length] + ' ' + data[12+length])
                                , Ticker.__index(data[13+length] + ' ' + data[14+length] + ' ' + data[15+length])
                                , Ticker.__index(data[16+length] + ' ' + data[17+length] + ' ' + data[18+length]+ ' ' + data[19+length])
                                , Ticker.__index(data[20+length] + ' ' + data[21+length] + ' ' + data[22+length])
                                , Ticker.__index(data[23+length] + ' ' + data[24+length] + ' ' + data[25+length]+ ' ' + data[26+length])
                                , Ticker.__index(data[27+length] + ' ' + data[28+length] + ' ' + data[29+length]+ ' ' + data[30+length])
                                , Ticker.__index(data[31+length] + ' ' + data[32+length])
                                , Ticker.__index(data[33+length] + ' ' + data[34+length] + ' ' + data[35+length]+ ' ' + data[36+length])
                                , Ticker.__index(data[37+length] + ' ' + data[38+length])
                                , Ticker.__index(data[39+length] + ' ' + data[40+length] + ' ' + data[41+length]+ ' ' + data[42+length]+ ' ' + data[43+length]+ ' ' + data[44+length])
                                , Ticker.__index(data[45+length] + ' ' + data[46+length] + ' ' + data[47+length]+ ' ' + data[48+length]+ ' ' + data[49+length])
                                , Ticker.__index(data[50+length] + ' ' + data[51+length] + ' ' + data[52+length]+ ' ' + data[53+length])
                                , Ticker.__index(data[54+length] + ' ' + data[55+length] + ' ' + data[56+length]+ ' ' + data[57+length]+ ' ' + data[58+length])
                                , Ticker.__index(data[59+length] + ' ' + data[60+length] + ' ' + data[61+length]+ ' ' + data[62+length]+ ' ' + data[53+length]+ ' ' + data[64+length]+ ' ' + data[65+length])
                                , Ticker.__index(data[66+length] + ' ' + data[67+length] + ' ' + data[68+length]+ ' ' + data[69+length])]
                      , columns = Ticker.__data_list(data[8+length] + data[9+length]))
    
        return df_morningstar_financials
    
    def __morningstar_margins_of_sales(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_margins_of_sales = pd.DataFrame([Ticker.__data_list(data[78+length]), Ticker.__data_list(data[79+length])
                                              , Ticker.__data_list(data[81+length]), Ticker.__data_list(data[82+length])
                                              , Ticker.__data_list(data[83+length]), Ticker.__data_list(data[84+length])
                                              , Ticker.__data_list(data[86+length]), Ticker.__data_list(data[91+length])
                                              , Ticker.__data_list(data[93+length])]
                          , index =['Revenue', 'COGS', 'Gross Margin', 'SG&A'
                                    , 'R&D', 'Other', 'Operating Margin', 'Net Int Inc & Other', 'EBT Margin']
                          , columns = Ticker.__data_list(data[77+length]))
        
        return self.morningstar_margins_of_sales
    
    def __morningstar_profitability(self):
        
        data = self.data
        length = self.length
    
        self.morningstar_profitability = pd.DataFrame([Ticker.__data_list(data[97+length]), Ticker.__data_list(data[100+length])
                                           , Ticker.__data_list(data[103+length]), Ticker.__data_list(data[107+length])
                                           , Ticker.__data_list(data[110+length]), Ticker.__data_list(data[114+length])
                                           , Ticker.__data_list(data[119+length]), Ticker.__data_list(data[121+length])]
                      , index =['Tax Rate %', 'Net Margin %', 'Asset Turnover (Average)', 'Return on Assets %'
                                , 'Financial Leverage (Average)', 'Return on Equity %', 'Return on Invested Capital %'
                                ,'Interest Coverage']
                      , columns = Ticker.__data_list(data[94+length]))
    
        return self.morningstar_profitability
    
    
    def __morningstar_growth_revenue(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_growth_revenue = pd.DataFrame([Ticker.__data_list(data[132+length]), Ticker.__data_list(data[134+length])
                                            , Ticker.__data_list(data[136+length]), Ticker.__data_list(data[138+length])]
                      , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                      , columns = Ticker.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.morningstar_growth_revenue
    
    def __morningstar_growth_operating_income(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_growth_operating_income = pd.DataFrame([Ticker.__data_list(data[144+length]), Ticker.__data_list(data[146+length])
                                                     , Ticker.__data_list(data[148+length]), Ticker.__data_list(data[150+length])]
                        , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                        , columns = Ticker.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.morningstar_growth_operating_income
    
    def __morningstar_growth_net_income(self):
        
        data = self.data
        length = self.length
        
        try: 
            self.morningstar_growth_net_income = pd.DataFrame([Ticker.__data_list(data[156+length]), Ticker.__data_list(data[158+length])
                                                   , Ticker.__data_list(data[160+length]), Ticker.__data_list(data[162+length])]
                          , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                          , columns = Ticker.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
        except(ValueError):
            Ticker.__data_list(data[156+length]).append(None)
            self.morningstar_growth_net_income = pd.DataFrame([Ticker.__data_list(data[156+length]), Ticker.__data_list(data[158+length])
                                                   , Ticker.__data_list(data[160+length]), Ticker.__data_list(data[162+length])]
                          , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                          , columns = Ticker.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.morningstar_growth_net_income
    
    def __morningstar_growth_eps(self):
        
        data = self.data
        length = self.length
    
        self.morningstar_growth_eps = pd.DataFrame([Ticker.__data_list(data[167+length]), Ticker.__data_list(data[169+length])
                                        , Ticker.__data_list(data[171+length]), Ticker.__data_list(data[173+length])]
                      , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                      , columns = Ticker.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.morningstar_growth_eps
        
    def __morningstar_cashflow_ratios(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_cashflow_ratios = pd.DataFrame([Ticker.__data_list(data[187+length]), Ticker.__data_list(data[193+length])
                                             , Ticker.__data_list(data[204+length]), Ticker.__data_list(data[204+length])
                                             , Ticker.__data_list(data[208+length])]
                      , index =['Operating Cash Flow Growth % YOY', 'Free Cash Flow Growth % YOY', 'Cap Ex as a % of Sales'
                                , 'Free Cash Flow/Sales %', 'Free Cash Flow/Net Income']
                      , columns =Ticker.__data_list(data[181+length]))
    
        return self.morningstar_cashflow_ratios
    
    def __morningstar_finhealth_bs(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_finhealth_bs = pd.DataFrame([Ticker.__data_list(data[223+length]), Ticker.__data_list(data[225+length])
                                          , Ticker.__data_list(data[226+length]), Ticker.__data_list(data[229+length])
                                          , Ticker.__data_list(data[232+length]), Ticker.__data_list(data[234+length])
                                          , Ticker.__data_list(data[235+length]), Ticker.__data_list(data[238+length])
                                          , Ticker.__data_list(data[240+length]), Ticker.__data_list(data[242+length])
                                          , Ticker.__data_list(data[244+length]), Ticker.__data_list(data[246+length])
                                          , Ticker.__data_list(data[248+length]), Ticker.__data_list(data[251+length])
                                          , Ticker.__data_list(data[254+length]), Ticker.__data_list(data[256+length])
                                          , Ticker.__data_list(data[259+length]), Ticker.__data_list(data[261+length])
                                          , Ticker.__data_list(data[264+length]), Ticker.__data_list(data[268+length])]
                          , index =['Cash & Short-Term Investments', 'Accounts Receivable', 'Inventory', 'Other Current Assets'
                                    , 'Total Current Assets', 'Net PP&E', 'Intangibles', 'Other Long-Term Assets', 'Total Assets'
                                    , 'Accounts Payable', 'Short-Term Debt', 'Taxes Payable', 'Accrued Liabilities'
                                    , 'Other Short-Term Liabilities', 'Total Current Liabilities', 'Long-Term Debt', 'Other Long-Term Liabilities'
                                    ,'Total Liabilities', "Total Stockholder's Equity", 'Total Liabilities & Equity']
                          , columns = Ticker.__data_list(data[218+length] + ' ' + data[219+length]))
    
        return self.morningstar_finhealth_bs
        
    def __morningstar_finhealth_health(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_finhealth_health = pd.DataFrame([Ticker.__data_list(data[273+length]), Ticker.__data_list(data[275+length])
                                              , Ticker.__data_list(data[277+length]), Ticker.__data_list(data[278+length])]
                          , index =['Current Ratio', 'Quick Ratio', 'Financial Leverage', 'Debt/Equity']
                          , columns = Ticker.__data_list(data[270+length] + ' ' + data[271+length]))
        
        return self.morningstar_finhealth_health
    
        
    def __morningstar_effiency_ratios(self):
        
        data = self.data
        length = self.length
        
        self.morningstar_effiency_ratios = pd.DataFrame([Ticker.__data_list(data[287+length]), Ticker.__data_list(data[289+length])
                                             , Ticker.__data_list(data[291+length]), Ticker.__data_list(data[294+length])
                                             , Ticker.__data_list(data[296+length]), Ticker.__data_list(data[298+length])
                                             , Ticker.__data_list(data[301+length]), Ticker.__data_list(data[303+length])]
                      , index =['Days Sales Outstanding', 'Days Inventory', 'Payables Period', 'Cash Conversion Cycle'
                                , 'Receivables Turnover', 'Inventory Turnover', 'Fixed Assets Turnover', 'Asset Turnover']
                      , columns = Ticker.__data_list(data[284+length]))
    
        return self.morningstar_effiency_ratios
    
    def __data_list(string):
        if '"' in string:
            substrings = []
            for s_quote_mark in string.split('"'):
                if len(s_quote_mark)>0: 
                    if s_quote_mark[0]=="," or s_quote_mark[-1]=="," or s_quote_mark==string:
                        for s_comma in s_quote_mark.split(','):
                            if len(s_comma)>0:
                                substrings.append(s_comma)
                            #else:
                            #    substrings.append(None)
                    else:
                        substrings.append(s_quote_mark)
        else: 
            substrings = string.split(',')
    
            for n, i in enumerate(substrings):
	            if len(substrings[n]) == 0:
		            substrings[n] = None
        
        del substrings[0]
    
        return substrings
    
    def __index(string):
        string = string.split(',')
        return string[0]