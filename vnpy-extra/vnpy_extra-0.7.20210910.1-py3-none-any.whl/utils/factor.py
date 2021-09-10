"""
@author  : MG
@Time    : 2021/7/1 16:58
@File    : factor.py
@contact : mmmaaaggg@163.com
@desc    : 用于辅助生成因子及计算相关工具包
"""
from typing import Dict, Callable, Tuple, Union, List

import pandas as pd
from ibats_common.backend.factor import get_factor
from vnpy.trader.object import BarData


def generate_factors(hist_bar_list: List[BarData]):
    """整理缓存数据，生成相应的因子"""
    from vnpy_extra.utils.data import BAR_ATTRIBUTES
    df = pd.DataFrame(
        [{key: getattr(_, key) for key in BAR_ATTRIBUTES}
         for _ in hist_bar_list]).set_index('datetime')
    df.index = pd.to_datetime(df.index)

    # 生成因子
    factor_df = get_factor(
        df,
        ohlcav_col_name_list=['open_price', 'high_price', 'low_price', 'close_price', None, 'volume'],
        dropna=False
    )
    return df, factor_df


def generate_y_s(bar_df, target_n_bars=5, close_label='close', target_func: Union[str, Callable] = 'calc_total_return'):
    """根据bar_df生成目标序列"""
    if isinstance(target_func, str):
        y_s = bar_df[close_label].rolling(
            window=target_n_bars).apply(lambda x: getattr(x, target_func)()).iloc[
              target_n_bars:]  # calc_total_return calc_calmar_ratio
    elif callable(target_func):
        y_s = bar_df[close_label].rolling(
            window=target_n_bars).apply(lambda x: target_func(x)).iloc[
              target_n_bars:]  # calc_total_return calc_calmar_ratio
    else:
        raise ValueError(f"target_func={target_func} 无效")

    return y_s


TypingFactorFunc = Callable[[pd.DataFrame, Union[list, dict]], pd.Series]
TypingFuncParams = Union[Tuple[list, dict], list, dict]


def generate_x_df(
        bar_df: pd.DataFrame, factor_func_params_dic: Dict[TypingFactorFunc, List[TypingFuncParams]], dropna=True):
    """根据 bar_df 计算 factor_param_dic 对应的因子"""
    x_s_dic: Dict[str, pd.Series] = {}
    for factor_func, params_dic_list in factor_func_params_dic.items():
        for params_dic in params_dic_list:
            if isinstance(params_dic, tuple):
                args, kwargs = params_dic
            elif isinstance(params_dic, list):
                args, kwargs = params_dic, {}
            elif isinstance(params_dic, dict):
                args, kwargs = [], params_dic
            else:
                args, kwargs = [params_dic], {}

            label, x_s = factor_func(bar_df, *args, **kwargs)
            x_s_dic[label] = x_s

    x_df = pd.DataFrame(x_s_dic)
    if dropna:
        x_df.dropna(inplace=True)

    return x_df


if __name__ == "__main__":
    pass
