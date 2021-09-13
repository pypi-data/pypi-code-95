from numpy.lib.function_base import append
import pandas as pd
import numpy as np
import os
import datetime
import traceback
import json
import requests
import re
from bs4 import BeautifulSoup
import xml
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry
from ...api.raw import RawDataApi
from ...view.raw_models import YahooIndexPrice, EmBTCFromWeb, EmFuturePriceDetail, EmFutureInfoDetail
from .raw_data_helper import RawDataHelper


class WebRawDataDownloader(object):

    def __init__(self, data_helper):
        self._data_helper = data_helper
        self._session = Session()
        self._session.mount('https://', HTTPAdapter(
            max_retries=Retry(total=10, backoff_factor=0.02),
        ))
        self._session.mount('http://', HTTPAdapter(
            max_retries=Retry(total=10, backoff_factor=0.02),
        ))

    def read_csv(self, csv_path):
        return pd.read_csv(csv_path, index_col=1)

    def fund_fee(self):
        pass

    def wind_fund_info(self, csv_path):
        # Update manually
        # Default file in company wechat is 'fundlist_wind_20202015.xlsx'
        df = pd.read_excel(csv_path)
        df.columns = ['wind_id', 'desc_name', 'full_name', 'start_date', 'end_date', 'benchmark', 'wind_class_1',
            'wind_class_2', 'currency', 'base_fund_id', 'is_structured', 'is_open', 'manager_id', 'company_id']
        df['start_date'] = df['start_date'].map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        df['end_date'] = df['end_date'].map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')
            if isinstance(x, str) else datetime.datetime.strptime('2040-12-31', '%Y-%m-%d'))
        df['is_structured'] = df['is_structured'].map(lambda x: False if x == '否' else True)
        df['is_open'] = df['is_open'].map(lambda x: False if x == '否' else True)
        self._data_helper._upload_raw(df, 'wind_fund_info')

    def cm_index_price(self, start_date, end_date):
        try:
            # history
            # default file in company wechat is 汇率数据.xls
            # df = pd.read_excel(csv_path)
            # df = df[['日期','美元中间价','欧元中间价','日元中间价','美元CFETS','欧元CFETS','日元CFETS']]
            # df.columns = ['datetime','usd_central_parity_rate','eur_central_parity_rate','jpy_central_parity_rate',
            #               'usd_cfets','eur_cfets','jpy_cfets']

            # auto update
            # data from http://www.chinamoney.com.cn/chinese/bkccpr
            start_date = datetime.datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
            url = ('http://www.chinamoney.com.cn/dqs/rest/cm-u-bk-ccpr/CcprHisExcelNew'
                f'?startDate={start_date}&endDate={end_date}&currency=USD/CNY,EUR/CNY,100JPY/CNY')
            headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')}
            filename = ''
            try:
                r = self._session.get(url, headers=headers, timeout=(15, 60))
                filename = os.path.join('/tmp', 'cm.xlsx')
                with open(filename, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print(f'[cm_index_price] got error {e}')
                return False
            df = pd.read_excel(filename)
            # Drop last 2 lines in excel, which are
            #   数据来源：	中国货币网
            #   www.chinamoney.com.cn
            df.drop(df.index[-2:], inplace=True)
            df = df[['日期', 'USD/CNY', 'EUR/CNY', '100JPY/CNY']]
            df.columns = ['datetime', 'usd_central_parity_rate', 'eur_central_parity_rate', 'jpy_central_parity_rate']
            df['jpy_central_parity_rate'] = df['jpy_central_parity_rate'] / 100
            df = df.sort_values('datetime')
            self._data_helper._upload_raw(df, 'cm_index_price')
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def cxindex_index_price(self, start_date, end_date):
        try:
            # history
            # default file in company wechat is 中证信用债指数历史数据.xls
            # df = pd.read_excel(csv_path)
            # df.columns = ['index_id', 'symbol', 'datetime', 'open', 'high', 'low', 'close', 'total_turnover', 'volume']
            # df['ret'] = df['close'] / df['close'].shift(1) - 1
            # df['index_id'] = 'credit_debt'
            # df = df.drop(['symbol'], axis=1)[:-2]

            # auto update
            # data from http://www.csindex.com.cn/zh-CN/indices/index-detail/H11073
            # File download url
            url = 'http://www.csindex.com.cn/uploads/file/autofile/perf/H11073perf.xls'
            headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')}
            filename = ''
            try:
                r = self._session.get(url, headers=headers, timeout=(15, 60))
                filename = os.path.join('/tmp', 'H11073perf.xls')
                with open(filename, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print(f'[cxindex_index_price] got error {e}')
                return False
            df = pd.read_excel(filename)
            df = df[['日期Date', '收盘Close', '涨跌幅(%)Change(%)', '成交量（万元）Volume(10 thousand CNY)',
                '成交金额（元）Turnover']]
            df.columns = ['datetime', 'close', 'ret', 'volume', 'total_turnover']
            df['volume'] = df['volume'].values * 10000
            df['ret'] = df['ret'] / 100
            start_date = str(pd.to_datetime(start_date).date() - datetime.timedelta(days=10)).replace('-','')
            df = df[(df['datetime']>=start_date) & (df['datetime']<=end_date)].sort_values('datetime')
            df['open'] = float('Nan')
            df['high'] = float('Nan')
            df['low'] = float('Nan')
            df['index_id'] = 'credit_debt'
            data = RawDataApi().get_cxindex_index_price_df(start_date, end_date)
            lst_time = data['datetime'].tolist()
            lst_str = [str(x) for x in lst_time]
            time_all = df['datetime'].tolist()
            time_all = [str(x.date()) for x in time_all]
            time_add = list(set(time_all).difference(set(lst_str)))
            data_ = pd.DataFrame()
            for i in time_add:
                data_ = pd.concat([data_,df[ df['datetime'] == i]])
            self._data_helper._upload_raw(data_, 'cxindex_index_price')
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def yahoo_index_price(self, start_date, end_date):
        try:
            # history
            # default file in company wechat is 大类资产指数据.xlsx
            # df = pd.read_excel(csv_path)
            # df['datetime'] = df['date']
            # for c in ['sp500', 'dax30', 'n225']:
            #     df_i = df[['datetime']].copy()
            #     df_i['close'] = df[c].copy()
            #     df_i['ret'] = df_i['close'] / df_i['close'].shift(1) - 1
            #     df_i['open'] = float('Nan')
            #     df_i['high'] = float('Nan')
            #     df_i['low'] = float('Nan')
            #     df_i['volume'] = float('Nan')
            #     df_i['total_turnover'] = float('Nan')
            #     df_i['index_id'] = c
            #     self._data_helper._upload_raw(df_i, 'yahoo_index_price')

            # auto update
            # data from
            # sp500 https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC
            # n225 https://finance.yahoo.com/quote/%5EN225/history?p=%5EN225
            # dax30 https://finance.yahoo.com/quote/%5EGDAXI/history/
            # File download url:
            # https://query1.finance.yahoo.com/v7/finance/download/%5EGSPC?period1=1553667756&period2=1585290156&interval=1d&events=history
            # https://query1.finance.yahoo.com/v7/finance/download/%5EN225?period1=1553673330&period2=1585295730&interval=1d&events=history
            # https://query1.finance.yahoo.com/v7/finance/download/%5EGDAXI?period1=1553673346&period2=1585295746&interval=1d&events=history

            url_prefix = 'https://query1.finance.yahoo.com/v7/finance/download/'

            trading_day = RawDataApi().get_em_tradedates().set_index('TRADEDATES')
            start_date_loc = trading_day.index.get_loc(pd.to_datetime(start_date).date(), method='ffill')
            end_date_loc = trading_day.index.get_loc(pd.to_datetime(end_date).date(), method='ffill')

            assert isinstance(start_date_loc, int), 'start date is not a valid trading day'
            assert isinstance(end_date_loc, int), 'end date is not a valid trading day'

            # TODO: (deprecated)由于我们目前更新的时间（次日0点），美股还没收盘，所以这里只能更新前一天的数据；之后再看看可能需要分批做自动更新
            # TODO: 更新时间暂时统一挪到美股收盘后了，这里直接更新当天数据
            extra_days = 0
            assert start_date_loc >= extra_days, 'there is no enough extra days before start date'
            start_date_with_extra_days = trading_day.index.array[start_date_loc - extra_days]
            print(f'start date with extra days: {start_date_with_extra_days}')

            assert end_date_loc >= extra_days, 'there is no enough extra days before end date'
            end_date_with_extra_days = trading_day.index.array[end_date_loc - extra_days]
            print(f'end date with extra days: {end_date_with_extra_days}')

            start_date = min(pd.to_datetime(start_date, infer_datetime_format=True) - datetime.timedelta(days=7), start_date_with_extra_days)
            start_timestamp = str(int((start_date).timestamp()))
            end_timestamp = str(int((datetime.datetime.strptime(end_date, '%Y%m%d') + datetime.timedelta(days=1)).timestamp()))
            url_postfix = f'?period1={start_timestamp}&period2={end_timestamp}&interval=1d&events=history'
            headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')}
            url_type_list = ['%5EGSPC', '%5EN225', '%5EGDAXI', '%5EFTSE', '%5EDJI', '%5Eixic']
            csv_list = ['^GSPC.csv', '^N225.csv', '^GDAXI.csv', '^FTSE.csv', '^DJI.csv', '^IXIC.csv']
            index_list = ['sp500', 'n225', 'dax30', 'ftse100', 'dji', 'ixic']
            df_list = []
            for url_type, csv_i, index_i in zip(url_type_list, csv_list, index_list):
                url = url_prefix + url_type + url_postfix
                filename = ''
                try:
                    r = self._session.get(url, headers=headers, timeout=(15, 60))
                    filename = os.path.join('/tmp', csv_i)
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                except Exception as e:
                    print(f'[yahoo_index_price] got error {e}')
                    continue
                df = pd.read_csv(filename)
                df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
                df.columns = ['datetime', 'open', 'high', 'low', 'close', 'adjclose', 'volume']
                df['datetime'] = df['datetime'].map(lambda x: pd.to_datetime(x, infer_datetime_format=True).date())
                df['index_id'] = index_i
                df['total_turnover'] = float('Nan')
                df['ret'] = df['adjclose'] / df['adjclose'].shift(1) - 1
                df = df.drop(['adjclose'], axis=1)
                df = df[df['datetime'].between(start_date_with_extra_days, end_date_with_extra_days)].sort_values('datetime')
                if not df.empty:
                    df_list.append(df)
            if df_list:
                df_all = pd.concat(df_list)
                self._data_helper._upload_raw(df_all, YahooIndexPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def sina_btc_download(self):
        try:
            url = 'https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20pp=/GlobalFuturesService.getGlobalFuturesDailyKLine?symbol=BTC'
            response = requests.get(url)
            dic = response._content.decode('utf8').replace('/*<script>location.href=\'//sina.com\';</script>*/\nvar pp=(','')[:-2]
            data = json.loads(dic)
            data = pd.DataFrame(data)
            data = data[['date','close']].copy()
            data.loc[:,'codes'] = 'cme_btc_cfd'
            td = pd.to_datetime(data.date)
            td = [i.date() for i in td]
            data.date = td
            raw = RawDataApi()
            df_existed = raw.get_btc(['cme_btc_cfd'])
            data = data[~data.date.isin(df_existed.date.tolist())]
            self._data_helper._upload_raw(data, EmBTCFromWeb.__table__.name)
            return True
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def cfe_future_data_download(self, start_date):
        try:
            month_part = start_date[:6]
            date_part = start_date[6:]
            url = f'http://www.cffex.com.cn/sj/hqsj/rtj/{month_part}/{date_part}/index.xml?id=15'
            response = requests.get(url)

            tag = response._content.decode('utf8').replace('<?xml version="1.0" encoding="UTF-8"?>\n\n<dailydatas>','')
            data = tag.splitlines()
            instrumentid = []
            tradingday = []
            openprice = []
            highestprice = []
            lowestprice = []
            closeprice = []
            preopeninterest = []
            openinterest = []
            presettlementprice = []
            settlementprice = []
            volume = []
            turnover = []
            expiredate = []
            # 股指期货数据
            for line in data:
                if 'IO' in line:
                    break
                else:
                    if 'instrumentid' in line:
                        instrumentid.append(line.split(' ')[-1].partition("instrumentid>")[-1].partition("</instrumentid")[0])
                    elif 'tradingday' in line:
                        tradingday.append(line.split(' ')[-1].partition("tradingday>")[-1].partition("</tradingday")[0])
                    elif 'openprice' in line:
                        openprice.append(line.split(' ')[-1].partition("openprice>")[-1].partition("</openprice")[0])
                    elif 'highestprice' in line:
                        highestprice.append(line.split(' ')[-1].partition("highestprice>")[-1].partition("</highestprice")[0])
                    elif 'lowestprice' in line:
                        lowestprice.append(line.split(' ')[-1].partition("lowestprice>")[-1].partition("</lowestprice")[0])
                    elif 'closeprice' in line:
                        closeprice.append(line.split(' ')[-1].partition("closeprice>")[-1].partition("</closeprice")[0])
                    elif 'preopeninterest' in line:
                        preopeninterest.append(line.split(' ')[-1].partition("preopeninterest>")[-1].partition("</preopeninterest")[0])
                    elif 'openinterest' in line:
                        openinterest.append(line.split(' ')[-1].partition("openinterest>")[-1].partition("</openinterest")[0])
                    elif 'presettlementprice' in line:
                        presettlementprice.append(line.split(' ')[-1].partition("presettlementprice>")[-1].partition("</presettlementprice")[0])
                    elif 'settlementprice' in line:
                        settlementprice.append(line.split(' ')[-1].partition("settlementprice>")[-1].partition("</settlementprice")[0])
                    elif 'volume' in line:
                        volume.append(line.split(' ')[-1].partition("volume>")[-1].partition("</volume")[0])
                    elif 'turnover' in line:
                        turnover.append(line.split(' ')[-1].partition("turnover>")[-1].partition("</turnover")[0])
                    elif 'expiredate' in line:
                        expiredate.append(line.split(' ')[-1].partition("expiredate>")[-1].partition("</expiredate")[0])

                    else:
                        pass
            # 国债期货数据
            acount = 0
            for line in data:
                if 'T' in line:
                    acount = 1
                else:
                    pass
                if acount == 1:
                    if 'instrumentid' in line:
                        instrumentid.append(line.split(' ')[-1].partition("instrumentid>")[-1].partition("</instrumentid")[0])
                    elif 'tradingday' in line:
                        tradingday.append(line.split(' ')[-1].partition("tradingday>")[-1].partition("</tradingday")[0])
                    elif 'openprice' in line:
                        openprice.append(line.split(' ')[-1].partition("openprice>")[-1].partition("</openprice")[0])
                    elif 'highestprice' in line:
                        highestprice.append(line.split(' ')[-1].partition("highestprice>")[-1].partition("</highestprice")[0])
                    elif 'lowestprice' in line:
                        lowestprice.append(line.split(' ')[-1].partition("lowestprice>")[-1].partition("</lowestprice")[0])
                    elif 'closeprice' in line:
                        closeprice.append(line.split(' ')[-1].partition("closeprice>")[-1].partition("</closeprice")[0])
                    elif 'preopeninterest' in line:
                        preopeninterest.append(line.split(' ')[-1].partition("preopeninterest>")[-1].partition("</preopeninterest")[0])
                    elif 'openinterest' in line:
                        openinterest.append(line.split(' ')[-1].partition("openinterest>")[-1].partition("</openinterest")[0])
                    elif 'presettlementprice' in line:
                        presettlementprice.append(line.split(' ')[-1].partition("presettlementprice>")[-1].partition("</presettlementprice")[0])
                    elif 'settlementprice' in line:
                        settlementprice.append(line.split(' ')[-1].partition("settlementprice>")[-1].partition("</settlementprice")[0])
                    elif 'volume' in line:
                        volume.append(line.split(' ')[-1].partition("volume>")[-1].partition("</volume")[0])
                    elif 'turnover' in line:
                        turnover.append(line.split(' ')[-1].partition("turnover>")[-1].partition("</turnover")[0])
                    elif 'expiredate' in line:
                        expiredate.append(line.split(' ')[-1].partition("expiredate>")[-1].partition("</expiredate")[0])

                    else:
                        pass
                else:
                    pass

            # 结算价去空格（是个坑）
            clear = []
            for i in range(1,len(settlementprice),2):
                clear.append(settlementprice[i])
            dic = {'em_id':instrumentid ,'datetime':tradingday ,'open':openprice,'high':highestprice ,'low':lowestprice,
                'close':closeprice, 'uni_oi':openinterest,'pre_clear':presettlementprice ,
                'clear':clear,'uni_volume':volume,'uni_amount':turnover}

            tag = pd.DataFrame(dic)
            tag.datetime = pd.to_datetime(tag.datetime)
            tag.em_id = tag.em_id + '.CFE'
            self._data_helper._upload_raw(tag, EmFuturePriceDetail.__table__.name)
            return True

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False


    def cfe_future_info_download(self):
        # 中金所期货信息下载
        try:
            # 国债期货部分信息
            def debt_info():
                dic1 ={'每日价格最大波动限制':'price_limit',
                    '最低交易保证金':'first_trans_margin',
                    '最后交易日':'last_trans_date',
                    '最小变动价位':'min_price_change',
                    '合约月份':'contract_date_info',
                    '交易时间':'trans_date_info',
                    '上市交易所':'mkt_name',
                    '交易代码':'product'}

                index_info = [['2ts','2017-02-17','2年期国债期货',20000,'元/手'],
                            ['5tf','2013-09-06','5年期国债期货',10000,'元/手'],
                            ['10tf','2015-03-20','10年期国债期货',10000,'元/手']]

                df1_ = pd.DataFrame()
                for index in index_info:
                    url_ = "http://www.cffex.com.cn/"+index[0]+"/"
                    f_ = requests.get(url_)                 
                    soup_ = BeautifulSoup(f_.content, "lxml")  


                    for k in soup_.find_all('div',class_='table_introduction debt_table_introduction'):
                        a = k.find_all('td')  

                    info_list = []

                    for line in a:
                        info_list.append(str(line).partition("td>")[-1].partition("</td")[0])

                    while '' in info_list:
                        info_list.remove('')
                    while '\n' in info_list:   
                        info_list.remove('\n')
                    key = []
                    value = []

                    for i in range(len(info_list)):
                        if i % 2==0:
                            key.append(info_list[i])
                        if i % 2==1:
                            value.append(info_list[i])

                    df=pd.DataFrame({'key':key,'value':value}).set_index('key').T
                    ddf2 = df[dic1.keys()].rename(columns=dic1)
                    ddf2['list_standard_date'] = index[1]
                    ddf2['trans_type'] = index[2]
                    ddf2['trans_unit'] = str(index[3]*100) + index[4]
                    ddf2['contract_mul'] = index[3]
                    ddf2['price_unit'] = index[4]
                    ddf2['price_limit_range'] = ddf2['price_limit']
                    df1_ = pd.concat([df1_,ddf2],axis=0)
                    df1_['short_eng_name'] = None
                    df1_['eng_name'] = None
                    df1_
                return df1_
            # 股指期货部分信息
            def index_info():
                dic = {'合约标的 ':'trans_type',
                    '每日价格最大波动限制':'price_limit',
                    '最低交易保证金':'first_trans_margin',
                    '最后交易日':'last_trans_date',
                    '合约乘数':'trans_unit',
                    '报价单位':'price_unit',
                    '最小变动价位':'min_price_change',
                    '交割日期':'deliver_date_info',
                    '合约月份':'contract_date_info',
                    '交易时间':'trans_date_info',
                    '上市交易所':'mkt_name',
                    '交易代码':'product'}

                df_ = pd.DataFrame()
                indexs = [['hs300','2010-04-16'],['zz500','2015-04-16'],['sz50','2015-04-16']]
                for index in indexs:
                    url = "http://www.cffex.com.cn/"+index[0]+"/"
                    f = requests.get(url)                 #Get该网页从而获取该html内容
                    soup = BeautifulSoup(f.content, "lxml")  #用lxml解析器解析该网页的内容, 好像f.text也是返回的html


                    for k in soup.find_all('div',class_='table_introduction debt_table_introduction'):
                        a = k.find_all('td')  
                    info_list = []

                    for line in a:
                        info_list.append(str(line).partition("td>")[-1].partition("</td")[0])

                    while '' in info_list:
                        info_list.remove('')
                    while '\n' in info_list:   
                        info_list.remove('\n')
                    key = []
                    value = []

                    for i in range(len(info_list)):
                        if i % 2==0:
                            key.append(info_list[i])
                        if i % 2==1:
                            value.append(info_list[i])

                    ddf=pd.DataFrame({'key':key,'value':value}).set_index('key').T
                    ddf['合约标的 '] = ddf['合约标的 '][0][:-2] + '股指期货'
                    ddf1 = ddf[dic.keys()].rename(columns=dic)
                    pattern = re.compile(r'\d+')
                    res = re.findall(pattern, ddf1['trans_unit'][0])
                    ddf1['contract_mul'] = res
                    ddf1['list_standard_date'] = index[1]
                    ddf1['price_limit_range'] = ddf1['price_limit']
                    df_ = pd.concat([df_,ddf1],axis=0)
                    df_['short_eng_name'] = None
                    df_['eng_name'] = None
                return df_

            # 基准价\开始\结束交易日
            url = 'http://www.cffex.com.cn/cp/index_6719.xml?id=1'
            response = requests.get(url)
            tag = response._content.decode('utf8').replace('<?xml version="1.0" encoding="UTF-8"?>\n\n<dailydatas>','')
            data = tag.splitlines()

            trading_code = []
            quote_price = []
            start_trade_date = []
            last_trade_date = []

            for line in data:
                if 'IO' in line:
                    break
                else:
                    if 'INSTRUMENTID' in line:
                        trading_code.append(line.split(' ')[-1].partition("INSTRUMENTID>")[-1].partition("</INSTRUMENTID")[0])
                    elif 'BASISPRICE' in line:
                        quote_price.append(line.split(' ')[-1].partition("BASISPRICE>")[-1].partition("</BASISPRICE")[0])
                    elif 'OPENDATE' in line:
                        start_trade_date.append(line.split(' ')[-1].partition("OPENDATE>")[-1].partition("</OPENDATE")[0])
                    elif 'ENDDELIVDATE' in line:
                        last_trade_date.append(line.split(' ')[-1].partition("ENDDELIVDATE>")[-1].partition("</ENDDELIVDATE")[0])
                    else:
                        pass

            acount = 0
            for line in data:
                if 'T2' in line:
                    acount = 1
                else:
                    pass
                if acount == 1:
                    if 'INSTRUMENTID' in line:
                        trading_code.append(line.split(' ')[-1].partition("INSTRUMENTID>")[-1].partition("</INSTRUMENTID")[0])
                    elif 'BASISPRICE' in line:
                        quote_price.append(line.split(' ')[-1].partition("BASISPRICE>")[-1].partition("</BASISPRICE")[0])
                    elif 'OPENDATE' in line:
                        start_trade_date.append(line.split(' ')[-1].partition("OPENDATE>")[-1].partition("</OPENDATE")[0])
                    elif 'ENDDELIVDATE' in line:
                        last_trade_date.append(line.split(' ')[-1].partition("ENDDELIVDATE>")[-1].partition("</ENDDELIVDATE")[0])
                    else:
                        pass
                else:
                    pass  
            df = pd.DataFrame({'trading_code':trading_code,
                            'quote_price':quote_price,
                            'start_trade_date':start_trade_date,
                            'last_trade_date':last_trade_date})

            df['deliv_month'] = df['last_trade_date'].apply(lambda x:x[:6])
            df.start_trade_date = pd.to_datetime(df.start_trade_date)
            df.last_trade_date = pd.to_datetime(df.last_trade_date)
            df['deliver_date'] = df['last_trade_date']

            # 保证金
            url1 = 'http://www.cffex.com.cn/sj/jscs/202108/16/index.xml?id=26'
            response1 = requests.get(url1)
            tag1 = response1._content.decode('utf8').replace('<?xml version="1.0" encoding="UTF-8"?>\n\n<dailydatas>','')
            data1 = tag1.splitlines()

            trading_code = []
            trans_margin = []
            long_margin = []
            short_margin = []
            product = []

            for line in data1:
                if 'INSTRUMENTID' in line:
                    trading_code.append(line.split(' ')[-1].partition("INSTRUMENTID>")[-1].partition("</INSTRUMENTID")[0])
                elif 'JGHMARGIN' in line:
                    trans_margin.append(line.split(' ')[-1].partition("JGHMARGIN>")[-1].partition("</JGHMARGIN")[0])
                elif 'LONGMARGINRATIO' in line:
                    long_margin.append(line.split(' ')[-1].partition("LONGMARGINRATIO>")[-1].partition("</LONGMARGINRATIO")[0])
                elif 'SHORTMARGINRATIO' in line:
                    short_margin.append(line.split(' ')[-1].partition("SHORTMARGINRATIO>")[-1].partition("</SHORTMARGINRATIO")[0])
                elif 'PRODUCTID' in line:
                    product.append(line.split(' ')[-1].partition("PRODUCTID>")[-1].partition("</PRODUCTID")[0])
                else:
                    pass

            df1 = pd.DataFrame({'trading_code':trading_code,
                                'trans_margin':trans_margin,
                                'long_margin':long_margin,
                                'short_margin':short_margin,
                                'product':product})
            df1[['long_margin','short_margin']] = df1[['long_margin','short_margin']].applymap(lambda x:float(x)*100)

            df1['em_id'] = df1.trading_code+'.CFE'
            df1['desc_name'] = df1.trading_code
            # 最后合并表格
            df_=index_info()
            df1_ = debt_info()

            result1 = pd.merge(pd.merge(df1,df_,on='product',how='inner'),df,on='trading_code')
            result2 = pd.merge(pd.merge(df1,df1_,on='product',how='inner'),df,on='trading_code')
            result = pd.concat([result1,result2],axis=0)
            result = result.drop(columns='product')
            exsited_future_info = RawDataApi().get_em_future_info()
            new_df = result[~result.em_id.isin(exsited_future_info.em_id)]
            if not new_df.empty:
                self._data_helper._upload_raw(new_df, EmFutureInfoDetail.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def dce_future_info_download(self):
        try:
            future = [['铁矿石','http://www.dce.com.cn/dalianshangpin/sspz/487477/487481/1500303/index.html','2013-05-16',2,32],
                    ['焦煤','http://www.dce.com.cn/dalianshangpin/sspz/487450/487454/1500228/index.html','2013-03-22',0,30],
                    ['焦炭','http://www.dce.com.cn/dalianshangpin/sspz/487423/487427/1499525/index.html','2019-04-30',2,32],
                    ['聚乙烯','http://www.dce.com.cn/dalianshangpin/sspz/487342/487346/1498988/index.html','2007-07-31',1,31],
                    ['聚氯乙烯','http://www.dce.com.cn/dalianshangpin/sspz/487369/487373/1499103/index.html','2009-05-25',1,31],
                    ['聚丙烯','http://www.dce.com.cn/dalianshangpin/sspz/487396/487400/1499431/index.html','2014-02-28',1,31],
                    ['乙二醇','http://www.dce.com.cn/dalianshangpin/sspz/yec63/6138350/6139005/index.html','2018-12-10',2,32],
                    ['苯乙烯','http://www.dce.com.cn/dalianshangpin/sspz/byx/hyygz42/6189178/index.html','2019-09-26',0,30],
                    ['液化石油气','http://www.dce.com.cn/dalianshangpin/sspz/yhsyq/hyygz7622/6210766/index.html','2020-03-30',1,31],
                    ['玉米','http://www.dce.com.cn/dalianshangpin/sspz/ym/hyygz/486238/index.html','2004-09-22',0,30],
                    ['淀粉','http://www.dce.com.cn/dalianshangpin/sspz/2081746/2081749/2081867/index.html','2014-12-19',1,31],
                    ['豆一','http://www.dce.com.cn/dalianshangpin/sspz/487124/487128/1391009/index.html','1999-01-18',1,31],
                    ['豆二','http://www.dce.com.cn/dalianshangpin/sspz/487153/487157/6040854/index.html','2004-12-22',2,32],
                    ['豆粕','http://www.dce.com.cn/dalianshangpin/sspz/487180/487184/1391326/index.html','2000-07-17',2,32],
                    ['豆油','http://www.dce.com.cn/dalianshangpin/sspz/487207/487211/1472342/index.html','2006-01-09',2,32],
                    ['棕榈油','http://www.dce.com.cn/dalianshangpin/sspz/487234/487238/1495874/index.html','2007-10-29',2,32],
                    ['鸡蛋','http://www.dce.com.cn/dalianshangpin/sspz/487261/487265/1498768/index.html','2013-11-08',2,32],
                    ['粳米','http://www.dce.com.cn/dalianshangpin/sspz/jm43/hyygz18/6178989/index.html','2019-08-16',2,32],
                    ]
            tag = pd.DataFrame()
            for index in future:
            #     print(index[0])
                url = index[1]
                f = requests.get(url)                 
                soup = BeautifulSoup(f.content, "lxml")  
                for k in soup.find_all('div',class_='detail_content'):
                    a = k.find_all('p')  
                info_list = []
                for line in a:
                    info_list.append(str(line).partition(';">')[-1].partition("</p")[0])
                    
                for i in range(len(info_list)):
                    if 'DCE' in info_list[i]:
                        info_list[i] = info_list[i].partition('（F')[0]

                while '' in info_list:
                    info_list.remove('') 
                        
                info_list = info_list[index[3]:index[4]] 
                key = []
                value = []
                for i in range(len(info_list)):
                    if i % 2==0:
                        key.append(info_list[i])
                    if i % 2==1:
                        value.append(info_list[i])
                ddf=pd.DataFrame({'key':key,'value':value}).set_index('key').T
                dic = {'涨跌停板幅度':'price_limit',
                    '最低交易保证金':'first_trans_margin',
                    '最后交易日':'last_trans_date',
                    '交易单位':'trans_unit',
                    '报价单位':'price_unit',
                    '最小变动价位':'min_price_change',
                    '最后交割日':'deliver_date_info',
                    '合约月份':'contract_date_info',
                    '交易时间':'trans_date_info',
                    '上市交易所':'mkt_name',
                    '交易代码':'product'}
                ddf1 = ddf[dic.keys()].rename(columns=dic)
                pattern = re.compile(r'\d+')
                res = re.findall(pattern, ddf1['trans_unit'][0])
                ddf1['contract_mul'] = res
                res1 = re.findall(pattern, ddf1['price_limit'][0])
                ddf1['price_limit_range'] = res1
                res2 = re.findall(pattern, ddf1['first_trans_margin'][0])
                ddf1['trans_margin'] = res2
                ddf1['long_margin']= res2
                ddf1['short_margin']= res2
                ddf1['list_standard_date'] = index[2]
                tag = pd.concat([tag,ddf1],axis=0)
            # 获取表格
            url1 = 'http://www.dce.com.cn/publicweb/businessguidelines/queryContractInfo.html'
            f1 = requests.get(url1)  
            soup1 = BeautifulSoup(f1.content, "lxml")
            for k in soup1.find_all('div',class_='dataWrapper'):
                c = k.find_all('tr')

            info_list1 = []
            for line in c:
                info_list1.append(str(line).partition('>')[-1].partition("</tr")[0])    
                
            lis1 = []
            for n in info_list1[0].split('><'):
                lis1.append(str(n).partition('>')[-1].partition("</th")[0])
                
            info = pd.DataFrame()
            for i in range(1,len(info_list1)):
                lis = []
                for n in info_list1[i].split('><'):
                    lis.append(str(n).partition('>')[-1].partition("</td")[0])

                pattern = re.compile(r'\d+')
                lis[3] = re.findall(pattern, info_list1[i].split('><')[3])[0]
                info = pd.concat([info,pd.DataFrame(lis)],axis=1) 
            df = pd.concat([pd.DataFrame({'key':lis1}),info],axis=1).set_index('key').T.reset_index(drop=True)
                
            dic1 = {'品种':'trans_type',
                    '合约代码':'trading_code',
                    '开始交易日':'start_trade_date',
                    '最后交易日':'last_trade_date',
                    '最后交割日':'deliver_date'}
            df = df[dic1.keys()].rename(columns=dic1)
            df['product'] = df['trading_code'].apply(lambda x:x[:-4].upper())
            df['em_id'] = df['trading_code'].apply(lambda x:x.upper() + '.DCE')
            result = pd.merge(df,tag,on='product',how='inner').drop(columns='product')
            result['deliv_month'] = result['deliver_date'].apply(lambda x:x[:6])
            result['start_trade_date'] = result['start_trade_date'].apply(lambda x:pd.to_datetime(str(x),format='%Y-%m-%d'))
            result['last_trade_date'] = result['last_trade_date'].apply(lambda x:pd.to_datetime(str(x),format='%Y-%m-%d'))
            result['deliver_date'] = result['deliver_date'].apply(lambda x:pd.to_datetime(str(x),format='%Y-%m-%d'))
            result['desc_name'] = result['trans_type'] + result['trading_code'].apply(lambda x:x[-4:])
            result['short_eng_name'] = None
            result['eng_name'] = None
            result['quote_price'] = None
            result['price_limit'] = result['price_limit'].map(lambda x: ''.join([s for s in x if s.isdigit()]))
            exsited_future_info = RawDataApi().get_em_future_info()
            new_df = result[~result.em_id.isin(exsited_future_info.em_id)]
            if not new_df.empty:
                self._data_helper._upload_raw(new_df, EmFutureInfoDetail.__table__.name)
            return True

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def download_all(self, start_date, end_date):
        failed_tasks = []
        if not self.cm_index_price(start_date, end_date):
            failed_tasks.append('cm_index_price')

        if not self.cxindex_index_price(start_date, end_date):
            failed_tasks.append('cxindex_index_price')

        if not self.yahoo_index_price(start_date, end_date):
            failed_tasks.append('yahoo_index_price')

        if not self.sina_btc_download():
            failed_tasks.append('sina_btc_close')

        return failed_tasks


if __name__ == "__main__":
    data_helper = RawDataHelper()
    web_downloader = WebRawDataDownloader(data_helper)
    # web_downloader.cm_index_price('20200408', '20200508')
    # web_downloader.yahoo_index_price('20210709', '20210709')
    # web_downloader.cxindex_index_price('20210617', '20210617')
