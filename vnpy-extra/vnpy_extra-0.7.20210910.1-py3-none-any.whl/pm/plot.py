#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/8/2 8:52
@File    : plot.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import logging
from collections import defaultdict
from typing import Dict, Callable, Optional, Set

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from vnpy_extra.constants import BASE_POSITION, STOP_OPENING_POS_PARAM
from vnpy_extra.db.orm import StrategyBacktestStats, set_account, AccountStrategyMapping, get_account, SymbolsInfo
from vnpy_extra.utils.symbol import get_vt_symbol_multiplier

logger = logging.getLogger(__name__)


def get_strategy_settings_by_account(stats: StrategyBacktestStats):
    return getattr(stats, 'strategy_settings_of_account', stats.strategy_settings)


def get_strategy_settings_by_default(stats: StrategyBacktestStats):
    return stats.strategy_settings


def log_contributes(rr_df: pd.DataFrame, key_vt_symbol_dic: Optional[dict] = None,
                    key_base_position_dic: Optional[dict] = None,
                    vt_symbol_market_value_dic: Optional[dict] = None,
                    vt_symbol_group_dic: Optional[dict] = None,
                    ):
    """日志记录收益率贡献"""
    rr_s = rr_df.iloc[:, -1]
    contribute_s: pd.Series = rr_s / np.sum(rr_s)
    # if key_base_position_dic:
    #     msg = '\n'.join([
    #         f"{num:2d}/{count:2d}) {key:130s} {_ * 100:5.2f}%    {key_base_position_dic.get(key, 0):2d}"
    #         for num, (key, _) in enumerate(contribute_s.items(), start=1)])
    #     logger.info(f"收益贡献度：\n       VT_SYMBOLS {' ' * 120}   PCT  BASE_POSITIONS\n{msg}")
    # else:
    #     msg = '\n'.join([
    #         f"{num:2d}/{count:2d}) {key:130s} {_ * 100:5.2f}%"
    #         for num, (key, _) in enumerate(contribute_s.items(), start=1)])
    #     logger.info(f"收益贡献度：\n       VT_SYMBOLS {' ' * 120}   PCT\n{msg}")
    if vt_symbol_group_dic is None:
        vt_symbol_group_dic = {}

    if key_vt_symbol_dic is None:
        key_vt_symbol_dic = {}

    if key_base_position_dic is None:
        key_base_position_dic = {}

    msg_df = pd.DataFrame([
        {
            "group_name": vt_symbol_group_dic.get(key_vt_symbol_dic.get(key, ''), '') if vt_symbol_group_dic else '',
            "vt_symbol": key_vt_symbol_dic.get(key, '') if key_vt_symbol_dic else '',
            "key": key,
            "贡献(%)": np.round(contribute * 100, 2),
            'base_position': key_base_position_dic.get(key, 0) if key_base_position_dic else 0,
        }
        for num, (key, contribute) in enumerate(contribute_s.items(), start=1)
    ])
    if not vt_symbol_group_dic:
        del msg_df['group_name']

    if not key_vt_symbol_dic:
        del msg_df['vt_symbol']

    if not key_vt_symbol_dic:
        del msg_df['vt_symbol']

    msg = msg_df.to_markdown()
    logger.info(f"收益贡献度：\n{msg}\n")

    if key_vt_symbol_dic:
        group = contribute_s.groupby(by=[key_vt_symbol_dic[key] for key in contribute_s.index])
        vt_symbol_contribute_df = pd.DataFrame(
            {
                'group_name': group.apply(lambda x: vt_symbol_group_dic.get(x.name, '') if vt_symbol_group_dic else ''),
                '贡献度(%)': group.sum().apply(lambda x: np.round(x * 100, 2)),
                'STG_COUNT': group.count()
            })
        vt_symbol_contribute_df.index.name = 'vt_symbol'
        vt_symbol_contribute_df = vt_symbol_contribute_df.reset_index()[
            ['group_name', 'vt_symbol', '贡献度(%)', 'STG_COUNT']
        ].sort_values(by=['group_name', 'vt_symbol']).reset_index(drop=True)
        if not vt_symbol_group_dic:
            del vt_symbol_contribute_df['group_name']

        if key_base_position_dic:
            vt_symbol_base_position_dic = defaultdict(int)
            for key, base_position in key_base_position_dic.items():
                if key in key_vt_symbol_dic:
                    vt_symbol_base_position_dic[key_vt_symbol_dic[key]] += base_position

            vt_symbol_contribute_df['base_positions'] = vt_symbol_contribute_df.apply(
                lambda x: vt_symbol_base_position_dic.get(x['vt_symbol'], 0), axis=1, )

        if vt_symbol_market_value_dic:
            market_value_s = vt_symbol_contribute_df.apply(
                lambda x: vt_symbol_market_value_dic.get(x['vt_symbol'], 0), axis=1, )
            vt_symbol_contribute_df['MV'] = market_value_s  # .apply(lambda x: f"{x:11,.0f}")
            tot_value = market_value_s.sum()
            if tot_value != 0:
                vt_symbol_contribute_df['MV(%)'] = np.round(market_value_s / tot_value * 100, 2)

        msg = vt_symbol_contribute_df.to_markdown(floatfmt="11,.2f")
        logger.info(f"按 vt_symbol 分组收益贡献度：\n{msg}\n")


def plot_with_weights(
        stats_list, weight_dic: dict, capital=None, legend=True, key_vt_symbol_dic: Optional[dict] = None,
        vt_symbol_market_value_dic: Optional[dict] = None, vt_symbol_group_dic: Optional[dict] = None, subplots=False
):
    key_stats_dic: Dict[str, StrategyBacktestStats] = {_.get_stats_key_str(): _ for _ in stats_list}
    if not key_vt_symbol_dic:
        key_vt_symbol_dic: Dict[str, str] = {_.get_stats_key_str(): _.symbols_info.symbols for _ in stats_list}

    key_df_dic = {key: stats.get_balance_df() for key, stats in key_stats_dic.items()}
    # profit_df = pd.DataFrame({key: df['profit'] for key, df in key_df_dic.items() if df is not None}).dropna()
    balance_df = pd.DataFrame({key: df['balance'] for key, df in key_df_dic.items() if df is not None}).ffill().dropna()
    rr_df = balance_df / balance_df.iloc[0, :]
    # for key, stats in key_stats_dic.items():
    #     if STOP_OPENING_POS_PARAM not in get_strategy_settings(stats):
    #         print(key, get_strategy_settings(stats))

    rr_sub_df = rr_df[[
        key for key, weight in weight_dic.items()
        if weight > 0.0001
    ]]
    if capital:
        profit_df = pd.DataFrame(
            {key: df['profit'] for key, df in key_df_dic.items() if df is not None}).ffill().dropna()
        profit_df = profit_df - profit_df.iloc[0, :]
        weighted_df = pd.DataFrame([
            profit_df[key] * weight
            for key, weight in weight_dic.items()
        ])
        log_contributes(weighted_df, key_vt_symbol_dic=key_vt_symbol_dic, key_base_position_dic=weight_dic,
                        vt_symbol_market_value_dic=vt_symbol_market_value_dic, vt_symbol_group_dic=vt_symbol_group_dic)
        result_s = weighted_df.sum(axis=0)
        rr_s = result_s / capital + 1
    else:
        weighted_df = pd.DataFrame([
            rr_sub_df[key] * weight
            for key, weight in weight_dic.items()
        ])
        log_contributes(weighted_df, key_vt_symbol_dic=key_vt_symbol_dic, key_base_position_dic=weight_dic,
                        vt_symbol_market_value_dic=vt_symbol_market_value_dic, vt_symbol_group_dic=vt_symbol_group_dic)
        result_s = weighted_df.sum(axis=0)
        rr_s = result_s / result_s.iloc[0]

    rr_s.name = 'nav'

    if subplots:
        rr_sub_df.insert(0, 'nav', rr_s)
        rr_sub_df.plot(grid=True, legend=legend, figsize=(12, rr_sub_df.shape[1] * 4), subplots=subplots)
        plt.show()
    else:
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 24))
        axes = axes.flatten()
        rr_sub_df.plot(grid=True, ax=axes[0], legend=legend)
        rr_s.plot(grid=True, ax=axes[1], legend=legend)
        plt.show()


def plot_with_base_position(
        stats_list,
        get_strategy_settings_func: Callable[[StrategyBacktestStats], dict] = get_strategy_settings_by_default,
        *,
        log_weights=False,
        legend=True,
        capital=None,
        **kwargs
):
    """根据权重合并 profit plot 出合并后的 profit 曲线"""
    key_base_positions_dic: Dict[str, int] = {
        _.get_stats_key_str(): int(get_strategy_settings_func(_).get(BASE_POSITION, 1))
        for _ in stats_list if not get_strategy_settings_func(_).get(STOP_OPENING_POS_PARAM, 0)}
    key_vt_symbol_dic: Dict[str, str] = {
        _.get_stats_key_str(): _.symbols_info.symbols for _ in stats_list}
    if log_weights:
        for key, base_position in key_base_positions_dic.items():
            logging.info(f"{key:150s}{base_position:3d}")
    symbols: Set[str] = {_.symbols_info.symbols.split('.')[0] for _ in stats_list}
    vt_symbol_price_dic = SymbolsInfo.get_vt_symbol_latest_price_dic(symbols)
    if not kwargs.get('vt_symbol_market_value_dic', None):
        vt_symbol_market_value_dic = {}
        for key, base_positions in key_base_positions_dic.items():
            vt_symbol = key_vt_symbol_dic[key]
            vt_symbol_market_value_dic[vt_symbol] = (
                    vt_symbol_price_dic[vt_symbol.upper()] * get_vt_symbol_multiplier(vt_symbol) * base_positions)
        kwargs["vt_symbol_market_value_dic"] = vt_symbol_market_value_dic

    kwargs.setdefault("weight_dic", key_base_positions_dic)
    plot_with_weights(stats_list=stats_list, legend=legend, capital=capital, **kwargs)


def _test_plot_with_weights():
    # user_name, broker_id = "11859087", "95533"
    user_name, broker_id = "721018", "1025"
    set_account(user_name, broker_id)
    stats_list = AccountStrategyMapping.get_stats_by_account(
        user_name, broker_id)
    plot_with_base_position(stats_list, get_strategy_settings_func=get_strategy_settings_by_account, legend=False)


def plot_by_account(user_name=None, broker_id=None, description=None, capital=3_000_000, **kwargs):
    stats_list = AccountStrategyMapping.get_stats_by_account(
        user_name=user_name, broker_id=broker_id, available_only=True)
    user_name, broker_id = get_account()
    logger.info(f"{user_name}[{broker_id}] {description if description else ''} 组合资金曲线")
    kwargs.setdefault('legend', False)
    plot_with_base_position(stats_list, capital=capital, **kwargs)


def _test_plot_by_account():
    plot_by_account(user_name="11859087", broker_id="95533", description="建信")


if __name__ == "__main__":
    # _test_plot_with_weights()
    _test_plot_by_account()
