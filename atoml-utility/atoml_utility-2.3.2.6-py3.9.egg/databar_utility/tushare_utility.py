
import datetime
import pandas as pd
import tushare as ts

from general_utility.appbase import ab
from general_utility import utils as us

def get_pro_api():
    print(ts.__version__)

    # ts.set_token("99a3d9924862250708c3eedf178cda2517563dd9e4c954ec9a005dd9")
    ts.set_token("71edd678299d640e4bfb0fee41a6cfc3a3f7e417de2c05ac538a9e23")
        
    return ts.pro_api()

def tradingday_n(start_d = None, end_d = None, format = '%Y%m%d', last_day = 30, pro_api = None):
    if pro_api is None:
        pro_api = get_pro_api()

    '''
    获取交易日数据
    last_day: 表示需要查询的记录数,注意,start_d和last_day参数一般只使用一个
    '''
    if (end_d == None):
        end_d = datetime.date.today() # 默认为今天
    return_days = abs(last_day) # 间隔天数
    # last_day = last_day * 2
    while True:
        if (start_d is not None) and (isinstance(start_d, str)):
            start_d = datetime.datetime.strptime(start_d, format)
        if (end_d is not None) and (isinstance(end_d, str)):
            end_d = datetime.datetime.strptime(end_d, format)
        if (start_d is not None):
            # 如果设置了开始日期则先需要计算开始日期是否能够返回足够的数据,此处以设置的last_day为优先
            if isinstance(start_d, str):
                start_d = datetime.datetime.strptime(start_d, format)
        else:
            if (last_day > 0):
                start_d = end_d
                end_d = start_d + datetime.timedelta(days=abs(last_day)) # 获取未来的n个交易日
            else:
                start_d = end_d - datetime.timedelta(days=abs(last_day)) # 获取之前的n个交易日
        if isinstance(start_d, datetime.date):
            start_d = start_d.strftime("%Y%m%d")
        if isinstance(end_d, datetime.date):
            end_d = end_d.strftime("%Y%m%d")
        ab.print_log("query trade_cal from %s-%s" % (start_d, end_d))
        df = pro_api.query('trade_cal', exchange='', fields='cal_date', start_date=start_d, end_date=end_d, is_open='1')
        
        if (df.shape[0] < return_days):
            #数据不够时再来一次
            if (last_day > 0):
                end_d = start_d
                start_d = None
            else:
                start_d = None
            last_day = last_day * 2
        else:
            break
    return df['cal_date'].tail(return_days)

def next_tradingday(start_d = None, pro_api = None):
    if pro_api is None:
        pro_api = get_pro_api()

    format = "%Y%m%d"
    if (start_d is None):
        start_d = us.now(format)
    end_d = us.datetime_timedelta_n(start_d, -3)

    start_d = us.datetime_conv(start_d, str, format)
    end_d = us.datetime_conv(end_d, str, format)

    df = pro_api.query('trade_cal', exchange='', fields='cal_date', start_date=start_d, end_date=end_d, is_open='1')
    tradingday = df.iloc[0, 0]
    return tradingday

def get_current_from_tushare(codes, pro_api = None):
    date_format = "%Y%m%d"

    if pro_api is None:
        pro_api = get_pro_api()

    end_date = us.now(date_format)

    trading_day_50 = tradingday_n(None, end_date, date_format, -60, pro_api) # 获取最近的50个交易日

    if (trading_day_50 is not None): # 既然获取了交易日则以此计算起始日期
        start_date = us.datetime_conv(trading_day_50.head(1).values[0], str, date_format)

    dfs = pd.DataFrame()
    codes = us.params_split(codes, ",")
    for code in codes:
        df = ts.pro_bar( ts_code=code, api=pro_api, adj='qfq', start_date=start_date, end_date=end_date, ma=[5, 10, 20, 30, 50])
        if df is None:
            continue
        dfs = dfs.append(df.head(1), ignore_index=True)

    return dfs