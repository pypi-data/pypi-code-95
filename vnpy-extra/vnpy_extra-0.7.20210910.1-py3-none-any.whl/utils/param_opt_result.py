"""
@author  : MG
@Time    : 2020/9/23 8:33
@File    : param_opt_result.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import os
import json
from typing import Callable, Optional

import pandas as pd
import numpy as np
import re
from collections import defaultdict, Counter
from itertools import product

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def calc_opt_params_by_weight(
        result_df: pd.DataFrame,
        weight_key='value',
        filter_func: Optional[Callable] = None,  # lambda x: x > 1
        use_result_df_if_filtered_is_0=True,
        ignore_quantile_over=0.95,
        ignore_quantile_under=0.05,
):
    """
    根据参数优化结果挑选出最优参数
    param: result_df 优化结果
    param: weight_key 计算最优参数的权重 column 名称
    param: filter_func 筛选有效参数
    param: ignore_quantile_over 分位数以上结果至今忽略
    return: param_dic 最优化参数
    """
    filtered_df = result_df
    # 根据 qunatile 过滤数据
    if ignore_quantile_over is not None and ignore_quantile_over > 0:
        value_over = filtered_df[weight_key].quantile(q=ignore_quantile_over)
    else:
        value_over = None

    if ignore_quantile_under is not None and ignore_quantile_under > 0:
        value_under = filtered_df[weight_key].quantile(q=ignore_quantile_under)
    else:
        value_under = None

    if value_over is not None:
        filtered_df = filtered_df[filtered_df[weight_key] < value_over]

    if value_under is not None:
        filtered_df = filtered_df[filtered_df[weight_key] > value_under]

    # 过滤出有效参数（例如：calmar > 1）
    if filter_func is not None:
        filtered_df = filtered_df[filtered_df[weight_key].apply(filter_func)]

    if use_result_df_if_filtered_is_0 and filtered_df.shape[0] == 0:
        logger.warning('当前结果过滤后数据为0，忽略过滤条件，filtered_df.shape=%s', filtered_df.shape)
        pass
    elif filtered_df.shape[0] > 0:
        result_df = filtered_df
    else:
        # use_result_df_if_filtered_is_0 == False and filtered_df.shape == 0
        # 无法继续优化，直接返回
        logger.warning('当前结果过滤后数据为0，无法进行优化')
        return None

    # 计算每一个参数的权重
    param_cum_weight = defaultdict(lambda: defaultdict(lambda: 0))
    param_list = [_ for _ in result_df.columns if _ != weight_key]
    available_params_set = set()
    for param_dic in result_df.to_dict('record'):
        available_params_set.add(tuple([(_, param_dic[_]) for _ in param_list]))
        for param, value in param_dic.items():
            if param == weight_key:
                continue

            param_cum_weight[param][value] += param_dic[weight_key]

    # 根据各个参数权重的顺序寻找到最优参数组合
    params_weight_dic = {}
    for params in product(*[list(param_cum_weight[_].keys()) for _ in param_list]):
        # print(params)
        params_weight_list = []
        for n, param_name in enumerate(param_list):
            params_weight_list.append(param_cum_weight[param_name][params[n]])

        params_weight_dic[params] = np.sum([params_weight_list])

    sorted_s = pd.Series(params_weight_dic).sort_values(ascending=False)
    for params in sorted_s.index:
        available_params = tuple([(_, params[n]) for n, _ in enumerate(param_list)])
        # print(available_params)
        if available_params in available_params_set:
            break
    else:
        available_params = None

    # 对每一个参数按权重从大到小排序
    # param_weighted_value_dic = {}
    # max_len = 0
    # for param, value_weight_dic in param_cum_weight.items():
    #     s = pd.Series(value_weight_dic).sort_values(ascending=False)
    #     max_len = max(max_len, s.shape[0])
    #     param_weighted_value_dic[param] = {
    #         'index': -1, 'index_max': s.shape[0] - 1, "values": s}

    # available_params = None
    # for n in range(max_len):
    #     has_next = True
    #     while has_next:
    #         result_params = {}
    #         changed = False  # 记录本轮循环是否存在参数的改变
    #         for param, weighted_value_dic in param_weighted_value_dic.items():
    #             if weighted_value_dic['index'] == -1:
    #                 weighted_value_dic['index'] = index = 0
    #                 changed = True
    #             elif (not changed) and weighted_value_dic['index'] < n <= weighted_value_dic['index_max']:
    #                 weighted_value_dic['index'] = index = weighted_value_dic['index'] + 1
    #                 changed = True
    #             else:
    #                 index = weighted_value_dic['index']
    #
    #             result_params[param] = weighted_value_dic['values'].index[index]
    #
    #         # 已经找不到更多的参数组合了
    #         if not changed:
    #             available_params = None
    #             break
    #
    #         # 查找参数是否在有效的列表中
    #         available_params = tuple([(_, result_params[_]) for _ in param_list])
    #         if available_params in available_params_set:
    #             # 找到合适的参数，退出 while
    #             break
    #         else:
    #             # 没有找到合适的，再次查找
    #             pass
    #
    #     else:
    #         # 循环结束，没有找到合适的参数
    #         available_params = None
    #
    #     if available_params is not None:
    #         break
    # else:
    #     logger.warning("没有找到合适的参数")
    #     available_params = None

    if available_params is not None:
        param_dic = {k: v for k, v in available_params}
    else:
        param_dic = None

    return param_dic


def _test_calc_opt_params_by_weight():
    result_df = pd.read_csv(
        r'd:\github\quant_vnpy\strategies\trandition\period_resonance_macd_kdj\period_resonance_macd_kdj_rb9999_2018-10-08.csv',
        encoding='GBK'
    )
    param_dic = calc_opt_params_by_weight(
        result_df, filter_func=None)
    print("最优参数:", param_dic)
    param_dic = calc_opt_params_by_weight(
        result_df,
        filter_func=lambda x: x > 10)
    print("最优参数:", param_dic)
    param_dic = calc_opt_params_by_weight(
        result_df,
        filter_func=lambda x: x > 10,
        use_result_df_if_filtered_is_0=False)
    assert param_dic is None
    print("没有最优参数")


def load_results(results: list, encoding='GBK', key=None, output_file_path=None):
    """
    加载参数优化后的结果，对参数项进行整理成为新的 csv文件
    """
    data_list = []
    for param_str, value, stat in results:
        dic = json.loads(re.sub("'", '"', param_str))
        dic['value'] = value
        data_list.append(dic)

    result_df = pd.DataFrame(data_list)
    if key is not None:
        result_df['key'] = key

    result_df.sort_values(by='value', ascending=False, inplace=True)
    if output_file_path is not None:
        result_df.to_csv(output_file_path, encoding=encoding, index=False)

    return result_df


def load_csv_file(file_path: str, encoding='GBK', key=None, output_csv=True):
    """
    加载参数优化后保存的csv文件，对参数项进行整理成为新的 csv文件
    """
    param_column_name = '参数'
    df = pd.read_csv(file_path, encoding=encoding)
    columns = set(df.columns)
    columns.remove(param_column_name)
    column_name = list(columns)[0]
    data_list = []
    for _, row_s in df.iterrows():
        param_str = row_s.pop(param_column_name)
        dic = json.loads(re.sub("'", '"', param_str))
        dic[column_name] = row_s[column_name]
        data_list.append(dic)

    result_df = pd.DataFrame(data_list)
    if key is not None:
        result_df['key'] = key

    if output_csv:
        file_name, _ = os.path.splitext(file_path)
        result_df.to_csv(f'{file_name}_df.csv', encoding=encoding, index=False)

    return result_df


def _test_to_csv():
    file_path = r'd:\github\quant_vnpy\strategies\trandition\double_ma\double_ma_strategy.csv'
    result_df = load_csv_file(file_path, key='I')
    assert result_df.shape[1] > 2


def merge_csv_files(key_path_dic: dict, encoding='GBK', output_csv=True):
    """
    将多个csv进行整理合并
    """
    df_list = []
    file_path = None
    for key, file_path in key_path_dic.items():
        df_list.append(load_csv_file(
            file_path, encoding=encoding, key=key, output_csv=output_csv))

    new_df = pd.concat(df_list)
    if output_csv:
        new_file_path = f"{os.path.splitext(file_path)[0]}_all.csv"
        new_df.to_csv(new_file_path, encoding=encoding)
        logger.info("输出合并后文件：%s", new_file_path)

    return new_df


def _test_merge_csv_files():
    dir_path = r'd:\github\quant_vnpy\strategies\trandition\period_resonance_macd_kdj'
    key_path_dic = {
        'rb': os.path.join(dir_path, r'period_resonance_macd_kdj.csv'),
        'i': os.path.join(dir_path, r'period_resonance_macd_kdj_I_ML.csv'),
    }
    merge_csv_files(key_path_dic)


def find_general_params(key_path_dic, group_by: list, filter_func: Callable, intersection_keys: list = None, most_n=10):
    """
    :param key_path_dic 品种，路径字典
    :param group_by group by 哪一些字段 是一个 list
    :param filter_func 过滤条件
    :param intersection_keys 统计交集的参数字段
    :param most_n 统计 top n 被常用参数
    """
    instrument_types = list(key_path_dic.keys())
    counter = Counter()
    merged_df = merge_csv_files(key_path_dic, output_csv=True)
    score_column_name = merged_df.columns[-2]
    if filter_func is not None:
        logger.debug('score_column_name:%s', score_column_name)
        fit = merged_df[score_column_name].apply(filter_func)
        merged_df = merged_df[fit]

    period_key_set_dic = {}
    period_key_score_dic = defaultdict(dict)
    for g_key, sub_df in merged_df.groupby(group_by):
        # 按照 group_by 分钟
        key_set_dic = defaultdict(set)
        for key, key_sub_df in sub_df.groupby('key'):
            # 根据 key 为每一个 子集 建立参数集合
            for _, row in key_sub_df.iterrows():
                # 对每一项进行整理并加入统计结果
                data = []
                for _ in row.index:
                    if _ == 'key' or _ in group_by or _ == score_column_name:
                        continue
                    if intersection_keys is not None and _ not in intersection_keys:
                        continue
                    data.append(_)
                    data.append(row[_])

                params = tuple(data)
                key_set_dic[key].add(params)
                period_key_score_dic[(g_key, key)][params] = row[score_column_name]

        label = ','.join([f'{_[0]}={_[1]}' for _ in zip(group_by, g_key)])
        if len(key_set_dic) == 0:
            logger.warning("%s 没有可供交集的 参数集", label)
            continue
        period_key_set_dic[g_key] = key_set_dic
        # 进行计数，统计使用次数
        for _ in key_set_dic.values():
            counter += Counter(_)

        available_keys = list(key_set_dic.keys())
        if len(available_keys) == 1:
            available_key = available_keys[0]
            logger.warning(
                "%s 只有 %s 有可用参数 %d 个",
                label, available_key, len(key_set_dic[available_key])
            )
            continue

        set_list = [key_set_dic[_] for _ in available_keys]
        intersections = set_list[0].intersection(*set_list[1:])
        intersection_count = len(intersections)
        if intersection_count == 0:
            logger.warning("%s 在 %s 上有 没有交集", label, available_keys)
        else:
            logger.info(
                "%s 在 %s 上有 %d 个交集，包括：\n%s",
                label, available_keys, intersection_count,
                '\n'.join([str(_) for _ in intersections])
            )

    logger.info("最长被使用的 %d 个参数：", most_n)
    for value, count in counter.most_common(most_n):
        logger.info("%2d 次被使用，%s", count, value)

    if len(group_by) == 2:
        # 只有当 group_by 长度为 2是才可以将其二维表格化
        for instrument_type in instrument_types:
            m_n_score_list = []
            for (period_m, period_n), key_set_dic in period_key_set_dic.items():
                param_set = key_set_dic[instrument_type]
                for param, _ in counter.most_common(len(counter)):
                    if param in param_set:
                        break
                else:
                    raise ValueError(f"没有找到任何参数在 param_set={param_set}")

                logger.debug("period_m=%s, period_n=%s 使用参数 %s", period_m, period_n, param)
                m_n_score_list.append({
                    "period_m": period_m,
                    "period_n": period_n,
                    "score": period_key_score_dic[((period_m, period_n), instrument_type)][param]
                })

            df = pd.DataFrame(m_n_score_list).pivot(index="period_m", columns="period_n", values='score')
            df.to_csv(f"{instrument_type}_period_score.csv")
            logger.info("%s score:\n%s", instrument_type, df)


def _test_find_general_params():
    dir_path = r'd:\github\quant_vnpy\strategies\trandition\period_resonance_macd_kdj'
    key_path_dic = {
        'rb': os.path.join(dir_path, r'period_resonance_macd_kdj_rb.csv'),
        'i': os.path.join(dir_path, r'period_resonance_macd_kdj_i.csv'),
    }
    group_by = ["period_m", "period_n"]
    intersection_keys = ["fast_window_m", "slow_window_m", "signal_period_m"]
    find_general_params(key_path_dic, group_by, lambda x: float(x) > 1, intersection_keys=intersection_keys)


if __name__ == "__main__":
    # _test_to_csv()
    # _test_merge_csv_files()
    # _test_find_general_params()
    _test_calc_opt_params_by_weight()
