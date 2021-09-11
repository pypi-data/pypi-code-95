#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:20
@File    : pandas.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import logging
import os
import re
from abc import ABC
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import xlrd

from ibats_utils.iter import reduce_list, get_last
from ibats_utils.transfer import str_2_date, try_2_date

logger = logging.getLogger(__name__)


def get_df_between_date(data_df, date_frm, date_to):
    """
    该函数仅用于 return_risk_analysis 中计算使用
    :param data_df:
    :param date_frm:
    :param date_to:
    :return:
    """
    if date_frm is not None and date_to is not None:
        new_data_df = data_df[(data_df.Date >= date_frm) & (data_df.Date <= date_to)]
    elif date_frm is not None:
        new_data_df = data_df[data_df.Date >= date_frm]
    elif date_to is not None:
        new_data_df = data_df[data_df.Date <= date_to]
    else:
        new_data_df = data_df
    new_data_df = new_data_df.reset_index(drop=True)
    return new_data_df


def _get_df_between_date_by_index(data_df, date_frm, date_to):
    """
    该函数仅用于 return_risk_analysis 中计算使用
    :param data_df:
    :param date_frm:
    :param date_to:
    :return:
    """
    if date_frm is not None and date_to is not None:
        new_data_df = data_df[(data_df.index >= date_frm) & (data_df.index <= date_to)]
    elif date_frm is not None:
        new_data_df = data_df[data_df.index >= date_frm]
    elif date_to is not None:
        new_data_df = data_df[data_df.index <= date_to]
    else:
        new_data_df = data_df
    return new_data_df


class DataFrame(pd.DataFrame, ABC):
    def interpolate_inner(self, columns=None, inplace=False):
        if columns is None:
            columns = list(self.columns)
        data = self if inplace else self.copy()
        for col_name in columns:
            index_not_nan = data.index[~np.isnan(data[col_name])]
            if index_not_nan.shape[0] == 0:
                continue
            index_range = (min(index_not_nan), max(index_not_nan))
            # data[col_name][index_range[0]:index_range[1]].interpolate(inplace=True)
            data[col_name][index_range[0]:index_range[1]] = data[col_name][index_range[0]:index_range[1]].interpolate()
        # print(data)
        if ~inplace:
            return data

    def map(self, func):
        row_count, col_count = self.shape
        columns = list(self.columns)
        indexes = list(self.index)
        for col_num in range(col_count):
            col_val = columns[col_num]
            for row_num in range(row_count):
                row_val = indexes[row_num]
                data_val = self.iloc[row_num, col_num]
                self.iloc[row_num, col_num] = func(col_val, row_val, data_val)
        return self


def merge_nav(df_list, date_from=None):
    """
    合并 df_list 将净值进行合并
    :param df_list:
    :param date_from:
    :return:
    """
    nav_df = None
    for nav_tmp_df in df_list:
        if nav_df is None:
            nav_df = nav_tmp_df
        else:
            nav_df = nav_df.merge(nav_tmp_df, how='outer', right_index=True, left_index=True)
    # 净值拟合
    # def calc_mean(nav_s):
    #     nav_sub_s = nav_s.dropna()
    #     if nav_sub_s.shape[0] == 0:
    #         mean_val = np.nan
    #     else:
    #         mean_val = nav_sub_s.mean()
    #     return mean_val

    pct_df = nav_df.pct_change()
    pct_mean_s = pct_df.mean(axis=1).fillna(0) + 1
    # 进行日期过滤
    if date_from is not None:
        pct_mean_s = pct_mean_s[pct_mean_s.index >= str_2_date(date_from)]
    nav_merged_df = pd.DataFrame({"nav": pct_mean_s.cumprod()})
    stat_df, _ = return_risk_analysis(nav_merged_df, freq=None)
    stat_funds_df, _ = return_risk_analysis(nav_df, freq=None)
    stat_all_df = stat_df.merge(stat_funds_df, how='outer', right_index=True, left_index=True)
    return nav_merged_df, nav_df, stat_all_df


def merge_nav_from_file(file_list, date_from=None):
    """
    从excel或csv文件中读取历史净值数据，进行合并
    :param file_list:
    :param date_from:
    :return:
    """
    df_list = []
    error_dic = {}
    for file_info_dic in file_list:
        # 读取文件
        file_path = file_info_dic['file_path']
        file_path_no_extention, file_extension = os.path.splitext(file_path)
        try:
            if file_extension == '.csv':
                data_df = pd.read_csv(file_path)
            elif file_extension in ('.xls', '.xlsx'):
                data_df = pd.read_excel(file_path, index_col=0).reset_index()
            else:
                error_dic['file type'] = '不支持 %s 净值文件类型' % file_extension
                continue
        except:
            error_dic['file read'] = '文件内容读取失败'
            logging.exception('文件内容读取失败：%s', file_path_no_extention)
            continue
        # 设置索引
        if 'date_column_name' in file_info_dic:
            date_column_name = file_info_dic['date_column_name']
            data_df.set_index(date_column_name, inplace=True)
        else:
            date_column_name = data_df.columns[0]
            data_df.set_index(date_column_name, inplace=True)
        # 设置索引日期格式
        data_df.index = [try_2_date(x) for x in data_df.index]
        # 取nav数据
        if 'nav_column_name_list' in file_info_dic:
            nav_column_name_list = file_info_dic['nav_column_name_list']
            if isinstance(nav_column_name_list, list):
                nav_column_name_dic = OrderedDict()
                for nav_column_name in nav_column_name_list:
                    if isinstance(nav_column_name, str):
                        nav_column_name_dic[nav_column_name] = nav_column_name
                    elif isinstance(nav_column_name, tuple):
                        nav_column_name_dic[nav_column_name[0]] = nav_column_name[1]
                    else:
                        raise ValueError("%s 列名称无效" % nav_column_name)
                nav_df = data_df[list(nav_column_name_dic.keys())].rename(columns=nav_column_name_dic)
            else:
                nav_df = data_df[[nav_column_name_list]]
        else:
            nav_df = data_df
        # 添加 df_list
        df_list.append(nav_df)
    # 合并
    nav_merged_df, nav_df, stat_df = merge_nav(df_list, date_from)
    return nav_merged_df, nav_df, stat_df


def return_risk_analysis_old(nav_df: pd.DataFrame, date_frm=None, date_to=None, freq='weekly', rf=0.02):
    """
    按列统计 rr_df 收益率绩效
    :param nav_df: 收益率DataFrame，index为日期，每一列为一个产品的净值走势
    :param date_frm: 统计日期区间，可以为空
    :param date_to: 统计日期区间，可以为空
    :param freq: None 自动识别, 'daily' 'weekly' 'monthly'
    :param rf: 无风险收益率，默认 0.02
    :return:
    """
    nav_df.index = [try_2_date(idx) for idx in nav_df.index]
    nav_sorted_df = nav_df.sort_index()
    rr_df = (1 + nav_sorted_df.pct_change().fillna(0)).cumprod()
    rr_df.index = [try_2_date(d) for d in rr_df.index]
    # 计算数据实际频率是日频、周频、月頻
    rr_df_len = rr_df.shape[0]
    day_per_data = (rr_df.index[rr_df_len - 1] - rr_df.index[0]).days / rr_df_len
    if day_per_data <= 0.005:
        freq_real = 'minute'
    elif day_per_data <= 0.2:
        freq_real = 'hour'
    elif day_per_data <= 2:
        freq_real = 'daily'
    elif day_per_data <= 10:
        freq_real = 'weekly'
    else:
        freq_real = 'monthly'
    if freq is None:
        freq = freq_real
    elif freq != freq_real:
        warnings_msg = "data freq wrong, expect %s, but %s was detected" % (freq, freq_real)
        # warnings.warn(warnings_msg)
        # logging.warning(warnings_msg)
        raise ValueError(warnings_msg)

    if freq == 'weekly':
        data_count_per_year = 50
        freq_str = '周'
    elif freq == 'monthly':
        data_count_per_year = 12
        freq_str = '月'
    elif freq == 'daily':
        data_count_per_year = 250
        freq_str = '日'
    elif freq == 'hour':
        data_count_per_year = 1250
        freq_str = '时'
    elif freq == 'minute':
        data_count_per_year = 75000
        freq_str = '分'
    else:
        raise ValueError('freq=%s 只接受 daily weekly monthly 三种之一', freq)
    stat_dic_dic = OrderedDict()
    # rr_df.index = [str_2_date(d) for d in rr_df.index]
    rr_uindex_df = rr_df.reset_index()
    col_name_list = list(rr_uindex_df.columns)
    date_col_name = col_name_list[0]
    col_name_list = col_name_list[1:]
    if type(date_frm) is str:
        date_frm = datetime.strptime(date_frm, '%Y-%m-%d').date()
    if type(date_to) is str:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    for col_name in col_name_list:
        data_df = rr_uindex_df[[date_col_name, col_name]]
        # print(data_df)
        data_df.columns = ['Date', 'Value']
        data_df = get_df_between_date(data_df, date_frm, date_to)
        data_df.Value = data_df.Value / data_df.Value[0]
        data_df['ret'] = data_df.Value.pct_change().fillna(0)
        date_span = data_df.Date[data_df.index[-1]] - data_df.Date[data_df.index[0]]
        date_span_fraction = 365 / date_span.days if date_span.days > 0 else 1
        # basic indicators
        CAGR = data_df.Value[data_df.index[-1]] ** date_span_fraction - 1
        period_rr = data_df.Value[data_df.index[-1]] - 1
        ann_vol = np.std(data_df.ret, ddof=1) * np.sqrt(data_count_per_year)
        down_side_vol = np.std(data_df.ret[data_df.ret < 0], ddof=1) * np.sqrt(data_count_per_year)
        # WeeksNum = data.shape[0]
        profit_loss_ratio = -np.mean(data_df.ret[data_df.ret > 0]) / np.mean(data_df.ret[data_df.ret < 0])
        win_ratio = len(data_df.ret[data_df.ret >= 0]) / len(data_df.ret)
        min_value = min(data_df.Value)
        final_value = data_df.Value[data_df.index[-1]]
        max_ret = max(data_df.ret)
        min_ret = min(data_df.ret)
        # End of basic indicators
        # max drawdown related
        data_df['mdd'] = data_df.Value / data_df.Value.cummax() - 1
        mdd_size = min(data_df.mdd)
        drop_array = pd.Series(data_df.index[data_df.mdd == 0])
        if len(drop_array) == 1:
            mdd_max_period = len(data_df.mdd)
        else:
            if float(data_df.Value[drop_array.tail(1)]) > float(data_df.Value.tail(1)):
                drop_array = drop_array.append(pd.Series(data_df.index[-1]), ignore_index=True)
            mdd_max_period = max(drop_array.diff().dropna()) - 1
        # End of max drawdown related
        # High level indicators
        sharpe_ratio = (CAGR - rf) / ann_vol
        sortino_ratio = (CAGR - rf) / down_side_vol
        calmar_ratio = CAGR / (-mdd_size)
        #  Natural month return
        j = 1
        for i in data_df.index:
            if i == 0:
                month_ret = pd.DataFrame([[data_df.Date[i], data_df.Value[i]]], columns=('Date', 'Value'))
            else:
                if data_df.Date[i].month != data_df.Date[i - 1].month:
                    month_ret.loc[j] = [data_df.Date[i - 1], data_df.Value[i - 1]]
                    j += 1
        month_ret.loc[j] = [data_df.Date[data_df.index[-1]], data_df.Value[data_df.index[-1]]]
        month_ret['ret'] = month_ret.Value.pct_change().fillna(0)
        max_rr_month = max(month_ret.ret)
        min_rr_month = min(month_ret.ret)
        # End of Natural month return
        data_len = data_df.shape[0]
        date_begin = data_df.Date[0]  # .date()
        date_end = data_df.Date[data_len - 1]
        stat_dic = OrderedDict([('起始日期', date_begin),
                                ('截止日期', date_end),
                                ('区间收益率', '%.2f%%' % (period_rr * 100)),
                                ('最终净值', '%.4f' % final_value),
                                ('最低净值', '%.4f' % min_value),
                                ('年化收益率', '%.2f%%' % (CAGR * 100)),
                                ('年化波动率', '%.2f%%' % (ann_vol * 100)),
                                ('年化下行波动率', '%.2f%%' % (down_side_vol * 100)),
                                ('最大回撤', '%.2f%%' % (mdd_size * 100)),
                                ('夏普率', '%.2f' % sharpe_ratio),
                                ('索提诺比率', '%.2f' % sortino_ratio),
                                ('卡马比率', '%.2f' % calmar_ratio),
                                ('盈亏比', '%.2f' % profit_loss_ratio),
                                ('胜率', '%.2f' % win_ratio),
                                ('最长不创新高（%s）' % freq_str, mdd_max_period),
                                ('统计周期最大收益', '%.2f%%' % (max_ret * 100)),
                                ('统计周期最大亏损', '%.2f%%' % (min_ret * 100)),
                                ('最大月收益', '%.2f%%' % (max_rr_month * 100)),
                                ('最大月亏损', '%.2f%%' % (min_rr_month * 100))])
        stat_dic_dic[col_name] = stat_dic
    stat_df = pd.DataFrame(stat_dic_dic)
    stat_df = stat_df.ix[list(stat_dic.keys())]
    return stat_df


def calc_performance(nav_df: pd.DataFrame, date_frm=None, date_to=None, freq='weekly', rf=0.02, suffix_name=None):
    """
    按列统计 rr_df 收益率绩效
    :param nav_df: 收益率DataFrame，index为日期，每一列为一个产品的净值走势
    :param date_frm: 统计日期区间，可以为空
    :param date_to: 统计日期区间，可以为空
    :param freq: None 自动识别, 'daily' 'weekly' 'monthly'
    :param rf: 无风险收益率，默认 0.02
    :param suffix_name: 前缀
    :return:
    """
    nav_sorted_df = nav_df.copy()
    nav_sorted_df.index = [try_2_date(idx) for idx in nav_sorted_df.index]
    nav_sorted_df.sort_index(inplace=True)
    # 计算数据实际频率是日频、周频、月頻
    data_count = nav_sorted_df.shape[0]
    day_per_data = (nav_sorted_df.index[data_count - 1] - nav_sorted_df.index[0]).days / data_count
    if day_per_data <= 0.008:
        freq_real = 'minute'
    elif day_per_data <= 0.2:
        freq_real = 'hour'
    elif day_per_data <= 2:
        freq_real = 'daily'
    elif day_per_data <= 10:
        freq_real = 'weekly'
    else:
        freq_real = 'monthly'
    if freq is None:
        freq = freq_real
    elif freq != freq_real:
        warnings_msg = "data freq wrong, expect %s, but %s was detected" % (freq, freq_real)
        # warnings.warn(warnings_msg)
        # logging.warning(warnings_msg)
        raise ValueError(warnings_msg)

    freq_str = ''
    if freq == 'weekly':
        data_count_per_year = 50
        freq_str = '周'
    elif freq == 'monthly':
        data_count_per_year = 12
        freq_str = '月'
    elif freq == 'daily':
        data_count_per_year = 250
        freq_str = '日'
    elif freq == 'hour':
        data_count_per_year = 1250
        freq_str = '时'
    elif freq == 'minute':
        data_count_per_year = 75000
        freq_str = '分'
    else:
        raise ValueError('freq=%s 只接受 daily weekly monthly 三种之一', freq)
    stat_dic_dic = OrderedDict()
    if type(date_frm) is str:
        date_frm = datetime.strptime(date_frm, '%Y-%m-%d').date()
    if type(date_to) is str:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

    col_name_list = list(nav_sorted_df.columns)
    # date_col_name = col_name_list[0]
    # col_name_list = col_name_list[1:]
    for col_name in col_name_list:
        data_sub_df = nav_sorted_df[[col_name]].dropna()
        if data_sub_df.shape[0] == 0:
            continue
        # rr_df = (1 + data_sub_df.pct_change().fillna(0)).cumprod()
        # rr_df.index = [try_2_date(d) for d in rr_df.index]
        # data_df = rr_df.reset_index()
        # data_df.columns = ['Date', 'Value']
        # 2018-07-01 不再重置索引，index为日期字段
        data_df = _get_df_between_date_by_index(data_sub_df, date_frm, date_to)
        data_df.columns = ['Value']
        rr_df = data_df.Value.pct_change().fillna(0)
        data_df.Value = (1 + rr_df).cumprod()
        data_df['ret'] = rr_df
        date_list = list(data_df.index)
        date_latest = date_list[-1]
        nav_latest = data_df.Value.loc[date_latest]
        # 计算 近7天，近30天，近365天收益率
        date_week_ago = date_latest - timedelta(days=7)
        date_month_ago = date_latest - timedelta(days=30)
        date_year_ago = date_latest - timedelta(days=365)
        date_week_ago = get_last(date_list, lambda x: x <= date_week_ago)
        date_month_ago = get_last(date_list, lambda x: x <= date_month_ago)
        date_year_ago = get_last(date_list, lambda x: x <= date_year_ago)
        rr_week = (nav_latest / data_df.Value.loc[date_week_ago] - 1) if date_week_ago is not None else None
        rr_month = (nav_latest / data_df.Value.loc[date_month_ago] - 1) if date_month_ago is not None else None
        rr_year = (nav_latest / data_df.Value.loc[date_year_ago] - 1) if date_year_ago is not None else None

        # 计算时间跨度
        date_span = date_list[-1] - date_list[0]
        date_span_fraction = 365 / date_span.days if date_span.days > 0 else 1
        # basic indicators
        CAGR = data_df.Value[date_latest] ** date_span_fraction - 1
        # 相当于余额宝倍数
        times_yeb = (CAGR - 1) / 0.03
        rr_tot = data_df.Value[date_latest] - 1
        ann_vol = np.std(data_df.ret, ddof=1) * np.sqrt(data_count_per_year)
        down_side_vol = np.std(data_df.ret[data_df.ret < 0], ddof=1) * np.sqrt(data_count_per_year)
        # WeeksNum = data.shape[0]
        profit_loss_ratio = -np.mean(data_df.ret[data_df.ret > 0]) / np.mean(data_df.ret[data_df.ret < 0])
        win_ratio = len(data_df.ret[data_df.ret >= 0]) / len(data_df.ret)
        min_value = min(data_df.Value)
        final_value = data_df.Value[data_df.index[-1]]
        max_ret = max(data_df.ret)
        min_ret = min(data_df.ret)
        # End of basic indicators
        # max drawdown related
        data_df['mdd'] = data_df.Value / data_df.Value.cummax() - 1
        mdd_size = min(data_df.mdd)
        drop_array = pd.Series(data_df.index[data_df.mdd == 0])
        if len(drop_array) == 1:
            mdd_max_period = len(data_df.mdd)
        else:
            if float(data_df.Value[drop_array.tail(1)]) > float(data_df.Value.tail(1)):
                drop_array = drop_array.append(pd.Series(data_df.index[-1]))  # , ignore_index=True
            mdd_max_period = max(drop_array.diff().dropna()).days - 1
        # End of max drawdown related
        # High level indicators
        sharpe_ratio = (CAGR - rf) / ann_vol
        sortino_ratio = (CAGR - rf) / down_side_vol
        calmar_ratio = CAGR / (-mdd_size)
        #  Natural month return
        j = 1
        for i, (date_4_df_idx, item) in enumerate(data_df.T.items()):
            if i == 0:
                month_ret = pd.DataFrame([[date_4_df_idx, item.Value]], columns=('Date', 'Value'))
            else:
                date_last_4_last = data_df.index[i - 1]
                if date_4_df_idx.month != date_last_4_last.month:
                    month_ret.loc[j] = [date_last_4_last, data_df.Value[date_last_4_last]]
                    j += 1

        month_ret.loc[j] = [date_latest, nav_latest]
        month_ret['ret'] = month_ret.Value.pct_change().fillna(0)
        max_rr_month = max(month_ret.ret)
        min_rr_month = min(month_ret.ret)
        # End of Natural month return
        date_begin = date_list[0]  # .date()
        date_end = date_list[-1]
        stat_dic = OrderedDict([('date_begen', date_begin),
                                ('date_end', date_end),
                                ('rr_tot', rr_tot),
                                ('rr_week', rr_week),
                                ('rr_month', rr_month),
                                ('rr_year', rr_year),
                                ('final_value', final_value),
                                ('min_value', min_value),
                                ('CAGR', CAGR),
                                ('ann_vol', ann_vol),
                                ('down_side_vol', down_side_vol),
                                ('mdd', mdd_size),
                                ('sharpe_ratio', sharpe_ratio),
                                ('sortino_ratio', sortino_ratio),
                                ('calmar_ratio', calmar_ratio),
                                ('profit_loss_ratio', profit_loss_ratio),  # 盈亏比
                                ('win_ratio', '%.2f' % win_ratio),  # 胜率
                                ('mdd_max_period', mdd_max_period),  # 最长不创新高周期数
                                ('freq', freq_str),  # 周期类型
                                ('max_ret', max_ret),  # 统计周期最大收益
                                ('min_ret', min_ret),  # 统计周期最大亏损
                                ('max_rr_month', max_rr_month),  # 最大月收益
                                ('min_rr_month', min_rr_month),  # 最大月亏损
                                ])
        stat_dic_dic[col_name if suffix_name is None else col_name + "_" + suffix_name] = stat_dic

    return stat_dic_dic


def return_risk_analysis(nav_df: pd.DataFrame, date_frm=None, date_to=None,
                         freq: Optional[str] = 'weekly', rf=0.02, suffix_name=None):
    """
    按列统计 rr_df 收益率绩效
    :param nav_df: 收益率DataFrame，index为日期，每一列为一个产品的净值走势
    :param date_frm: 统计日期区间，可以为空
    :param date_to: 统计日期区间，可以为空
    :param freq: None 自动识别, 'daily' 'weekly' 'monthly'
    :param rf: 无风险收益率，默认 0.02
    :return:
    """
    nav_sorted_df = nav_df.copy()
    nav_sorted_df.index = pd.to_datetime([try_2_date(idx) for idx in nav_sorted_df.index])
    nav_sorted_df.sort_index(inplace=True)
    # 计算数据实际频率是日频、周频、月頻
    data_count = nav_sorted_df.shape[0]
    day_per_data = (nav_sorted_df.index[data_count - 1] - nav_sorted_df.index[0]).days / data_count
    if day_per_data <= 0.008:
        freq_real = 'minute'
    elif day_per_data <= 0.2:
        freq_real = 'hour'
    elif day_per_data <= 2:
        freq_real = 'daily'
    elif day_per_data <= 10:
        freq_real = 'weekly'
    else:
        freq_real = 'monthly'
    if freq is None:
        freq = freq_real
    elif freq != freq_real:
        warnings_msg = "data freq wrong, expect %s, but %s was detected" % (freq, freq_real)
        # warnings.warn(warnings_msg)
        # logging.warning(warnings_msg)
        raise ValueError(warnings_msg)

    freq_str = ''
    if freq == 'weekly':
        data_count_per_year = 50
        freq_str = '周'
    elif freq == 'monthly':
        data_count_per_year = 12
        freq_str = '月'
    elif freq == 'daily':
        data_count_per_year = 250
        freq_str = '日'
    elif freq == 'hour':
        data_count_per_year = 1250
        freq_str = '时'
    elif freq == 'minute':
        data_count_per_year = 75000
        freq_str = '分'
    else:
        raise ValueError('freq=%s 只接受 daily weekly monthly 三种之一', freq)
    stat_dic_dic = OrderedDict()
    mon_rr_dic = {}
    if type(date_frm) is str:
        date_frm = datetime.strptime(date_frm, '%Y-%m-%d').date()
    if type(date_to) is str:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

    col_name_list = list(nav_sorted_df.columns)
    # date_col_name = col_name_list[0]
    # col_name_list = col_name_list[1:]
    for col_name in col_name_list:
        data_sub_df = nav_sorted_df[[col_name]].dropna()
        if data_sub_df.shape[0] == 0:
            continue
        rr_df = (1 + data_sub_df.pct_change().fillna(0)).cumprod()
        # rr_df.index = [try_2_date(d) for d in rr_df.index]
        data_df = rr_df.reset_index()
        data_df.columns = ['Date', 'Value']
        data_df = get_df_between_date(data_df, date_frm, date_to)
        data_df.Value = data_df.Value / data_df.Value[0]
        data_df['ret'] = data_df.Value.pct_change().fillna(0)
        date_span = data_df.Date[data_df.index[-1]] - data_df.Date[data_df.index[0]]
        date_span_fraction = 365 / date_span.days if date_span.days > 0 else 1
        # basic indicators
        CAGR = data_df.Value[data_df.index[-1]] ** date_span_fraction - 1
        period_rr = data_df.Value[data_df.index[-1]] - 1
        ann_vol = np.std(data_df.ret, ddof=1) * np.sqrt(data_count_per_year)
        down_side_vol = np.std(data_df.ret[data_df.ret < 0], ddof=1) * np.sqrt(data_count_per_year)
        # WeeksNum = data.shape[0]
        profit_loss_ratio = -np.mean(data_df.ret[data_df.ret > 0]) / np.mean(data_df.ret[data_df.ret < 0])
        win_ratio = len(data_df.ret[data_df.ret >= 0]) / len(data_df.ret)
        min_value = min(data_df.Value)
        final_value = data_df.Value[data_df.index[-1]]
        max_ret = max(data_df.ret)
        min_ret = min(data_df.ret)
        # End of basic indicators
        # max drawdown related
        data_df['mdd'] = data_df.Value / data_df.Value.cummax() - 1
        mdd_size = min(data_df.mdd)
        drop_array = pd.Series(data_df.index[data_df.mdd == 0])
        if len(drop_array) == 1:
            mdd_max_period = len(data_df.mdd)
        else:
            if float(data_df.Value[drop_array.tail(1)]) > float(data_df.Value.tail(1)):
                drop_array = drop_array.append(pd.Series(data_df.index[-1]))  # , ignore_index=True
            mdd_max_period = max(drop_array.diff().dropna()) - 1
        # End of max drawdown related
        # High level indicators
        sharpe_ratio = (CAGR - rf) / ann_vol
        sortino_ratio = (CAGR - rf) / down_side_vol
        calmar_ratio = CAGR / (-mdd_size)
        #  Natural month return
        j = 1
        for i in data_df.index:
            if i == 0:
                month_ret = pd.DataFrame([[data_df.Date[i], data_df.Value[i]]], columns=('Date', 'Value'))
            else:
                if data_df.Date[i].month != data_df.Date[i - 1].month:
                    month_ret.loc[j] = [data_df.Date[i - 1], data_df.Value[i - 1]]
                    j += 1
        month_ret.loc[j] = [data_df.Date[data_df.index[-1]], data_df.Value[data_df.index[-1]]]
        month_ret['ret'] = month_ret.Value.pct_change().fillna(0)
        max_rr_month = max(month_ret.ret)
        min_rr_month = min(month_ret.ret)
        # End of Natural month return
        data_len = data_df.shape[0]
        date_begin = data_df.Date[0]  # .date()
        date_end = data_df.Date[data_len - 1]
        stat_dic = OrderedDict([('起始日期', date_begin),
                                ('截止日期', date_end),
                                ('区间收益率', '%.2f%%' % (period_rr * 100)),
                                ('最终净值', '%.4f' % final_value),
                                ('最低净值', '%.4f' % min_value),
                                ('年化收益率', '%.2f%%' % (CAGR * 100)),
                                ('年化波动率', '%.2f%%' % (ann_vol * 100)),
                                ('年化下行波动率', '%.2f%%' % (down_side_vol * 100)),
                                ('最大回撤', '%.2f%%' % (mdd_size * 100)),
                                ('夏普率', '%.2f' % sharpe_ratio),
                                ('索提诺比率', '%.2f' % sortino_ratio),
                                ('卡马比率', '%.2f' % calmar_ratio),
                                ('盈亏比', '%.2f' % profit_loss_ratio),
                                ('胜率', '%.2f' % win_ratio),
                                ('最长不创新高（%s）' % freq_str, mdd_max_period),
                                ('统计周期最大收益', '%.2f%%' % (max_ret * 100)),
                                ('统计周期最大亏损', '%.2f%%' % (min_ret * 100)),
                                ('最大月收益', '%.2f%%' % (max_rr_month * 100)),
                                ('最大月亏损', '%.2f%%' % (min_rr_month * 100))])
        stat_dic_dic[col_name if suffix_name is None else col_name + "_" + suffix_name] = stat_dic

        # 按时间周期进行相关统计
        data_df = data_df.set_index('Date')[['Value']]
        # data_df_g = data_df.groupby(pd.Grouper(freq='M'))
        # TODO: 首月收益未被计算进去，以后再修复
        monthly_rr_df = data_df.resample('M', convention='end').last().pct_change().fillna(0)
        mon_rr_dic[col_name if suffix_name is None else col_name + "_" + suffix_name] = monthly_rr_df

    if len(stat_dic_dic) > 0:
        stat_df = pd.DataFrame(stat_dic_dic)
        stat_df = stat_df.loc[list(stat_dic.keys())]
    else:
        stat_df = None

    return stat_df, mon_rr_dic


def _calc_mdd_4_drawback_analysis(pair, y):
    """
    此函数仅供 drawback_analysis 使用
    用于计算最大回撤使用
    :param pair:
    :param y:
    :return:
    """
    max_y_last = pair[0]
    max_y = max_y_last if max_y_last > y else y
    mdd_last = pair[1]
    keep_max = pair[2]
    dd = y / max_y - 1
    if keep_max:
        mdd = dd if dd < mdd_last else mdd_last
    else:
        mdd = dd
    return max_y, mdd, keep_max


def drawback_analysis(data_df, keep_max=False):
    """
    计算给定 DataFrame 数据对应的时间序列最大回撤数据
    :param data_df:
    :return:
    """
    if data_df is None or data_df.shape[0] <= 1:
        mdd_df = None
    else:
        mdd_df = data_df.apply(
            lambda xx: [rr[1] for rr in reduce_list(_calc_mdd_4_drawback_analysis, xx, (xx.iloc[0], 0, keep_max))])
    return mdd_df


def return_risk_analysis_by_xls(file_path, date_col=None, nav_col_list=None, encoding=None):
    """
    读xls文件，对每个sheet进行分析，并最终合并绩效分析报告
    回撤分析分别生成文件显示
    :param file_path:
    :return:
    """
    file_path_no_extention, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.csv':
        is_csv_file = True
    else:
        is_csv_file = False
    if is_csv_file:
        sheet_names = ['sheet1']
    else:
        workbook = xlrd.open_workbook(file_path)
        sheet_names = workbook.sheet_names()

    sheet_mdd_df_dic = {}
    stat_df = None
    sheet_mon_rr_dic = {}
    for sheet_name in sheet_names:
        # if sheet_name not in col_names:
        #     continue
        try:
            index_col = 0
            if isinstance(date_col, str):
                if is_csv_file:
                    raise ValueError('csv 文件不支持 index_col 参数为字符串')
                sheet = workbook.sheet_by_name(sheet_name)
                # 取得日期索引后退出
                col_name = sheet.cell_value(0, index_col)
                while not (col_name is None or col_name == ""):
                    if col_name == date_col:
                        break
                    index_col += 1
                    col_name = sheet.cell_value(0, index_col)
            elif isinstance(date_col, int):
                index_col = date_col
            else:
                index_col = 0
            # 默认第0列为日期
            # sheetname Deprecated since version 0.21.0: Use sheet_name instead
            if is_csv_file:
                data_df = pd.read_csv(file_path, index_col=index_col, encoding=encoding)  # 某些版本使用 sheet_name
            else:
                data_df = pd.read_excel(file_path, index_col=index_col, sheet_name=sheet_name)  # 某些版本使用 sheet_name

            if data_df is None or data_df.shape[0] == 0:
                continue
            if nav_col_list is not None:
                data_df = data_df[nav_col_list]
            # 是否带suffix
            if re.search("[S|s]heet", sheet_name) is None:
                suffix_name = sheet_name
            else:
                suffix_name = None
            stat_df_tmp, mon_rr_dic = return_risk_analysis(data_df, freq=None,
                                                           suffix_name=suffix_name)  # , freq='daily'
            if stat_df is None:
                stat_df = stat_df_tmp
            else:
                stat_df = stat_df.merge(stat_df_tmp, how='outer', left_index=True, right_index=True)

            mdd_df = drawback_analysis(data_df)
            sheet_mdd_df_dic[sheet_name] = mdd_df
            sheet_mon_rr_dic[sheet_name] = mon_rr_dic
        except:
            logging.exception('处理 %s 时失败', sheet_name)
            continue
    return stat_df, sheet_mdd_df_dic, sheet_mon_rr_dic


if __name__ == "__main__":
    pass
    # logging.basicConfig(level=logging.DEBUG,
    #   format='%(asctime)s %(name)s|%(funcName)s:%(lineno)d %(levelname)s %(message)s')
    # logger = logging.getLogger()
    # # 基金绩效分析
    # from pandas.io.formats.excel import ExcelCell
    # file_path = r'd:\WSPych\fof_ams\Stage\periodic_task\analysis_cache\2016-6-1_2018-6-1\各策略指数走势_按机构.csv'
    # file_path_no_extention, _ = os.path.splitext(file_path)
    # stat_df, sheet_mdd_df_dic, sheet_mon_rr_dic = return_risk_analysis_by_xls(
    #   file_path, encoding='GBK')  # , date_col="日期", nav_col_list=['产品净值']
    # if stat_df is not None:
    #     stat_df.to_csv('%s_绩效统计.csv' % file_path_no_extention, encoding='GBK')
    # for sheet_name, mdd_df in sheet_mdd_df_dic.items():
    #     mdd_df.to_csv('%s_%s_最大回撤.csv' % (file_path_no_extention, sheet_name), encoding='GBK')
    # if len(sheet_mon_rr_dic) > 0:
    #     xls_file_path = '%s_%s_月度收益.xls' % (file_path_no_extention, sheet_name)
    #     writer = pd.ExcelWriter(xls_file_path)
    #     try:
    #         for sheet_name, mon_rr_dic in sheet_mon_rr_dic.items():
    #             start_row = 1
    #             for name, monthly_rr_df in mon_rr_dic.items():
    #                 year_set = {trade_date.year for trade_date in monthly_rr_df.index}
    #                 monthly_rr_matrix_df = pd.DataFrame(index=year_set, columns=range(1, 13))
    #                 for trade_date, rr_s in monthly_rr_df.T.items():
    #                     monthly_rr_matrix_df.loc[trade_date.year, trade_date.month] = '%2.2f%%' % (rr_s[0] * 100)
    #                 # 写 excel
    #                 # sheet.write(start_row, 0, name)
    #                 writer.write_cells([ExcelCell(0, 0, name)], sheet_name, startrow=start_row - 1)
    #                 monthly_rr_matrix_df.to_excel(writer, sheet_name, startrow=start_row)
    #                 start_row += len(year_set) + 3
    #     finally:
    #         writer.close()

    # 基金净值合并
    # file_list = [
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\复华1号历史净值180105(1).xls"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\历史净值171017.xls",
    #      'date_colum_name': '净值日期', 'nav_colum_name_list': ['最新净值']},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\新萌拟合后净值.xlsx",
    #      'date_colum_name': '日期', 'nav_colum_name_list': ['拟合后净值']},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\投放产品历史净值.csv",
    #      'date_colum_name': 'nav_date', 'nav_colum_name_list': ['nav_acc']},
    # ]

    # file_list = [
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\诚盛投资\诚盛2期Z期净值20171229nav.xlsx",
    #      'date_colum_name': '估值基准', 'nav_colum_name_list': [('单位净值',"诚盛2期Z期净值")]},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\诚盛投资\诚盛1期净值表.xlsx",
    #      'date_colum_name': '日期', 'nav_colum_name_list': ['诚盛1期净值']},
    # ]

    # file_list = [
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\合晟\合晟产品历史净值.csv"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\展弘\展弘投放产品历史净值.xlsx"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\新萌合并业绩后净值.xlsx"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\思勰\思勰合并后净值 2018 - 03 - 09.xls"},
    # ]
    #
    # file_list = [
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\思瑞二号周净值.xlsx',
    #      'date_colum_name': 'date', 'nav_colum_name_list': ['累计净值']},
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\2016.1-2016.10思勰净值.xlsx'},
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\思诚十二号周净值(1).xlsx',
    #      'date_colum_name': 'date', 'nav_colum_name_list': ['累计净值']},
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\SM2082-思瑞二号私募投资基金周净值(1).xls',
    #      'date_colum_name': '日期', 'nav_colum_name_list': ['累计净值']},
    # ]

    # nav_merged_df, nav_df, stat_df = merge_nav_from_file(file_list)
    # logging.info("\n%s", nav_merged_df)
    # logging.info("\n%s", nav_df)
    # logging.info("\n%s", stat_df)
    #
    # os.path.dirname(file_list[0]['file_path'])
    # folder_path = os.path.dirname(file_list[0]['file_path'])
    # file_name = "合并后净值.xls"
    # file_path = os.path.join(folder_path, file_name)
    # with pd.ExcelWriter(file_path) as writer:
    #     nav_merged_df.to_excel(writer, sheet_name="合并净值")
    #     nav_df.to_excel(writer, sheet_name="基金净值")
    #     stat_df.to_excel(writer, sheet_name="绩效统计")
    #     writer.save()
    # logging.info("输出文件：\n%s", file_path)
