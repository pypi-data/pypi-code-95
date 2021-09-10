"""
@author  : MG
@Time    : 2021/7/21 15:06
@File    : optimization.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import List, Set, Dict, Optional, Tuple

import cvxpy
import numpy as np
import pandas as pd
from ibats_utils.transfer import str_2_date, date_2_str
from pypfopt import EfficientFrontier, risk_models, expected_returns, DiscreteAllocation
from pypfopt.black_litterman import BlackLittermanModel, market_implied_risk_aversion, market_implied_prior_returns
from pypfopt.exceptions import OptimizationError

from vnpy_extra.backtest import InstrumentClassificationEnum
from vnpy_extra.constants import DEFAULT_CAPITAL
from vnpy_extra.db.export_strategy_setting import generate_strategy_setting_file
from vnpy_extra.db.orm import SymbolsInfo, AccountStrategyMapping, StrategyBacktestStats, set_account
from vnpy_extra.pm.plot import plot_with_weights, plot_by_account
from vnpy_extra.utils.symbol import get_vt_symbol_multiplier, get_instrument_type

logger = logging.getLogger(__name__)


class PortfolioOptimizeGoalEnum(Enum):
    max_sharpe = 'max_sharpe'
    min_volatility = 'min_volatility'
    max_quadratic_utility = 'max_quadratic_utility'
    black_litterman = 'black_litterman'
    equal_mdd = 'equal_mdd'


@dataclass
class FittingInstrumentGroup:
    name: str
    instrument_set: set
    weights: float
    goal: PortfolioOptimizeGoalEnum
    solver: str
    kwargs: dict

    @staticmethod
    def create_by_instrument_classification_enum(
            inst_enum: InstrumentClassificationEnum,
            weights,
            goal: PortfolioOptimizeGoalEnum,
            solver: str = 'ECOS',
            **kwargs
    ):
        return FittingInstrumentGroup(
            inst_enum.name,
            inst_enum.value,
            weights,
            goal,
            solver,
            kwargs
        )


def calc_most_drawdown(drawdown_s: pd.Series):
    """根据回撤数据计算毛回撤"""
    drawdown_sub_s: pd.Series = drawdown_s[drawdown_s < 0]
    most_drawdown = drawdown_sub_s.mean() - drawdown_sub_s.std() * 2
    return most_drawdown


def fit_df(
        rr_df: pd.DataFrame, name,
        goal: PortfolioOptimizeGoalEnum, weight=1.0, solver='ECOS', start_date=None, end_date=None, **kwargs) -> dict:
    """对制定 stats_list 进行优化，返回优化够相应权重 dict """
    if rr_df.shape[1] <= 1:
        key_weight_dic = {key: weight for key in rr_df.columns}
        return key_weight_dic

    key_weight_dic = {}
    if goal == PortfolioOptimizeGoalEnum.equal_mdd:
        data_df = rr_df * DEFAULT_CAPITAL
        indicator = kwargs.get('equal_mdd_indicator', "max_drawdown")
        if indicator == "max_drawdown":
            # noinspection PyUnresolvedReferences
            import ffn  # NOQA
            key_mdd_dic = data_df.calc_max_drawdown().to_dict()
        elif indicator == "most_drawdown":
            drawdown_df: pd.DataFrame = data_df - data_df.expanding().max()
            key_mdd_dic = drawdown_df.apply(calc_most_drawdown).to_dict()

        # key_mdd_dic = {
        #     key: _.indicator_dic.get("daily_stats_dic", {}).get(indicator, None)
        #     for key, _ in key_stats_dic.items()
        #     if (key in key_set and _.indicator_dic and
        #         _.indicator_dic.get("daily_stats_dic", {}).get(indicator, None) is not None)
        # }
        # benchmark_capital 该参数对结果没有影响
        benchmark_capital = 100_000
        _key_weight_dic = {key: benchmark_capital / np.abs(v) for key, v in key_mdd_dic.items()}
        tot_weight = sum(_key_weight_dic.values())
        _key_weight_dic = {key: _weight / tot_weight * weight for key, _weight in _key_weight_dic.items()}
        key_weight_dic.update(_key_weight_dic)

    elif goal == PortfolioOptimizeGoalEnum.black_litterman:
        cov_matrix = risk_models.sample_cov(rr_df)
        mcaps = rr_df.iloc[-1, :]
        delta = market_implied_risk_aversion(rr_df, risk_free_rate=0).to_numpy()
        # delta = None
        prior = market_implied_prior_returns(mcaps, delta, cov_matrix).to_numpy(dtype='float')

        # 作为简单解决方案，自动优化生成 absolute view
        count = rr_df.shape[1]
        mu = expected_returns.mean_historical_return(rr_df)
        cov_matrix = risk_models.sample_cov(rr_df)
        # Optimize for maximal Sharpe ratio
        ef = EfficientFrontier(
            mu, cov_matrix,
            weight_bounds=kwargs.get('weight_bounds', (0, 0.3) if count > 4 else (0, 1)),
            solver=solver)
        absolute_views = ef.min_volatility()
        bl = BlackLittermanModel(
            cov_matrix, absolute_views=absolute_views,
            # pi='equal',
            # pi='market', market_caps=mcaps.to_dict()
            pi=prior
        )
        # rets = bl.bl_returns()
        # ef = EfficientFrontier(rets, cov_matrix)
        # OR use return-implied weight
        raw_weights = bl.bl_weights(delta)
        # clean_weights = bl.clean_weights()
        _key_weight_dic = {
            key: _weight * weight
            # for key, weight in ef.clean_weights().items()
            for key, _weight in (raw_weights if raw_weights else ef.clean_weights()).items()
        }
        # for num, (key, weight) in enumerate(raw_weights.items(), start=1):
        #     logger.info(f"{num:2d}) {key_vt_symbol_dic[key]:11s} {key:130s} --> {weight * 100:.2f}%")

    else:
        count = rr_df.shape[1]
        mu = expected_returns.mean_historical_return(rr_df)
        cov_matrix = risk_models.sample_cov(rr_df)
        # Optimize for maximal Sharpe ratio
        ef = EfficientFrontier(
            mu, cov_matrix,
            weight_bounds=kwargs.get('weight_bounds', (0, 0.3) if count > 4 else (0, 1)),
            solver=solver)
        try:
            raw_weights = getattr(ef, goal.value)()
        except OptimizationError as exp:
            logger.error(f"{name}[{rr_df.shape[0]}] {goal} solver={solver} 优化异常")
            raise exp from exp
        # ef.save_weights_to_file("weight.csv")  # saves to file
        # ef.portfolio_performance(verbose=True)  #
        _key_weight_dic = {
            key: _weight * weight
            # for key, weight in ef.clean_weights().items()
            for key, _weight in (raw_weights if raw_weights else ef.clean_weights()).items()
        }
        key_weight_dic.update(_key_weight_dic)
        # logger.info(f"{name} has {len(raw_weights)} keys")
        # for num, (key, weight) in enumerate(raw_weights.items(), start=1):
        #     logger.info(f"{num:2d}) {key_vt_symbol_dic[key]:11s} {key:130s} --> {weight * 100:.2f}%")

    for key, weight in _key_weight_dic.items():
        if weight < 0:
            raise ValueError(f"{key} weight={weight:.4f} 不允许负权重持仓。请尝试其他方法。")

    return key_weight_dic


def fit_and_merge_key_stats_dic(
        key_stats_dic: Dict[str, StrategyBacktestStats], name, *,
        goal: PortfolioOptimizeGoalEnum, weight=1.0, solver='ECOS', start_date=None, end_date=None,
        group_by_vt_symbol=False, group_by_vt_symbol_kwargs: Optional[dict] = None, **kwargs
) -> Tuple[dict, pd.Series]:
    """对制定 stats_list 进行优化，返回优化够相应权重 dict """
    vt_symbol_key_weight_dic: Dict[str, Dict[str, float]] = {}
    vt_symbol_rr_s_dic: Dict[str, pd.Series] = {}
    if group_by_vt_symbol:
        # 按合约进行 fitting
        # 整理参数
        if group_by_vt_symbol_kwargs is None:
            group_by_vt_symbol_kwargs = {}

        # 整理 vt_symbol key_key_stats 对照关系
        vt_symbol_key_key_stats_dic = defaultdict(dict)
        for key, stats in key_stats_dic.items():
            vt_symbol_key_key_stats_dic[stats.symbols_info.symbols][key] = stats

        # 按合约进行 fitting
        for vt_symbol, _key_stats_dic in vt_symbol_key_key_stats_dic.items():
            if vt_symbol in group_by_vt_symbol_kwargs:
                _kwargs = group_by_vt_symbol_kwargs[vt_symbol]
            else:
                _kwargs = group_by_vt_symbol_kwargs.get('default', {})

            if len(_kwargs) == 0:
                _kwargs.setdefault('goal', goal)
                _kwargs.setdefault('solver', solver)
                _kwargs.setdefault('start_date', start_date)
                _kwargs.setdefault('end_date', end_date)
                _kwargs.setdefault('weight', 1.0)
                for param, val in kwargs.items():
                    _kwargs.setdefault(param, val)

            _key_weight_dic, _rr_s = fit_and_merge_key_stats_dic(_key_stats_dic, name=vt_symbol, **_kwargs)
            vt_symbol_key_weight_dic[vt_symbol] = _key_weight_dic
            vt_symbol_rr_s_dic[vt_symbol] = _rr_s

        # 整理 fitting 后的收益率曲线
        rr_df = pd.DataFrame(vt_symbol_rr_s_dic).sort_index().ffill().dropna()
    else:
        key_rr_s_dic: Dict[str, pd.Series] = {key: _.get_rr_s() for key, _ in key_stats_dic.items()}
        rr_df = pd.DataFrame({
            key: rr_s for key, rr_s in key_rr_s_dic.items() if rr_s is not None
        }).sort_index().ffill().dropna()

    # 将 rr_df 其实点回归 1 起始点
    rr_df -= (rr_df.iloc[0, :] - 1)

    # start_date， end_date参数仅用于 fitting，合并曲线是依然适用全量数据
    fit_rr_df = rr_df
    if start_date:
        fit_rr_df = fit_rr_df[fit_rr_df.index >= pd.to_datetime(start_date)]
    if end_date:
        fit_rr_df = fit_rr_df[fit_rr_df.index <= pd.to_datetime(end_date)]

    # 将 rr_df 其实点回归 1 起始点
    fit_rr_df -= (fit_rr_df.iloc[0, :] - 1)

    _key_weight_dic = fit_df(fit_rr_df, name, goal, weight, solver, **kwargs)
    pct_df = pd.DataFrame({
        key: rr_df[key].pct_change().fillna(0) * _weight for key, _weight in _key_weight_dic.items()
    })
    rr_s: pd.Series = (pct_df.sum(axis=1) + 1).cumprod()
    rr_s.name = name

    if group_by_vt_symbol:
        # 将权重综合计算
        key_weight_dic = {
            key: weight_key * weight_vt_symbol
            for vt_symbol, weight_key in _key_weight_dic.items()
            for key, weight_vt_symbol in vt_symbol_key_weight_dic[vt_symbol].items()}
    else:
        key_weight_dic = _key_weight_dic

    return key_weight_dic, rr_s


@dataclass
class FittingKeysGroup:
    name: str
    key_set: Set[str]
    weights: float
    goal: PortfolioOptimizeGoalEnum
    solver: str
    kwargs: dict


class PortfolioOptimization:

    def __init__(self, stats_list: List[StrategyBacktestStats], shown_corr_plot=False, curr_symbol_only=True, **kwargs):
        self.key_stats_dic: Dict[str, StrategyBacktestStats] = {_.get_stats_key_str(): _ for _ in stats_list}
        # 有效策略列表筛选逻辑
        # 1）非冻结状态的策略
        # 2）主力合约
        self.available_keys = {
            key for key, _ in self.key_stats_dic.items()
            if (not _.get_freeze_of_account()
                and (not curr_symbol_only or
                     SymbolsInfo.get_or_create_curr_symbols(_.symbols_info.symbols).symbols == _.symbols_info.symbols))
        }
        # 目前仅考虑 CTA 的情况
        self.key_vt_symbol_dic: Dict[str, str] = {
            key: _.symbols_info.symbols for key, _ in self.key_stats_dic.items()}
        self.key_multiplier_dic = {
            key: get_vt_symbol_multiplier(_.symbols_info.symbols) for key, _ in self.key_stats_dic.items()}
        self.key_balance_df_dic: Dict[str, pd.DataFrame] = {
            key: _.get_balance_df() for key, _ in self.key_stats_dic.items()
            if key in self.available_keys
        }
        date_range_df = pd.DataFrame({
            key: [df.index.min(), df.index.max(), df.index.max() - df.index.min()]
            for key, df in self.key_balance_df_dic.items() if df is not None}, index=['start', 'end', 'range']).T
        min_range_s = date_range_df.iloc[date_range_df['range'].argmin(), :]
        self.profit_df = pd.DataFrame({
            key: df['profit']
            for key, df in self.key_balance_df_dic.items() if df is not None}).dropna().astype(float)
        ef = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(
            f"共 {len(stats_list)} 条数据，最短策略周期 {min_range_s['range'].days}：\n"
            f"{min_range_s.name} {date_2_str(min_range_s['start'])} - {date_2_str(min_range_s['end'])}")
        self.goal = None
        self.key_weight_dic: Optional[Dict] = None
        # key 与 group_name 对应关系，用于进行排序显示日志使用
        self.key_group_dic = {}
        # vt_symbol 与 group_name 对应关系，用于进行排序显示日志使用
        self.vt_symbol_group_dic = {}
        self._kwargs = kwargs
        self.group_weight_dic: Optional[Dict[InstrumentClassificationEnum, float]] = None
        self.auto_merge_into_other_group_if_lower_than = 1
        self.max_vt_symbol_weight = None
        self.start_date = None
        self.end_date = None
        self.solver = cvxpy.ECOS
        if shown_corr_plot:
            import seaborn as sns
            import matplotlib.pyplot as plt
            corr = self.profit_df.corr()
            sns.heatmap(corr, vmax=1, vmin=-1, center=0)
            plt.show()

    def set_goal(self, goal, *, solver=cvxpy.ECOS,
                 fit_by_group: Optional[Dict[InstrumentClassificationEnum, float]] = None,
                 max_vt_symbol_weight=None, start_date=None, end_date=None, **kwargs):
        self.goal = goal
        self.solver = solver
        self.group_weight_dic: Optional[Dict[InstrumentClassificationEnum, float]] = fit_by_group
        self.max_vt_symbol_weight = max_vt_symbol_weight
        self.start_date = start_date
        self.end_date = end_date
        self._kwargs.update(kwargs)

    def fit(self):
        if self._kwargs.get('output_balance_df', False):
            balance_df = pd.DataFrame({
                key: df['balance']
                for key, df in self.key_balance_df_dic.items() if df is not None})
            # rr_s = balance_df / balance_df.iloc[0, :]
            balance_df.to_csv(f"balance_df.csv")

        if self.group_weight_dic:
            # 分组计算权重
            group_keys_dic = {}
            group_merged_key_set = {}
            min_group = None
            for group, weight in list(self.group_weight_dic.items()):
                # 仅对当期主力合约进行优化
                key_set = set([
                    key for key, vt_symbol in self.key_vt_symbol_dic.items()
                    if (SymbolsInfo.get_or_create_curr_symbols(vt_symbol).symbols == vt_symbol
                        and key in self.key_balance_df_dic
                        and get_instrument_type(vt_symbol).upper() in group.value)
                ])
                key_count = len(key_set)
                if key_count == 0:
                    self.group_weight_dic.pop(group)
                    self.logger.warning(f"{group.name} has {key_count} key. ignored.")
                    continue
                elif key_count == 1 and self.auto_merge_into_other_group_if_lower_than <= 0:
                    raise ValueError(f"{group.name} has only on key '{key_set.pop()}'")
                elif key_count <= self.auto_merge_into_other_group_if_lower_than:
                    self.logger.warning(f"{group.name} has {key_count} keys too small to be optimized.")
                    group_merged_key_set[group] = (key_set, weight)
                else:
                    group_keys_dic[group] = key_set
                    if not min_group or len(group_keys_dic[min_group]) > key_count:
                        min_group = group

            if len(group_merged_key_set) > 0:
                # 数量过少的 key 集中到一起合并到此前最少的分组里面
                for group, (key_set, weight) in group_merged_key_set.items():
                    self.logger.warning(
                        f"{len(group_merged_key_set)} keys merge {group} -> {min_group.name}: {key_set}")
                    self.group_weight_dic[min_group] += weight
                    group_keys_dic[min_group].update(key_set)

            tot_weight = sum(self.group_weight_dic.values())
            self.group_weight_dic = {group: weight / tot_weight for group, weight in self.group_weight_dic.items()}
            msg = "\n".join(
                [f"{group.name:50s} {weight * 100:.2f}%" for group, weight in self.group_weight_dic.items()])
            self.logger.info(f"各分组权重如下：\n{msg}")
        else:
            # 不分组计算权重
            self.group_weight_dic = {InstrumentClassificationEnum.All: 1}
            group_keys_dic = {InstrumentClassificationEnum.All: self.key_balance_df_dic.keys()}

        # 分组进行目标优化
        key_weight_dic = {}
        for group, key_set in group_keys_dic.items():
            # 更新 key_weight_dic 记录
            _key_weight_dic = self._fit_by_group_keys(group, key_set)
            key_weight_dic.update(_key_weight_dic)
            for key in key_set:
                self.key_group_dic[key] = group.name
                self.vt_symbol_group_dic[self.key_vt_symbol_dic[key]] = group.name

        _sum = sum(key_weight_dic.values())
        keys = list(key_weight_dic.keys())
        keys.sort(key=lambda key: self.key_vt_symbol_dic[key])
        self.key_weight_dic = _key_weight_dic = {key: key_weight_dic[key] / _sum for key in keys}
        if self.max_vt_symbol_weight:
            # -------------------- max_vt_symbol_weight 调整开始 ----------------------------
            # 记录因仓位限制而调整后，剩余的key以及仓位比例
            rest_key_set = set(_key_weight_dic.keys())
            rest_weight = 1
            # 按 instrument_type 分组
            vt_symbol_weight_pairs_dic = defaultdict(list)
            for key, weight in _key_weight_dic.items():
                vt_symbol_weight_pairs_dic[self.key_vt_symbol_dic[key]].append(
                    (key, weight))

            # 分组计算是否需要调整
            vt_symbol_weight_dic = {}
            for vt_symbol, key_weight_pairs in vt_symbol_weight_pairs_dic.items():
                tot_weight = sum([_[1] for _ in key_weight_pairs])
                if tot_weight > self.max_vt_symbol_weight:
                    scaling_down_rate = self.max_vt_symbol_weight / tot_weight
                    for key, weight in key_weight_pairs:
                        _key_weight_dic[key] = weight * scaling_down_rate
                        rest_key_set.remove(key)

                    keys_str = '\n'.join([f"{key:130s} {weight * 100:.2f}% -> {_key_weight_dic[key] * 100:.2f}"
                                          for key, weight in key_weight_pairs])
                    self.logger.warning(
                        f"{vt_symbol} 总体比例 {tot_weight * 100:.2f}% > "
                        f"{self.max_vt_symbol_weight * 100:.2f}% 缩放比例 {scaling_down_rate:.2f}，"
                        f"受影响key包括：\n{keys_str}")
                    rest_weight -= self.max_vt_symbol_weight
                    vt_symbol_weight_dic[vt_symbol] = self.max_vt_symbol_weight
                else:
                    vt_symbol_weight_dic[vt_symbol] = tot_weight

            if rest_weight < 1 and len(rest_key_set) > 0:
                tot_weight = sum([weight for key, weight in self.key_weight_dic.items() if key in rest_key_set])
                change_rate = rest_weight / tot_weight
                self.logger.warning(f"调整剩余 {len(rest_key_set)} key 的权重，调整因子{change_rate:.2f}")
                # 按合约简称是否存在调整后超 max_vt_symbol_weight 的合约
                vt_symbols = list({self.key_vt_symbol_dic[key] for key in rest_key_set})
                vt_symbols.sort(key=lambda x: vt_symbol_weight_dic[x], reverse=True)
                for vt_symbol in vt_symbols:
                    vt_symbol_weight = vt_symbol_weight_dic[vt_symbol]
                    new_weight = vt_symbol_weight * change_rate
                    if new_weight > self.max_vt_symbol_weight:
                        change_rate_curr = self.max_vt_symbol_weight / vt_symbol_weight
                        tot_weight -= vt_symbol_weight
                        rest_weight -= self.max_vt_symbol_weight
                        change_rate = rest_weight / tot_weight
                        change_rate_changed = True
                    else:
                        change_rate_curr = change_rate
                        change_rate_changed = False

                    key_weight_pairs = vt_symbol_weight_pairs_dic[vt_symbol]
                    for key, weight in key_weight_pairs:
                        self.key_weight_dic[key] = weight * change_rate_curr
                        rest_key_set.remove(key)

                    if change_rate_changed:
                        self.logger.warning(
                            f"调整剩余 {len(rest_key_set)} key 的权重，"
                            f"调整因子{change_rate:.2f}，{vt_symbol} -> {self.max_vt_symbol_weight * 100:.2f}%")

            # -------------------- max_vt_symbol_weight 调整结束 ----------------------------

        self.logger.info(f"{'*' * 20} weight by key {'*' * 20}")
        for num, (key, weight) in enumerate(self.key_weight_dic.items(), start=1):
            self.logger.info(f"{num:2d}) {self.key_vt_symbol_dic[key]:11s} {key:130s} --> {weight * 100:.2f}%")

        self.logger.info(f"{'*' * 20} weight by vt_symbol (strategy count){'*' * 20}")
        vt_symbol_weight_pairs_dic = defaultdict(list)
        for key, weight in self.key_weight_dic.items():
            vt_symbol_weight_pairs_dic[self.key_vt_symbol_dic[key]].append((key, weight))
        vt_symbols = list(vt_symbol_weight_pairs_dic.keys())
        vt_symbols.sort()
        for num, vt_symbol in enumerate(vt_symbols, start=1):
            key_weight_pairs = vt_symbol_weight_pairs_dic[vt_symbol]
            tot_weight = sum([_[1] for _ in key_weight_pairs])
            available_count = sum([1 for _ in key_weight_pairs if _[1] > 0.01])
            self.logger.info(
                f"{num:2d}) {vt_symbol:11s} {len(key_weight_pairs)} >> {available_count}(>0.01)"
                f" sum: {tot_weight * 100:5.2f}%")

    def _fit_by_group_keys(self, group: InstrumentClassificationEnum, key_set: set):
        key_stats_dic = {key: _ for key, _ in self.key_stats_dic.items() if key in key_set}
        key_weight_dic, rr_s = fit_and_merge_key_stats_dic(
            key_stats_dic, group.name, goal=self.goal, weight=self.group_weight_dic[group],
            solver=self.solver, start_date=self.start_date, end_date=self.end_date, **self._kwargs)

        missing_key_set = key_set - set(key_weight_dic.keys())
        if len(missing_key_set) > 0:
            self.logger.warning("%s %d keys missing in fitting. \n%s",
                                group.name, len(missing_key_set), "\n".join(missing_key_set))
        for key, weight in key_weight_dic.items():
            if weight < 0:
                raise ValueError(f"{key} weight={weight:.4f} 无效。不允许负权重持仓。")

        return key_weight_dic

    def get_weights(self) -> Dict[str, float]:
        return self.key_weight_dic

    @lru_cache()
    def get_latest_price(self) -> Dict[str, float]:
        symbols: Set[str] = {_.symbols_info.symbols.split('.')[0] for _ in self.key_stats_dic.values()}
        vt_symbol_price_dic = SymbolsInfo.get_vt_symbol_latest_price_dic(symbols)
        return vt_symbol_price_dic

    def get_vt_symbol_market_value_dic(self, key_base_positions_dic):
        vt_symbol_price_dic = self.get_latest_price()
        vt_symbol_market_value_dic = {}
        for key, base_positions in key_base_positions_dic.items():
            vt_symbol = self.key_vt_symbol_dic[key]
            vt_symbol_market_value_dic[vt_symbol] = (
                    vt_symbol_price_dic[vt_symbol.upper()] * get_vt_symbol_multiplier(vt_symbol) * base_positions)

        return vt_symbol_market_value_dic

    @lru_cache()
    def get_base_positions(self, capital=1_000_000) -> Dict[str, int]:
        vt_symbol_price_dic = self.get_latest_price()
        # 该价格为×乘数后的价格
        weights_dic = self.get_weights()
        price_s = pd.Series({
            k: vt_symbol_price_dic[
                   stats.symbols_info.symbols.upper()
               ] * get_vt_symbol_multiplier(stats.symbols_info.symbols)
            for k, stats in self.key_stats_dic.items() if k in weights_dic})
        da = DiscreteAllocation(weights_dic, price_s, capital)
        _key_base_positions_dic, leftover = da.lp_portfolio(**self._kwargs.get('lp_portfolio_param', {}))
        # self.logger.info(f"{'*' * 20} base_positions {capital:,d} (base_positions) {'*' * 20}")
        symbol_pos_dic = defaultdict(lambda: 0)
        symbol_stg_count_dic = defaultdict(lambda: 0)
        msg_dic_list = []
        for num, (key, base_positions) in enumerate(_key_base_positions_dic.items(), start=1):
            # self.logger.info(f"{num:2d}) {key} --> {base_positions}")
            symbol_pos_dic[self.key_vt_symbol_dic[key]] += base_positions
            symbol_stg_count_dic[self.key_vt_symbol_dic[key]] += 1
            msg_dic_list.append({
                "group_name": self.key_group_dic[key],
                "vt_symbol": self.key_vt_symbol_dic[key],
                "key": key,
                "base_positions": base_positions
            })

        msg_dic_list.sort(key=lambda x: f"{x['group_name']}_{x['vt_symbol']}_{x['key']}")
        self.logger.info(f"capital: {capital:,d} 按策略统计持仓：\n{pd.DataFrame(msg_dic_list).to_markdown()}")
        keys = list(symbol_pos_dic.keys())
        keys.sort()
        msg_dic_list = []
        for num, ((symbol, base_positions), (_, stg_count)) in enumerate(zip(
                symbol_pos_dic.items(), symbol_stg_count_dic.items()), start=1
        ):
            msg_dic_list.append({
                "group_name": self.vt_symbol_group_dic[symbol],
                "vt_symbol": symbol,
                "stg_count": stg_count,
                "base_positions": base_positions
            })
            # self.logger.info(f"{num:2d}) {symbol:11s}[{stg_count:2d}] --> {base_positions:2d}")

        msg_dic_list.sort(key=lambda x: f"{x['group_name']}_{x['vt_symbol']}")
        self.logger.info(f"capital: {capital:,d} 按合约统计持仓情况：\n{pd.DataFrame(msg_dic_list).to_markdown()}")
        return _key_base_positions_dic

    def update_base_positions(self, *, capital=1_000_000, min_positions=0,
                              stop_opening_pos_if_base_position_zero=True):
        from vnpy_extra.db.orm import database
        key_base_positions_dic = self.get_base_positions(capital=capital)
        with database.atomic():
            for key, stats in self.key_stats_dic.items():
                base_positions = key_base_positions_dic.get(key, min_positions)
                stats.set_base_position(
                    base_positions, stop_opening_pos_if_base_position_zero=stop_opening_pos_if_base_position_zero)

    @classmethod
    def build_by_account(cls, user_name, broker_id, **kwargs):
        stats_list = AccountStrategyMapping.get_stats_by_account(user_name, broker_id)
        return cls(stats_list, **kwargs)


class PortfolioOptimizationGroupFitting(PortfolioOptimization):
    def __init__(self, stats_list: List[StrategyBacktestStats], shown_corr_plot=False, **kwargs):
        super(PortfolioOptimizationGroupFitting, self).__init__(stats_list, shown_corr_plot, **kwargs)
        self.fitting_instrument_group_list: Optional[List[FittingInstrumentGroup]] = None

    def set_goal(self, *, fitting_group_list: List[FittingInstrumentGroup],
                 max_vt_symbol_weight=None, start_date=None, end_date=None,
                 auto_merge_into_other_group_if_lower_than=3,
                 **kwargs
                 ):
        self.fitting_instrument_group_list: List[FittingInstrumentGroup] = fitting_group_list
        self.max_vt_symbol_weight = max_vt_symbol_weight
        self.start_date = start_date
        self.end_date = end_date
        self.auto_merge_into_other_group_if_lower_than = auto_merge_into_other_group_if_lower_than
        self._kwargs.update(kwargs)

    def fit(self):
        """分组计算权重"""
        if self._kwargs.get('output_balance_df', False):
            balance_df = pd.DataFrame({
                key: df['balance']
                for key, df in self.key_balance_df_dic.items() if df is not None})
            # rr_s = balance_df / balance_df.iloc[0, :]
            balance_df.to_csv(f"balance_df.csv")

        # 对分组进行整理
        group_fitting_key_group_dic: Dict[str, FittingKeysGroup] = {}
        group_merged_key_set: Dict[str, Tuple[set, float]] = {}
        min_group = None
        for num, fitting_instrument_group in enumerate(
                self.fitting_instrument_group_list, start=1
        ):
            # 仅对当期主力合约进行优化
            available_key_set = {
                key for key, vt_symbol in self.key_vt_symbol_dic.items()
                if (key in self.key_balance_df_dic
                    and get_instrument_type(vt_symbol).upper() in fitting_instrument_group.instrument_set)
            }
            key_count = len(available_key_set)
            group_name = fitting_instrument_group.name
            if fitting_instrument_group.weights == 0:
                self.logger.warning(f"ignore {group_name}[{key_count}] because of weight=0.")
                group_fitting_key_group_dic[group_name] = FittingKeysGroup(
                    group_name,
                    available_key_set,
                    0,
                    fitting_instrument_group.goal,
                    fitting_instrument_group.solver,
                    fitting_instrument_group.kwargs
                )
                continue
            if key_count == 0:
                self.fitting_instrument_group_list.pop(num - 1)
                self.logger.warning(f"{group_name} has {key_count} key. ignored.")
                group_fitting_key_group_dic[group_name] = FittingKeysGroup(
                    group_name,
                    available_key_set,
                    0,
                    fitting_instrument_group.goal,
                    fitting_instrument_group.solver,
                    fitting_instrument_group.kwargs
                )
                continue
            elif key_count <= self.auto_merge_into_other_group_if_lower_than:
                self.logger.warning(
                    f"{group_name} has {key_count}<{self.auto_merge_into_other_group_if_lower_than} keys "
                    f"will be merged with other groups.")
                group_merged_key_set[group_name] = (available_key_set, fitting_instrument_group.weights)
            else:
                group_fitting_key_group_dic[group_name] = FittingKeysGroup(
                    group_name,
                    available_key_set,
                    fitting_instrument_group.weights,
                    fitting_instrument_group.goal,
                    fitting_instrument_group.solver,
                    fitting_instrument_group.kwargs
                )
                if not min_group or len(group_fitting_key_group_dic[min_group].key_set) > key_count:
                    min_group = group_name

        # 合并 < auto_merge_into_other_group_if_lower_than 的分组
        if len(group_merged_key_set) > 0:
            # 数量过少的 key 集中到一起合并到此前最少的分组里面
            for group_name, (available_key_set, weights) in group_merged_key_set.items():
                self.logger.warning(
                    f"{len(group_merged_key_set)} keys merge {group_name} -> {min_group}: {available_key_set}")
                obj: FittingKeysGroup = group_fitting_key_group_dic[min_group]
                group_fitting_key_group_dic[min_group].key_set |= available_key_set
                group_fitting_key_group_dic[min_group].weights += weights

        # 重新计算权重
        tot_weight = sum([_.weights for _ in group_fitting_key_group_dic.values()])
        for group_name, fitting_key_group in group_fitting_key_group_dic.items():
            fitting_key_group.weights /= tot_weight
            for key in fitting_key_group.key_set:
                self.key_group_dic[key] = group_name
                self.vt_symbol_group_dic[self.key_vt_symbol_dic[key]] = group_name

        # msg = "\n".join(
        #     [f"{group_name:50s} {fitting_key_group.weight * 100:.2f}%"
        #      for group_name, fitting_key_group in group_fitting_key_group_dic.items()])
        df = pd.DataFrame({
            group_name: [np.round(fitting_key_group.weights * 100, 2),
                         len(fitting_key_group.key_set),
                         fitting_key_group.goal.name]
            for group_name, fitting_key_group in group_fitting_key_group_dic.items()},
            index=['weight(%)', "stg count", 'goal']).T
        self.logger.info(f"各分组权重如下：\n{df.to_markdown()}\n")

        # 分组进行目标优化
        key_weight_dic = {}
        for group_name, fitting_key_group in group_fitting_key_group_dic.items():
            if fitting_key_group.weights == 0 or len(fitting_key_group.key_set) == 0:
                continue
            # 更新 key_weight_dic 记录
            key_weight_dic.update(self._fit_by_group_keys(fitting_key_group))

        # 开始重新平衡合约权重
        _sum = sum(key_weight_dic.values())
        keys = list(key_weight_dic.keys())
        keys.sort(key=lambda key: f"{self.key_group_dic[key]}_{self.key_vt_symbol_dic[key]}")
        self.key_weight_dic = _key_weight_dic = {key: key_weight_dic[key] / _sum for key in keys}
        if self.max_vt_symbol_weight:
            # -------------------- max_vt_symbol_weight 调整开始 ----------------------------
            # 记录因仓位限制而调整后，剩余的key以及仓位比例
            rest_key_set = set(_key_weight_dic.keys())
            rest_weight = 1
            # 按 instrument_type 分组
            vt_symbol_weight_pairs_dic = defaultdict(list)
            for key, weights in _key_weight_dic.items():
                vt_symbol_weight_pairs_dic[self.key_vt_symbol_dic[key]].append(
                    (key, weights))

            # 分组计算是否需要调整
            vt_symbol_weight_dic = {}
            for vt_symbol, key_weight_pairs in vt_symbol_weight_pairs_dic.items():
                tot_weight = sum([_[1] for _ in key_weight_pairs])
                if tot_weight > self.max_vt_symbol_weight:
                    scaling_down_rate = self.max_vt_symbol_weight / tot_weight
                    for key, weights in key_weight_pairs:
                        _key_weight_dic[key] = weights * scaling_down_rate
                        rest_key_set.remove(key)

                    keys_str = '\n'.join([f"{key:130s} {weight * 100:.2f}% -> {_key_weight_dic[key] * 100:.2f}"
                                          for key, weight in key_weight_pairs])
                    self.logger.warning(
                        f"{vt_symbol} 总体比例 {tot_weight * 100:.2f}% > "
                        f"{self.max_vt_symbol_weight * 100:.2f}% 缩放比例 {scaling_down_rate:.2f}，"
                        f"受影响key包括：\n{keys_str}")
                    rest_weight -= self.max_vt_symbol_weight
                    vt_symbol_weight_dic[vt_symbol] = self.max_vt_symbol_weight
                else:
                    vt_symbol_weight_dic[vt_symbol] = tot_weight

            if rest_weight < 1 and len(rest_key_set) > 0:
                tot_weight = sum([weight for key, weight in self.key_weight_dic.items() if key in rest_key_set])
                change_rate = rest_weight / tot_weight
                self.logger.warning(f"调整剩余 {len(rest_key_set)} key 的权重，调整因子{change_rate:.2f}")
                # 按合约简称是否存在调整后超 max_vt_symbol_weight 的合约
                vt_symbols = list({self.key_vt_symbol_dic[key] for key in rest_key_set})
                vt_symbols.sort(key=lambda x: vt_symbol_weight_dic[x], reverse=True)
                for vt_symbol in vt_symbols:
                    vt_symbol_weight = vt_symbol_weight_dic[vt_symbol]
                    new_weight = vt_symbol_weight * change_rate
                    if new_weight > self.max_vt_symbol_weight:
                        change_rate_curr = self.max_vt_symbol_weight / vt_symbol_weight
                        tot_weight -= vt_symbol_weight
                        rest_weight -= self.max_vt_symbol_weight
                        change_rate = rest_weight / tot_weight
                        change_rate_changed = True
                    else:
                        change_rate_curr = change_rate
                        change_rate_changed = False

                    key_weight_pairs = vt_symbol_weight_pairs_dic[vt_symbol]
                    for key, weights in key_weight_pairs:
                        self.key_weight_dic[key] = weights * change_rate_curr
                        rest_key_set.remove(key)

                    if change_rate_changed:
                        self.logger.warning(
                            f"调整剩余 {len(rest_key_set)} key 的权重，"
                            f"调整因子{change_rate:.2f}，{vt_symbol} -> {self.max_vt_symbol_weight * 100:.2f}%")

            # -------------------- max_vt_symbol_weight 调整结束 ----------------------------

        # 输出 key weight 对照关系
        # self.logger.info(f"{'*' * 20} weight by key {'*' * 20}")
        msg_dic_list = []
        for num, (key, weights) in enumerate(self.key_weight_dic.items(), start=1):
            vt_symbol = self.key_vt_symbol_dic[key]
            # self.logger.info(f"{num:2d}) {vt_symbol:11s} {key:130s} --> {weight * 100:.2f}%")
            msg_dic_list.append({
                "group_name": self.key_group_dic[key],
                "vt_symbol": vt_symbol,
                "key": key,
                "weight(%)": np.round(weights * 100, 2),
            })

        msg_dic_list.sort(key=lambda x: f"{x['group_name']}_{x['vt_symbol']}")
        self.logger.info(f"策略权重：\n{pd.DataFrame(msg_dic_list).to_markdown()}\n")

        # 输出 vt_symbol weight 对应关系
        # self.logger.info(f"{'*' * 20} weight by vt_symbol (strategy count){'*' * 20}")
        vt_symbol_weight_pairs_dic = defaultdict(list)
        for key, weights in self.key_weight_dic.items():
            vt_symbol_weight_pairs_dic[self.key_vt_symbol_dic[key]].append((key, weights))
        vt_symbols = list(vt_symbol_weight_pairs_dic.keys())
        vt_symbols.sort()
        msg_dic_list = []
        for num, vt_symbol in enumerate(vt_symbols, start=1):
            key_weight_pairs = vt_symbol_weight_pairs_dic[vt_symbol]
            tot_weight = sum([_[1] for _ in key_weight_pairs])
            available_count = sum([1 for _ in key_weight_pairs if _[1] > 0.01])
            # self.logger.info(
            #     f"{num:2d}) {vt_symbol:11s} {len(key_weight_pairs)} >> {available_count}(>0.01)"
            #     f" sum: {tot_weight * 100:5.2f}%")
            msg_dic_list.append({
                "group_name": self.vt_symbol_group_dic[vt_symbol],
                "vt_symbol": vt_symbol,
                "strategy_count": len(key_weight_pairs),
                "weight>0.01": available_count,
                "weight(%)": np.round(tot_weight * 100, 2),
            })

        msg_dic_list.sort(key=lambda x: f"{x['group_name']}_{x['vt_symbol']}")
        self.logger.info(f"按合约统计策略数量及权重：\n{pd.DataFrame(msg_dic_list).to_markdown()}\n")

    def _fit_by_group_keys(self, fitting_keys_group: FittingKeysGroup):
        key_set = fitting_keys_group.key_set
        group_name = fitting_keys_group.name
        key_stats_dic = {key: _ for key, _ in self.key_stats_dic.items() if key in key_set}
        key_weight_dic, rr_s = fit_and_merge_key_stats_dic(
            key_stats_dic, group_name, goal=fitting_keys_group.goal, weight=fitting_keys_group.weights,
            solver=fitting_keys_group.solver, **fitting_keys_group.kwargs)

        missing_key_set = key_set - set(key_weight_dic.keys())
        if len(missing_key_set) > 0:
            self.logger.warning("%s %d keys missing in fitting. \n%s",
                                group_name, len(missing_key_set), "\n".join(missing_key_set))
        for key, weight in key_weight_dic.items():
            if weight < 0:
                raise ValueError(f"{key} weight={weight:.4f} 不允许负权重持仓。请尝试其他方法。")

        return key_weight_dic


def portfolio_optimization_by_account(
        user_name, broker_id, description=None,
        capital=1_000_000, refresh_pos=True,
        do_update_base_positions=True, shown_corr_plot=False, show_plot=True, show_plot_legend=False,
        curr_symbol_only=True,
        **kwargs
):
    set_account(user_name, broker_id)
    if refresh_pos:
        from vnpy_extra.report.monitor import StrategyPositionMonitor
        monitor = StrategyPositionMonitor()
        monitor.logger.info(f"{'*' * 10} {user_name}[{broker_id}] {description if description else ''} "
                            f"开始更新持仓信息 {'*' * 10}")
        monitor.refresh_positions()
        StrategyPositionMonitor.refresh_position_daily()

    if 'fit_by_group' in kwargs:
        po = PortfolioOptimization.build_by_account(
            user_name, broker_id, shown_corr_plot=shown_corr_plot, curr_symbol_only=curr_symbol_only,
        )
        # po.set_goal(
        #     PortfolioOptimizeGoalEnum.equal_mdd,
        #     benchmark=100_000,  # 仅 PortfolioOptimizeGoalEnum.equal_mdd 时有效
        #     equal_mdd_indicator='most_drawdown',  # 仅 PortfolioOptimizeGoalEnum.equal_mdd 时有效
        #     fit_by_group={
        #         InstrumentClassificationEnum.AGRICULTURE: 0.4,
        #         InstrumentClassificationEnum.CHEMICAL: 0.3,
        #         InstrumentClassificationEnum.CFFEX: 0.2,
        #         InstrumentClassificationEnum.BLACK: 0.1,
        #         InstrumentClassificationEnum.PRECIOUS_NONFERROUS_METAL: 0.0,
        #     },
        #     start_date=str_2_date('2021-03-01'),
        #     max_vt_symbol_weight=0.2,
        #     lp_portfolio_param=dict(
        #         solver="CPLEX"
        #     ),
        # )
    elif 'fitting_group_list' in kwargs:
        po = PortfolioOptimizationGroupFitting.build_by_account(
            user_name, broker_id, shown_corr_plot=shown_corr_plot, curr_symbol_only=curr_symbol_only,
        )
    else:
        raise ValueError(f"参数无效：{kwargs.keys()}")

    po.set_goal(**kwargs)
    po.fit()
    if show_plot or do_update_base_positions:
        key_base_positions_dic = po.get_base_positions(capital=capital)
        vt_symbol_market_value_dic = po.get_vt_symbol_market_value_dic(key_base_positions_dic)
        if show_plot:
            plot_with_weights(
                po.key_stats_dic.values(), weight_dic=key_base_positions_dic,
                capital=capital, key_vt_symbol_dic=po.key_vt_symbol_dic, legend=show_plot_legend,
                vt_symbol_market_value_dic=vt_symbol_market_value_dic,
                vt_symbol_group_dic=po.vt_symbol_group_dic,
            )

        if do_update_base_positions:
            po.update_base_positions(
                min_positions=0, stop_opening_pos_if_base_position_zero=True,
                capital=capital)
            generate_strategy_setting_file(
                list(po.key_stats_dic.values()),
                ignore_stop_opening_pos_stg=True, ignore_old_symbol=True, include_holding_pos_stg=True)
            plot_by_account(
                description=description, capital=capital,
                legend=show_plot_legend,
                vt_symbol_group_dic=po.vt_symbol_group_dic,
            )


def _test_portfolio_optimization():
    goal_kwargs = dict(
        goal=PortfolioOptimizeGoalEnum.min_volatility,
        # PortfolioOptimizeGoalEnum.equal_mdd, benchmark=20_000,  # 仅 PortfolioOptimizeGoalEnum.equal_mdd 时有效
        # equal_mdd_indicator='most_drawdown',  # 仅 PortfolioOptimizeGoalEnum.equal_mdd 时有效
        fit_by_group={
            InstrumentClassificationEnum.AGRICULTURE: 0.2,
            InstrumentClassificationEnum.CHEMICAL: 0.3,
            InstrumentClassificationEnum.CFFEX: 0.2,
            InstrumentClassificationEnum.BLACK: 0.4,
            InstrumentClassificationEnum.PRECIOUS_NONFERROUS_METAL: 0.1,
        },
        start_date=str_2_date('2020-01-01'),
        end_date=str_2_date('2020-12-31'),
        max_vt_symbol_weight=0.15
    )
    portfolio_optimization_by_account(
        user_name="000001", broker_id="000001", description='测试账户',
        capital=3_000_000, refresh_pos=False, do_update_base_positions=False,
        shown_corr_plot=False, show_plot=True, **goal_kwargs
    )


def _test_portfolio_optimization_group_fitting():
    goal_kwargs = dict(
        fitting_group_list=[
            FittingInstrumentGroup.create_by_instrument_classification_enum(
                InstrumentClassificationEnum.AGRICULTURE,
                0.4,
                PortfolioOptimizeGoalEnum.min_volatility,
            ),
            FittingInstrumentGroup.create_by_instrument_classification_enum(
                InstrumentClassificationEnum.CHEMICAL,
                0.3,
                PortfolioOptimizeGoalEnum.equal_mdd,
                benchmark=20_000,  # 仅 PortfolioOptimizeGoalEnum.equal_mdd 时有效
                equal_mdd_indicator='most_drawdown',  # 仅 PortfolioOptimizeGoalEnum.equal_mdd 时有效
                # group_by_vt_symbol=True,
                # group_by_vt_symbol_kwargs=dict(
                #     default=dict(
                #         goal=PortfolioOptimizeGoalEnum.min_volatility,
                #     )
                # )
            ),
            FittingInstrumentGroup.create_by_instrument_classification_enum(
                InstrumentClassificationEnum.CFFEX,
                0.0,
                PortfolioOptimizeGoalEnum.max_quadratic_utility,
            ),
            FittingInstrumentGroup.create_by_instrument_classification_enum(
                InstrumentClassificationEnum.BLACK,
                0.0,
                PortfolioOptimizeGoalEnum.max_sharpe,
            ),
            FittingInstrumentGroup.create_by_instrument_classification_enum(
                InstrumentClassificationEnum.PRECIOUS_NONFERROUS_METAL,
                0.3,
                PortfolioOptimizeGoalEnum.min_volatility,
            ),
        ],
        start_date=str_2_date('2020-01-01'),
        end_date=str_2_date('2020-12-31'),
        max_vt_symbol_weight=0.2,
        lp_portfolio_param=dict(
            solver="CPLEX"
        ),
        auto_merge_into_other_group_if_lower_than=1
    )
    portfolio_optimization_by_account(
        user_name="000001", broker_id="000001", description='测试账户',
        capital=3_000_000, refresh_pos=False, do_update_base_positions=False,
        shown_corr_plot=False, show_plot=True, **goal_kwargs
    )


if __name__ == "__main__":
    # _test_portfolio_optimization()
    _test_portfolio_optimization_group_fitting()
