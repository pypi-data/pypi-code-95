import numpy as np
import numpy.linalg as la
import pandas as pd
from sklearn.metrics import *
from xgboost import XGBClassifier
from matplotlib import pyplot as plt
#from model.dl_model import *
from sklearn import linear_model
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
import tushare as ts
try:
    from numpy.lib.stride_tricks import sliding_window_view
except:
    pass

ts.set_token('46304a165e1a71a0ff4ffaaa9c3da977498c1d1c918c798322ffe6b1')
pro = ts.pro_api()


def label_percent(df_factor, percent_select, sort_col='next_ret', class_num=2, delete=False, ret_threshold=0.01,
                  fillna=True):
    df_factor.loc[:, 'bin'] = None
    if ret_threshold:
        df_factor.loc[(df_factor[sort_col] > df_factor[sort_col].quantile(q=percent_select[0])) &
                      (df_factor['next_ret'] > ret_threshold), 'bin'] = 1
    else:
        df_factor.loc[df_factor[sort_col] > df_factor[sort_col].quantile(q=percent_select[0]), 'bin'] = 1

    if class_num == 2:
        df_factor.loc[df_factor[sort_col] <= df_factor[sort_col].quantile(q=percent_select[1]), 'bin'] = 0
    elif class_num == 3:
        df_factor.loc[df_factor[sort_col] <= df_factor[sort_col].quantile(q=percent_select[1]), 'bin'] = -1

    if delete:
        df_factor.dropna(subset=['bin'], inplace=True)
    else:
        if fillna:
            df_factor.loc[:, 'bin'] = df_factor['bin'].fillna(0)  # 2分类问题标签必须是0或者1，所以若数据不删除则必须填充
        else:
            pass
    return df_factor


def label_threshold(df_stk, threshold, sort_col='next_ret', class_num=2):
    if class_num == 2:
        df_stk['bin'] = df_stk[sort_col].apply(lambda x: 1 if x > threshold else 0)
    return df_stk

# alpha大于0的股票标1否则标0
def lable_alpha(df_stk, df_index, diff=False, percent_select=None, delete=True):
    df_stk = df_stk.groupby(level=1).apply(lambda df: get_alpha(df, df_index, diff=diff))
    if not percent_select:
        df_stk['bin'] = df_stk['alpha'].apply(lambda x: 1 if x > 0 else 0)
    else:
        label_percent(df_stk, percent_select, sort_col='alpha', delete=delete)
    return df_stk

def get_beta(stk_ret, index_ret):
    beta = np.cov(stk_ret, index_ret)[0][1] / np.var(index_ret)
    return beta

def get_alpha(df_stk, df_benchmark, diff=False):
    # 找到每只股票的交易时间
    dates = df_stk.index.get_level_values('date').drop_duplicates().astype(str).tolist()
    # 找到收益率
    stk_ret = df_stk['next_ret'].values
    index_ret = df_benchmark[df_benchmark.index.isin(dates)]['next_ret'].values
    # 判断是直接做差得到alpha还是通过线性回归得到alpha
    df_stk['alpha'] = None
    if diff:
        for trade_date in dates:
            diff = df_stk.loc[trade_date, 'next_ret'] - \
                   df_benchmark[df_benchmark.index == str(trade_date).split()[0]].next_ret.values[0]
            df_stk.loc[trade_date, ['alpha']] = diff.tolist()
    else:
        # 计算贝塔
        try:
            beta = get_beta(stk_ret, index_ret)
        except:
            print(df_stk.iloc[0], stk_ret.shape, index_ret.shape)
        # 得到alpha
        df_stk.loc[:, ['alpha']] = (stk_ret - beta * index_ret).tolist()
    return df_stk

#得到x列和y列
def get_x_y(df, no_x_cols, label_col):
    x = df[df.columns.difference(no_x_cols)]
    y = df[label_col]#.astype(int)
    return x,y

#按时序分割x,y
def split_x_y(x, y, train_ratio=0.8):
    train_len = int(train_ratio * len(x))

    x_train = x[:train_len]
    y_train = y[:train_len]

    x_test = x[train_len:]
    y_test = y[train_len:]

    return x_train, y_train, x_test, y_test

#按时序分割成df_train, df_test
def split_df(x, y, train_ratio=0.8):
    train_len = int(train_ratio * len(x))

    x_train = x[:train_len]
    y_train = y[:train_len]

    x_test = x[train_len:]
    y_test = y[train_len:]

    return x_train, y_train, x_test, y_test

# 行业中性化
def data_scale_neutral(data, feature_names, indu_col='industry'):
    # feature_names = get_feature_names(data)
    data_ = data.copy()
    industrys = data[indu_col]  # 获取所属申万一级行业代码
    data_med = pd.get_dummies(data, columns=[indu_col], drop_first=True)
    n = len(data[indu_col].unique())  # 确定产生虚拟变量个数
    X = np.array(data_med[data_med.columns[-(n - 1):]])  # 行业虚拟变量作为为自变量
    for name in feature_names:
        y = np.array(data_[name])
        if la.matrix_rank(X.T.dot(X)) == (n - 1):  # 当矩阵满秩时，估计回归参数
            beta_ols = la.inv(X.T.dot(X)).dot(X.T).dot(y)
            residual = y - X.dot(beta_ols)  # 计算残差，并将其作为剔除行业影响的因子值
        else:
            residual = y  # 如果逆不存在的话 则 用原值
        data_[name] = residual
    return data_

# 市值中性化
def data_scale_cap(df, scale_cols, cap_col='FloatCap_Ln'):
    cap_weight = df[cap_col]/df[cap_col].sum()
    avg = (df[scale_cols].T*cap_weight).sum(axis=1)
    df.loc[:,scale_cols] = (df[scale_cols] - avg)/(df[scale_cols].std() + 1e-8)
    return df

# 去极值
def process_extreme_data(df, factor_cols, method='mad', extreme_num=5, datetime_index='date'):
    '''
    去极值函数
    :param df: 包含日期、代码、因子值的df
    :param factor_cols:因子列
    :param method: mad中位数法，std标准差法
    :param extreme_num: 离差倍数
    :param datetime_index: 日期索引名称
    :return:
    '''

    def _filter_extreme_mad(arr, n=5):
        median = np.nanquantile(arr, 0.5, axis=0)
        new_median = np.nanquantile(np.abs(arr - median), 0.5, axis=0)
        max_range = median + n * new_median
        min_range = median - n * new_median
        return np.clip(arr, min_range, max_range)

    def _filter_extreme_std(arr, n=3):
        mean = np.mean(arr, axis=0)
        std = np.std(arr, axis=0)
        max_range = mean + n * std
        min_range = mean - n * std
        return np.clip(arr, min_range, max_range)

    if method == 'mad':
        df.loc[:, factor_cols] = df.groupby(datetime_index)[factor_cols].apply(
            lambda x: pd.DataFrame(_filter_extreme_mad(x.values, extreme_num), index=x.index, columns=x.columns))
    elif method == 'std':
        df.loc[:, factor_cols] = df.groupby(datetime_index)[factor_cols].apply(
            lambda x: pd.DataFrame(_filter_extreme_std(x.values, extreme_num), index=x.index, columns=x.columns))
    return df


#数据标准化
def data_scale(df, factor_cols, scaler = None):

    df_basic_cols = df[df.columns.difference(factor_cols)]
    index_ = df.index
    df_proc = df.loc[:, factor_cols]

    # 如果没有scaler，初始化一个，如果有，用已经fit过的
    if not scaler:
        scaler = StandardScaler()
        arr_proc = scaler.fit_transform(df[factor_cols])
    else:
        arr_proc = scaler.transform(df[factor_cols]) # 直接调用传入的scaler进行分布转换
    df_proc = pd.DataFrame(arr_proc, index = index_, columns = factor_cols)
    df = pd.concat([df_basic_cols, df_proc], axis=1)
    return df, scaler

def select_factors(x, model, threshold=0.8, method='xgb_importance', num=20):
    if method == 'xgb_importance':
        df_score = pd.DataFrame({'importance':list(model.feature_importances_), 'name':x.columns.tolist()})
        df_score.sort_values('importance', ascending=False, inplace=True)
    #如果规定了因子数量优先采用数量筛选
    if num:
        df_important = df_score.iloc[:20]
    else:
        df_important = df_score[df_score.importance >= df_score.importance.quantile(threshold)]
    selected_factors = df_important.name.tolist()
    return selected_factors

def get_IR(series):
    yieldRate = series.iat[-1]
    IR = yieldRate/series.std()
    return IR

def get_maxdraw(series):
    series += 1
    max_draw_down = 0
    temp_max_value = 0
    for i in range(1, len(series)):
        temp_max_value = max(temp_max_value, series.iat[i - 1])
        # temp_max_value=max(series[:i])
        max_draw_down = min(max_draw_down, (series.iat[i] / temp_max_value) - 1)
    return max_draw_down

def get_calmar(series):
    max_draw_down = get_maxdraw(series)
    calmar = (series.iat[-1] - 1) / max_draw_down
    return calmar

def group_share_calmar(df_item):
    df_item['rise_ratio'] = df_item.close.iloc[0]
    df_item.rise_ratio = df_item.close / df_item.rise_ratio - 1
    series = df_item.rise_ratio
    sharpe = get_IR(series)
    calmar = get_calmar(series)
    df_item.iloc[-1, -3] = sharpe
    df_item.iloc[-1, -2] = calmar
    return df_item

def factor_ret(df, Y):
    X = df.iloc[:, 0]
    rlm_model = sm.RLM(Y, X, M=sm.robust.norms.HuberT()).fit()
    factor_ret = rlm_model.params
    factor_ret = factor_ret.values[0]
    return factor_ret

def group_factor_ret(df, ret_type='normal'):
    Y = df.next_ret
    df = df[factor_cols]
    if ret_type == 'rank':
        df = df.rank(ascending=True, method='dense')
        df_ret = df.groupby(axis=1, level=0).apply(
            lambda x: sm.RLM(Y, x.iloc[:, 0], M=sm.robust.norms.HuberT()).fit().params.values[0])
    elif ret_type == 'normal':
         df_ret = df.groupby(axis=1, level=0).apply(
            lambda x: sm.RLM(Y, x.iloc[:, 0], M=sm.robust.norms.HuberT()).fit().params.values[0])
    return df_ret

def backtest(df_weight, df_next_ret, fee_rate=0.001, model=0, show=True):

    # 构造交易权重矩阵
    df_turnover = df_weight.diff()
    df_fee = (np.abs(df_turnover) * fee_rate)

    df_ret = df_next_ret * df_weight - df_fee
    df_ret_day = df_ret.sum(axis=1)
    df_pnl = df_ret_day.cumsum() if model == 0 else (1+df_ret_day).cumprod()
    if show: df_pnl.plot();plt.show()

    return df_pnl

def ts_backtest(df_ret, order_col='order', ret_col='next_open2open',
                fee_rate=0.002, title='', show=True, model=0):
    '''
    :param df_ret: 包含下期收益率和交易方向的DataFrame
    :param order_col: 交易方向列名
    :param ret_col: 收益列名
    :param fee_rate: 交易费用比率
    :param show: 是否显示回测曲线
    :param model: 0：单利，1：复利
    :return: 附带pnl曲线的DataFrame
    '''
    df_ret['fee'] = np.abs(df_ret[order_col].diff() * fee_rate)
    df_ret['ret'] = df_ret[order_col] * df_ret['next_open2open'] - df_ret['fee']
    if model==0 :df_ret['pnl'] = df_ret['ret'].cumsum()
    else: df_ret['pnl'] = df_ret['ret'].cumprod()
    if show:df_ret['pnl'].plot(title=title);plt.show()
    return df_ret

def cal_date(start, end, period, dtype='str', opening=-1):
    # 修正时间字符串格式
    start = start.replace('-', '')
    end = end.replace('-', '')
    # 取交易日历
    df = pro.query('trade_cal', start_date=start, end_date=end)
    df_d = df[df.is_open == 1]
    df_d.set_index(pd.to_datetime(df_d['cal_date'], format='%Y%m%d'), inplace=True)
    cal_dates = pd.Series()
    # 判断取期初还是期末
    if opening == 1:
        option = 'first'
    else:
        option = 'last'

    # 判断周期
    if period == 'D':
        cal_dates = df_d['cal_date']
    elif period == 'W':
        df_w = df_d.resample('W').agg({'cal_date': option})
        cal_dates = df_w['cal_date']
    elif period == 'M':
        df_m = df_d.resample('M').agg({'cal_date': option})
        cal_dates = df_m['cal_date']
    # 删除空值
    cal_dates.dropna(inplace=True)
    # 判断返回类型
    if dtype == 'str':
        cal_dates = cal_dates.astype(str).apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[
                                                                                       6:]).tolist()  # .index.to_series().dt.strftime('%Y-%m-%d').tolist()
    elif dtype == 'dt':
        cal_dates = pd.to_datetime(cal_dates, format='%Y%m%d').dt.date.tolist()
    return cal_dates


def check_df_code(df_stk, target='int', code_col='code'):
    '''
    检查df的code列格式，并转换为指定格式
    :param df_stk:
    :param target:
    :return:
    '''

    if target=='int':
        if isinstance(df_stk[code_col].iat[0], (np.int64, np.int, np.int32)):
            pass
        if df_stk[code_col].dtype==type(str):
            df_stk[code_col] = df_stk[code_col].apply(lambda x:int(x[:6]))
    elif target=='tushare':
        if df_stk[code_col].dtype == type(str):
            suffix = df_stk[code_col].iat[0].split()[-1]
            if suffix == 'SZ' or suffix=='SH':
                pass
            else:
                df_stk[code_col] = df_stk[code_col].apply(lambda x: x[:6] + '.SH' if x[0] == '6' else x[:6] + '.SZ')

        if isinstance(df_stk[code_col].iat[0], (np.int64, np.int, np.int32)):
            df_stk[code_col] = df_stk[code_col].apply(lambda x:str(x).zfill(6))
            df_stk[code_col] = df_stk[code_col].apply(lambda x: x+'.SH' if x[0]=='6' else x+'.SZ')
    elif target=='jk':
        if df_stk[code_col].dtype == type(str):
            suffix = df_stk[code_col].iat[0].split()[-1]
            if suffix == 'XSHG' or suffix=='XSHE':
                pass
            else:
                df_stk[code_col] = df_stk[code_col].apply(lambda x: x[:6] + '.XSHG' if x[0] == '6' else x[:6] + '.XSHE')

        if isinstance(df_stk[code_col].iat[0], (np.int64, np.int, np.int32, np.float)):
            df_stk[code_col] = df_stk[code_col].apply(lambda x:str(x).zfill(6))
            df_stk[code_col] = df_stk[code_col].apply(lambda x: x+'.XSHG' if x[0]=='6' else x+'.XSHE')
    return df_stk

def check_format(df, code_col='code', date_col='datetime', code_type='int'):
    if df.index.names[0]: df.reset_index(inplace=True) # 有索引就reset
    unnamed_cols = list(filter(lambda x: 'Unnamed' in x, df.columns))
    df.drop(unnamed_cols, axis=1, inplace=True)
    df.rename(columns={'ticker':code_col, 'code':code_col, 'S_INFO_WINDCODE':code_col}, inplace=True)
    df.rename(columns={'date': date_col, 'datetime':date_col, 'TRADE_DT': date_col, 'ANN_DT':date_col}, inplace=True)
    df = check_df_code(df, target=code_type, code_col=code_col)
    df[date_col] = pd.to_datetime(df[date_col].astype(str))
    return df

def check_index(df, target_index=['code', 'datetime'], code_col='code', date_col='datetime', code_type='int'):
    df = check_format(df, code_col=code_col, date_col=date_col, code_type=code_type)
    idx_names = df.index.names
    set_cols = []
    for col in target_index:
        if col not in idx_names:
            set_cols.append(col)
    if len(set_cols) < len(target_index):
        df.set_index(set_cols, inplace=True, append=True)
    else:
        df.set_index(set_cols, inplace=True)
    if df.index.names != target_index:
        df.index = df.index.swaplevel()
    return df


# 按照行业均值填充
def fillna_industry_mean(df_tmp_indu, factor_col):
    na_flag = df_tmp_indu[factor_col].isnull().any()
    if na_flag.sum()>0:
        industry_mean = df_tmp_indu[na_flag[na_flag].index].mean()
        df_tmp_indu.fillna(industry_mean, inplace=True)
    return df_tmp_indu

# 对统一格式的因子数据，按行业均值填充
def fillna_indu(df_factor, df_industry, factor_cols, industry_col='industry'):
    '''
    :param df_factor:  含有code列的因子数据
    :param df_industry: 含有code列的行业数据
    :param factor_cols: 因子列
    :return:
    '''
    df_factor = pd.merge(df_factor, df_industry.loc[:, ['code', industry_col]], on='code', how='left')
    # 设置索引
    df_factor.set_index(['date', 'code'], inplace=True)
    df_factor = df_factor.groupby(industry_col, as_index=False).apply(
        lambda x: x.groupby(level='date').apply(lambda y: fillna_industry_mean(y, factor_cols)))
    return df_factor[factor_cols]

def merge_data(df_raw, df_merge, target_col=None, key_col=None):
    '''
    向原始数据拼接新列
    :param df_raw: 原数据df
    :param df_merge: 要拼接的数据df
    :param target_col: 要拼接的单列
    :param key_col: 使用merge方法的on对应的列
    :return:
    '''

    if df_raw.index.names==df_merge.index.names and df_raw.index.dtype== df_merge.index.dtype:
        df_raw[target_col] = df_merge[target_col]
    else:
        if target_col:
            merge_cols = [target_col] + [key_col] if ~isinstance(key_col, list) else [target_col] + key_col
        else:
            merge_cols = df_merge.columns
        if key_col in df_raw.index.names:
            df_raw.reset_index(inplace=True)
        df_raw = pd.merge(df_raw, df_merge[merge_cols], on=key_col)
        df_raw.set_index(['date','code'], inplace=True)
    return df_raw

def fq(df, target_cols = ['open', 'high', 'low', 'close'], adjust_type='pre'):
    '''
    :param df: 行情数据df，带有复权因子列adj_factor
    :param target_cols: 要复权的列
    :param adjust_type: pre:前复权  post:后复权
    :return:
    '''
    if adjust_type=='pre':
        adj_factor = df['adj_factor'].iat[-1]
    else:
        adj_factor = df['adj_factor'].iat[0]
    df.loc[:, target_cols] = df[target_cols].mul(df['adj_factor'],axis=0) / adjust_type
    return df

def get_decay_wlist(length, halflife, direction=1, normalizing=True):
    '''
    :param length: 权重列表长度
    :param halflife: 半衰期
    :param direction: 1代表从大到小排列，-1代表从小到大排列
    :param normalizing: 是否对权重标准化，使其求和为1
    :return:
    '''
    N = length
    H = halflife  # 半衰期
    if normalizing:
        w_denominator = np.sum([2 ** (-t / H) for t in range(1, N + 1)])
        w = np.array([(2 ** ((i - N - 1) / H)) / w_denominator for i in range(1, N + 1)][::-1])
    else:
        w = np.array([(2 ** ((i - N - 1) / H)) for i in range(1, N + 1)][::-1])
    if direction == -1:
        w = w[::-1]
    return w

def top_turnover(df, factor, stk_num=100, dt_idx='datetime', code_idx='ticker'):
    df_pool = df.groupby(dt_idx).apply(lambda x: x.sort_values(factor, ascending=False).iloc[:stk_num])
    df_pool[factor] = 1/stk_num
    df_pool = df_pool.pivot(index=dt_idx, columns=code_idx, values=factor)
    df_pool.fillna(0, inplace=True)
    print(abs(df_pool.diff()).sum(axis=1).median())

def fator_stability(df, factor, code_col='ticker', date_col='datetime'):
    df_table = df.dropna(axis=0).pivot(index=code_col, columns=date_col, values=factor)
    df_corr = df_table.corr()
    auto_corr = np.diag(df_corr.shift(-1))
    factor_stab = np.nanmean(auto_corr)
    return factor_stab

def get_cnn_data(df, factor_cols, time_step):
    '''
    example: df_data = df_factor.groupby('ticker').apply(lambda x: get_cnn_data(x, factor_cols, 5))
    '''
    if len(df)>=time_step:
        df_basic = df.iloc[time_step-1:][['datetime']].reset_index(drop=True)
        df_window = sliding_window_view(df[factor_cols], time_step, axis=0)
        df_window = list(map(lambda x: x, df_window))
        df_basic['data'] = pd.Series(df_window)
        return df_basic

if __name__ == '__main__':
    #from factor_stat import FactorRetStat

    df_factor = pd.read_csv(r'D:\work\ZNC\reinforced\test_data\df_factor_test.csv', index_col=['date', 'code'], parse_dates=['date'])
    # 非X列
    no_x_columns = ['codes', 'date', 'next_ret', 'bin', 'end_date', 'alpha', 'MKT_CAP_ASHARE', 'sharpe', 'calmar', 'IR']
    # 得到特征列
    factor_cols = list(df_factor.columns.difference(no_x_columns))
    
    df_factor.loc[:, factor_cols] = df_factor.loc[:, factor_cols].groupby(level=0).apply(lambda x:x.groupby(axis=1, level=0).apply(lambda y:filter_extreme_mad(y[y.columns[0]], 5)))    
    
    hxx = x_train.groupby(axis=1, level=0).apply(lambda df1: mutual_info_score(y_train, df1.iloc[:,0]))
    hxx.sort_values(inplace=True)
    # dates = df_factor.index.get_level_values('date').drop_duplicates()
    # df_factor.sort_index(inplace=True)
    # df_factor = df_factor.loc[:dates[-1]]
    # financial = FactorRetStat()
    # df_factor_ret = df_factor.groupby(level=0).apply(financial.group_factor_ret)
    # data = financial.data_concat(df_factor[factor_cols], df_factor_ret)

    # data.columns = map(lambda x:str(x), data.columns)
    # x = data[data.columns.difference(['Y'])]
    # y = data['Y'].apply(lambda x: 1 if x>0 else 0)
    # x_train, y_train, x_test, y_test = split_x_y(x, y)

    # model = get_model()
    # model.fit(x_train.values, y_train.values)
    # pred = model.predict(x_test.values)
    # pred_proba = model.predict_proba(x_test.values)[:, 1]
    # index_ = np.argwhere(pred_proba >= np.percentile(pred_proba, 80))#.reshape(1,-1).tolist()[0]
    # index_ = np.argwhere(pred == 1).reshape(1,-1).tolist()[0]
    # auc = roc_auc_score(y_test.values, pred)
    # acc = accuracy_score(y_test.values, pred)
    # select_factors = x_test.iloc[index_].index.get_level_values(1).tolist()

    #df_factor_ret = df.groupby(level=0).apply(group_factor_ret)
    #df_factor_basic  = df.reset_index().pivot(index='date', columns=df.columns)
    #df_factor_basic = df.groupby(level=0).apply(lambda x:x.transpose())
    # df_tmp = df.loc[dates[0]]#.transpose()
    # seri_next_ret = df_tmp.next_ret
    #
    # Y = df_tmp.next_ret
    # df_tmp = df_tmp[factor_cols]
    # seri_col_g = [df for i,df in df_tmp.groupby(axis=1, level=0)]
    # df_facter_test = seri_col_g[0]
    # df_facter_test.sort_values(df_facter_test.columns[0], ascending=False, inplace=True)

    #df_test2 = df_test.reset_index(col_level=0)

    #df_facter_test = df_facter_test.rank(ascending=True, method='dense')

    # X = df_facter_test.iloc[:, 0]#.rank(ascending=True, method='dense')
    # # df_facter_test = df_tmp.groupby(axis=1, level=0).apply(lambda x: x.rank(ascending=True, method='dense'))
    # # X = df_facter_test.drop(['end_date', 'next_ret'], axis=1)
    # rlm_model = sm.RLM(Y, X, M=sm.robust.norms.HuberT()).fit()
    # factor_ret = rlm_model.params


    # 计算IR
    # df_basic = pd.read_csv(r'D:\work\ZNC\reinforced\test_data/df_basic.csv',index_col=['date', 'code'], parse_dates=['date'])
    # df_benchmark = pd.read_csv(r'D:\work\ZNC\reinforced\test_data/df_benchmark.csv', index_col='date')
    #
    # df_basic = df_basic.loc[df_benchmark.index[0]:df_benchmark.index[-1]]
    #
    # df_list = [df for i,df in df_basic.groupby(level=1)]
    #
    # df_stk = df_list[0]
    #
    # dates = df_stk.index.get_level_values('date').drop_duplicates().astype(str).tolist()
    #
    # df_stk['rise_ratio'] = df_stk.close.iloc[0]
    # df_stk.rise_ratio = df_stk.close / df_stk.rise_ratio
    #
    # df_benchmark_tmp = df_benchmark[df_benchmark.index.isin(dates)]
    # df_benchmark_tmp['rise_ratio'] = df_benchmark_tmp.close/df_benchmark_tmp.close.iat[0]
    # seri_extra_yield = pd.Series(df_stk['rise_ratio'].values - df_benchmark_tmp['rise_ratio'].values)
    #
    # # IR = get_IR(seri_extra_yield)
    # calmar = get_calmar(seri_extra_yield)

    
    # df = pd.read_csv(r'D:\work\ZNC\reinforced\test_data\df_factor.csv', index_col=['date', 'code'])
    # df_y = pd.read_csv(r'D:\work\ZNC\reinforced\database\夏普calmar月度数据.csv', index_col=['date', 'code'])
    # df['sharpe'] = df_y['sharpe']
    # df['calmar'] =  df_y['calmar']
    # df.dropna(axis=0, inplace=True)
    # no_x_columns = ['codes', 'date', 'next_ret', 'bin', 'end_date', 'alpha', 'MKT_CAP_ASHARE']
    # factor_cols = df.columns.difference(no_x_columns)

    # x = df[factor_cols]
    # # df['bin_ret'] = df['next_ret'].apply(lambda x: 1 if x>0 else 0)
    # # df['bin_sharpe'] = df['sharpe'].apply(lambda x: 1 if x>0 else 0)
    # # df['bin_calmar'] = df['calmar'].apply(lambda x: 1 if x>0 else 0)
    
    
    # y_ret = df['next_ret'].apply(lambda x: 1 if x>0 else 0)
    # y_sharpe = df['sharpe'].apply(lambda x: 1 if x>0 else 0)
    # y_calmar = df['calmar'].apply(lambda x: 1 if x>0 else 0)


    # x_train, y_ret_train, x_test, y_ret_test = split_x_y(x, y_ret)
    # y_sharpe_train, y_calmar_train, y_sharpe_test, y_calmar_test = split_x_y(y_sharpe, y_calmar)
    

    #第一轮训练
    # from xgboost import plot_importance
    # model1 = get_model()
    # model1.fit(x_train, y_ret_train)
    # x1 = model1.predict_proba(x_train)[:, 1]
    # x1_test = model1.predict_proba(x_test)[:, 1]
    # y_pred1 = model1.predict(x_test)
    # auc1 = roc_auc_score(y_ret_test, y_pred1)

    # model2 = get_model()
    # model2.fit(x_train, y_sharpe_train)
    # x2 = model2.predict_proba(x_train)[:, 1]
    # x2_test = model2.predict_proba(x_test)[:, 1]
    # y_pred2 = model2.predict(x_test)
    # auc2 = roc_auc_score(y_ret_test, y_pred2)
    
    # model3 = get_model()
    # model3.fit(x_train, y_calmar_train)
    # x3 = model3.predict_proba(x_train)[:, 1]
    # x3_test = model3.predict_proba(x_test)[:, 1]
    # y_pred3 = model3.predict(x_test)
    # auc3 = roc_auc_score(y_ret_test, y_pred3)

    # x_train_final = np.r_[x1, x2, x3].reshape(-1,1)
    # y_train_final = np.r_[y_ret_train, y_sharpe_train, y_calmar_train].reshape(-1,1)
    # #x_train_final = np.array([x1, x2, x3])#.T
    # #y_train_final = np.array([y_ret_train, y_sharpe_train, y_calmar_train])
    # x_test_final = np.r_[x1_test, x2_test, x3_test]

    # ln_model = linear_model.LogisticRegression()
    # ln_model.fit(x_train_final, y_train_final)
    # y_pred = ln_model.predict(x_test_final)
    # auc = roc_auc_score(y_ret_test, y_pred)      
    
    # proba_sum = (x1_test + x2_test + x3_test) / 3
    # sum_flag = [1 if x>0.5 else 0 for x in proba_sum]
    # auc_sum = roc_auc_score(y_ret_test, sum_flag)


    # 算出隐藏层
    # input_dim = x.shape[1]
    # first_hidden_units = input_dim * 4
    # floor_num = 4
    # HiddenLayer = list(range(first_hidden_units, 0, -int(first_hidden_units / floor_num)))
    # HiddenDropout = [0.2] * len(HiddenLayer)   
    
    # model = auto_encoder(input_dim, HiddenLayer, HiddenDropout)
    # model.fit(x, x, epochs=30, batch_size=1024, verbose=True)

    # model.fit(x_train,y_train)
    #
    # # 使用模型预测
    # y_pred = model.predict(x_test)
    #
    # accuracy = accuracy_score(y_test, y_pred)
    # auc = roc_auc_score(y_test, y_pred)
    #
    # ### plot feature importance
    # # fig,ax = plt.subplots(figsize=(15,15))
    # #
    # # plot_importance(model,
    # #                 height=0.5,
    # #                 ax=ax,
    # #                 max_num_features=20)
    # # fig.show()
    #
    # #特征重要性筛选
    # selected_factors = select_factors(x_train, model, threshold=0.65, method='xgb_importance')
    # model.fit(x_train.loc[:,selected_factors], y_train)
    # # 使用模型预测
    # y_pred = model.predict(x_test.loc[:,selected_factors])
    # accuracy2 = accuracy_score(y_test, y_pred)
    # auc2 = roc_auc_score(y_test, y_pred)
    #
    # # #互信息筛选
    # # hxx = x_train.groupby(axis=1, level=0).apply(lambda df1: mutual_info_score(y_train, df1.iloc[:,0]))
    # # hxx.sort_values(inplace=True)
    # # selected_factors = hxx[hxx >= hxx.quantile(0.3)].index.tolist()
    # # model.fit(x_train.loc[:,selected_factors], y_train)
    # # # 使用模型预测
    # # y_pred = model.predict(x_test.loc[:,selected_factors])
    # # accuracy3 = accuracy_score(y_test, y_pred)
    # # auc3 = roc_auc_score(y_test, y_pred)
    #
    # # #train上面表现增强否
    # # y_pred = model.predict(x_train.loc[:,selected_factors])
    # # accuracy4 = accuracy_score(y_train, y_pred)
    # # auc4 = roc_auc_score(y_train, y_pred)