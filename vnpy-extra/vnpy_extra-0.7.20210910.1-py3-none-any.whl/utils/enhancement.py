"""
@author  : MG
@Time    : 2020/10/9 13:49
@File    : enhancement.py
@contact : mmmaaaggg@163.com
@desc    : 用于对 vnpy 内置的各种类及函数进行增强
"""
import collections
import inspect
import math
import weakref
from datetime import time
from enum import Enum
from typing import Callable, Union, Tuple, Optional

import numpy as np
import pandas as pd
import talib
from ibats_utils.mess import get_first
from vnpy.app.cta_strategy import (
    BarData,
    BarGenerator as BarGeneratorBase,
    ArrayManager as ArrayManagerBase,
    CtaSignal as CtaSignalBase,
)
from vnpy.trader.constant import Interval
from vnpy.trader.object import TickData

from vnpy_extra.config import logging
from vnpy_extra.constants import SYMBOL_MINUTES_COUNT_DIC, BASE_POSITION
from vnpy_extra.utils.symbol import get_instrument_type

logger = logging.getLogger(__name__)


class PriceTypeEnum(Enum):
    open = 'open'
    high = 'high'
    low = 'low'
    close = 'close'
    auto = 'auto'


def get_daily_min_bar_count(symbol: Optional[str] = None):
    """返回每天有多少分钟线数据"""
    if symbol is None:
        return 350
    instrument_type = get_instrument_type(symbol)
    min_bar_count = SYMBOL_MINUTES_COUNT_DIC[instrument_type.upper()]
    return min_bar_count


class BarGenerator(BarGeneratorBase):
    def __init__(
            self,
            on_bar: Callable,
            window: int = 0,
            on_window_bar: Callable = None,
            interval: Interval = Interval.MINUTE,
            strict=False
    ):
        super().__init__(on_bar, window, on_window_bar, interval)
        # self.instrument_type = None
        # 统一按照 15点整收盘计算
        self.trade_end_time = time(15, 0, 0)
        # 记录上一个触发 self.on_window_bar 的 bar 实例
        self.last_finished_bar = None
        # 记录 1m bar的数量
        self.bar_count = 0
        # 记录上一次生产 window_bar 时，对应的 bar_count
        self._last_finished_bar_no = 0
        self.strict = strict
        # 记录上一次 (bar.datetime.minute + 1) % self.window 的余数结果
        self._last_mod_remainder = 0

    def is_end_day(self, bar):
        """判断交易日是否结束，以15点作为分界点"""
        is_end = bar.datetime.time() == self.trade_end_time
        if not is_end:
            if self.last_bar.datetime.date() == bar.datetime.date():
                # 有夜盘的情况
                is_end = self.last_bar != self.last_finished_bar and \
                         self.last_bar.datetime.hour <= 15 < bar.datetime.hour
            else:
                # 没有夜盘的情况
                is_end = self.last_bar != self.last_finished_bar and \
                         9 <= bar.datetime.hour < self.last_bar.datetime.hour <= 15

        return is_end

    def is_end_week(self, bar):
        """判断但却bar是否是周末最后一根"""
        # isocalendar()[:2] 匹配年号和周数
        # if self.is_end_day(bar):
        #     # 判断当日是否是收盘时间，且即将跨周(周五+2天为周日，跨周）
        #     # 该逻辑不够严谨，对于周一跨周的计算机需要+3，这里暂不考虑
        #
        #     is_end = (bar.datetime + timedelta(days=2)).isocalendar()[:2] != self.last_bar.datetime.isocalendar()[:2]
        # else:
        #     # 有些情况下，当前最后一个时段bar没有，这种情况下只能通过下一个交易日的bar与当前bar周数是否一致来判断
        #     is_end = bar.datetime.isocalendar()[:2] != self.last_bar.datetime.isocalendar()[:2]
        if not self.is_end_day(bar):
            return False
        # from vnpy_extra.db.orm import TradeDateModel 不能放在外层引用，会导致循环引用问题。
        # orm包中部分功能会用到 enhancement.py 中的功能
        from vnpy_extra.db.orm import TradeDateModel
        next_trade_date_dic, _ = TradeDateModel.get_trade_date_dic()
        win_bar_date = self.window_bar.datetime.date()
        if win_bar_date in next_trade_date_dic:
            next_day_dt = next_trade_date_dic[win_bar_date]
            is_end = next_day_dt.isocalendar()[:2] != win_bar_date.isocalendar()[:2]
        else:
            date_time_list = list(next_trade_date_dic.keys())
            date_time_list.sort()
            next_day_date = get_first(date_time_list, lambda x: x > win_bar_date)
            if next_day_date is None:
                logger.error(f"TradeDateModel 数据有误,没有找到 {win_bar_date} 以后的交易日数据")
                is_end = False
            else:
                is_end = next_day_date.isocalendar()[:2] != win_bar_date.isocalendar()[:2]

        return is_end

    def is_end_month(self, bar):
        """判断但却bar是否是月末最后一根（下一个大版本时再启用）"""
        if not self.is_end_day(bar):
            return False
        from vnpy_extra.db.orm import TradeDateModel
        next_trade_date_dic, _ = TradeDateModel.get_trade_date_dic()
        win_bar_date = self.window_bar.datetime.date()
        if win_bar_date in next_trade_date_dic:
            next_day_dt = next_trade_date_dic[win_bar_date]
            is_end = next_day_dt.year != win_bar_date.year or next_day_dt.month != win_bar_date.month
        else:
            date_time_list = list(next_trade_date_dic.keys())
            date_time_list.sort()
            next_day_date = get_first(date_time_list, lambda x: x > win_bar_date)
            is_end = next_day_date.year != win_bar_date.year or next_day_date.month != win_bar_date.month

        return is_end

    def update_bar(self, bar: BarData) -> None:
        """
        Update 1 minute bar into generator
        """
        if bar is None:
            return
        self.bar_count += 1
        # if self.instrument_type is None:
        #     self.instrument_type = get_instrument_type(bar.symbol)
        #     if self.instrument_type in INSTRUMENT_TRADE_TIME_PAIR_DIC:
        #         self.trade_end_time = INSTRUMENT_TRADE_TIME_PAIR_DIC[self.instrument_type][1]
        #     else:
        #         logger.error("当前合约 %s 对应品种 %s 没有对应的交易时段，默认15点收盘",
        #                      bar.symbol, self.instrument_type)
        #         self.trade_end_time = time(15, 0, 0)

        # If not inited, create window bar object
        if not self.window_bar:
            # Generate timestamp for bar data
            if self.interval == Interval.MINUTE:
                dt = bar.datetime.replace(second=0, microsecond=0)
            else:
                dt = bar.datetime.replace(minute=0, second=0, microsecond=0)

            self.window_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price
            )
        # Otherwise, update high/low price into window bar
        else:
            self.window_bar.high_price = max(
                self.window_bar.high_price, bar.high_price)
            self.window_bar.low_price = min(
                self.window_bar.low_price, bar.low_price)

        # Update close price/volume into window bar
        self.window_bar.close_price = bar.close_price
        self.window_bar.volume += int(bar.volume)
        self.window_bar.open_interest = bar.open_interest

        # Check if window bar completed
        finished = False

        if self.interval == Interval.MINUTE:
            # x-minute bar
            if self.strict:
                remainder = (bar.datetime.minute + 1) % self.window
                if remainder == 0 or remainder < self._last_mod_remainder:
                    # remainder < self._last_mod_remainder 说明跨时间段情况出现。
                    # 例如：30分钟周期情况下 10:15 交易所进入休息时段，下一次开盘时间10:30。
                    # 用 (bar.datetime.minute + 1) % self.window 的逻辑将错过此次bar生成。
                    # 而在当前逻辑下，将会在10:30分时生成一个 10:00 ~ 10:15时段的 bar 最为 30m bar
                    finished = True

                self._last_mod_remainder = remainder
            elif not (bar.datetime.minute + 1) % self.window:
                finished = True

        elif self.interval == Interval.HOUR:
            if self.last_bar:
                new_hour = self.last_finished_bar != self.last_bar and bar.datetime.hour != self.last_bar.datetime.hour
                last_minute = bar.datetime.minute == 59

                if new_hour or last_minute:
                    # 1-hour bar
                    if self.window == 1:
                        finished = True
                    # x-hour bar
                    else:
                        self.interval_count += 1

                        if not self.interval_count % self.window:
                            finished = True
                            self.interval_count = 0

        elif self.interval == Interval.DAILY:
            if self.last_bar and self.last_finished_bar != self.last_bar and self.is_end_day(bar):
                # 1-day bar
                if self.window == 1:
                    finished = True
                # x-day bar
                else:
                    self.interval_count += 1

                    if not self.interval_count % self.window:
                        finished = True
                        self.interval_count = 0
        elif self.interval == Interval.WEEKLY:
            if self.last_bar and self.last_finished_bar != self.last_bar and self.is_end_week(bar):
                # 1-day bar
                if self.window == 1:
                    finished = True
                # x-day bar
                else:
                    self.interval_count += 1

                    if not self.interval_count % self.window:
                        finished = True
                        self.interval_count = 0

        # 判断是否当前 bar 结束
        if finished:
            self.on_window_bar(self.window_bar)
            self.last_finished_bar = bar
            self._last_finished_bar_no = self.bar_count
            self.window_bar: Optional[BarData] = None

        # Cache last bar object
        self.last_bar = bar


def update_array(array: np.ndarray, value):
    """将数据更新到数组最后个"""
    array[:-1] = array[1:]
    array[-1] = value


def update_array_2d(array: np.ndarray, value: np.ndarray):
    """将数据更新到数组最后个"""
    array[:-1, :] = array[1:, :]
    array[-1, :] = value


class ArrayManager(ArrayManagerBase):

    def __init__(self, size: int = 100, base_price_type=PriceTypeEnum.close.name):
        """
        行情数组
        :param size:数组尺寸
        :param base_price_type:（默认为close）。数组的基础价格类型。对于单一指标而言，计算RSI、MACD等指标时使用的默认价格类型，
        """
        super().__init__(size=size)
        self.datetime_array: np.ndarray = np.array(np.zeros(size), dtype='datetime64[s]')
        # 用于记录每一个 MACD， KDJ，RSI等每一个指标最近一次被调用时候的 count 值。
        # 该值主要是用来在进行指数标准化(z-score)时为了防止重复训练而记录的一个标识位，
        # 每一次新的训练都从该标识位开始往后进行训练，这样以便保证么一次训练均是最新数据
        # 默认情况下 指标都是0上下浮动或者0~1之间浮动，因此，不做均值处理，只除以方差，避免出现0轴偏移的情况
        from sklearn.preprocessing import StandardScaler
        self.index_last_invoked_count_dic = collections.defaultdict(lambda: (0, StandardScaler(with_mean=False)))
        self.fit_threshold = int(self.size * 0.9)  # 超过90% 再进行 fit
        self.base_price_type = base_price_type \
            if isinstance(base_price_type, PriceTypeEnum) else PriceTypeEnum[base_price_type]
        if self.base_price_type == PriceTypeEnum.close:
            self.base_price = self.close
        elif self.base_price_type == PriceTypeEnum.open:
            self.base_price = self.open
        elif self.base_price_type == PriceTypeEnum.high:
            self.base_price = self.high
        elif self.base_price_type == PriceTypeEnum.low:
            self.base_price = self.low
        else:
            raise ValueError(f"base_price_type={base_price_type} 无效")

    def update_bar(self, bar: BarData) -> None:
        super().update_bar(bar=bar)
        self.datetime_array[:-1] = self.datetime_array[1:]
        self.datetime_array[-1] = np.datetime64(bar.datetime)

    def return_rate(self, array: bool = False) -> Union[float, np.ndarray]:
        rr = np.zeros(self.size)
        rr[1:] = self.close_array[1:] / self.close_array[:-1] - 1
        if array:
            return rr
        return rr[-1]

    def kdj(self, fastk_period: int, slowk_period: int, slowd_period: int, array: bool = False):
        # KDJ 值对应的函数是 STOCH
        slowk, slowd = talib.STOCH(
            self.high, self.low, self.close,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,
            slowd_period=slowd_period,
            slowd_matype=0)
        # 求出J值，J = (3*K)-(2*D)
        slowj = list(map(lambda x, y: 3 * x - 2 * y, slowk, slowd))
        if array:
            return slowk, slowd, slowj
        return slowk[-1], slowd[-1], slowj[-1]

    def rsi(self, n: int, array: bool = False) -> Union[float, np.ndarray]:
        """
        Relative Strenght Index (RSI).
        """
        result = talib.RSI(self.base_price, n)
        if array:
            return result
        return result[-1]

    def ma(self, *args, price=None, matype=0, array: bool = False):
        """
        ta.MA(close,timeperiod=30,matype=0)
        移动平均线系列指标包括：SMA简单移动平均线、EMA指数移动平均线、WMA加权移动平均线、DEMA双移动平均线、TEMA三重指数移动平均线、TRIMA三角移动平均线、KAMA考夫曼自适应移动平均线、MAMA为MESA自适应移动平均线、T3三重指数移动平均线。
        其中，close为收盘价，时间序列，timeperiod为时间短，默认30天，
        :param args:
        :param price: 价格序列，默认为None，使用 self.base_price 作为计算基准
        :param matype: matype 分别对应：0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
        :param array: 是否返回数组
        :return:
        """
        if price is None:
            price = self.base_price

        rets = [talib.MA(price, win, matype) for win in args]

        if array:
            return tuple(rets)

        return tuple([_[-1] for _ in rets])

    def record_index_used(self, model, func_name=None):
        """记录该指标的索引值"""
        if func_name is None:
            func_name = inspect.stack()[1][3]
        self.index_last_invoked_count_dic[func_name] = (self.count, model)
        return func_name, self.count

    def get_index_last_used(self, func_name=None):
        """
        获取该指标的索引值
        """
        if func_name is None:
            func_name = inspect.stack()[1][3]
        return func_name, self.index_last_invoked_count_dic[func_name]

    def macd(
            self,
            fast_period: int,
            slow_period: int,
            signal_period: int,
            z_score: bool = False,
            array: bool = False,
    ) -> Union[
        Tuple[np.ndarray, np.ndarray, np.ndarray],
        Tuple[float, float, float]
    ]:
        """
        MACD.
        """
        macd, signal, hist = talib.MACD(
            self.base_price, fast_period, slow_period, signal_period
        )
        if z_score:
            func_name = 'macd'
            _, (count_last, model) = self.get_index_last_used(func_name)
            # 计算需要进行训练的数量
            count_fit = self.count - count_last
            if self.fit_threshold < count_fit:
                if count_last == 0:
                    # 首次训练
                    x = np.concatenate([
                        macd[-count_fit:][:, np.newaxis],
                        signal[-count_fit:][:, np.newaxis],
                        hist[-count_fit:][:, np.newaxis],
                    ], axis=1)
                    x = model.fit_transform(x)
                elif count_fit > self.size:
                    # 全数据增量训练
                    x = np.concatenate([
                        macd[:, np.newaxis],
                        signal[:, np.newaxis],
                        hist[:, np.newaxis],
                    ], axis=1)
                    x = model.partial_fit(x)
                else:
                    # 部分数据增量训练
                    x = np.concatenate([
                        macd[-count_fit:][:, np.newaxis],
                        signal[-count_fit:][:, np.newaxis],
                        hist[-count_fit:][:, np.newaxis],
                    ], axis=1)
                    model.partial_fit(x)
                    x = np.concatenate([
                        macd[:, np.newaxis],
                        signal[:, np.newaxis],
                        hist[:, np.newaxis],
                    ], axis=1)
                    x = model.transform(x)

                # 记录当前指数被使用时的 Count
                self.record_index_used(model, func_name)
            else:
                # 全数据转换
                x = np.concatenate([
                    macd[:, np.newaxis],
                    signal[:, np.newaxis],
                    hist[:, np.newaxis],
                ], axis=1)
                x = model.transform(x)

            # 恢复成 指标
            macd = x[:, 0]
            signal = x[:, 1]
            hist = x[:, 2]

        if array:
            return macd, signal, hist
        return macd[-1], signal[-1], hist[-1]


def generate_available_period(contract_month: int, date_from_str: str, date_to_str: str) -> list:
    """
    生成合约对应的有效日期范围，与给点日期范围的交集
    该功能仅用于策略回测是对1月份连续合约等连续合约数据是使用
    根据合约生成日期范围规则，例如：
    1月合约，上一年8月1 ~ 11月31日
    5月合约，上一年12月1 ~ 3月31日
    9月合约，4月1日 ~ 7月31日
    """
    date_from = pd.to_datetime(date_from_str if date_from_str is not None else '2000-01-01')
    date_to = pd.to_datetime(date_to_str if date_from_str is not None else '2030-01-01')
    periods = []
    for range_year in range(date_from.year, date_to.year + 2):
        year, month = (range_year, contract_month - 5) if contract_month > 5 else (
            range_year - 1, contract_month + 12 - 5)
        range_from = pd.to_datetime(f"{year:4d}-{month:02d}-01")
        year, month = (range_year, contract_month - 1) if contract_month > 1 else (
            range_year - 1, 12)
        range_to = pd.to_datetime(f"{year:4d}-{month:02d}-01") - pd.to_timedelta(1, unit='D')
        # 与 date_from date_to 取交集
        if range_to < date_from or date_to < range_from:
            continue
        range_from = date_from if range_from < date_from < range_to else range_from
        range_to = date_to if range_from < date_to < range_to else range_to
        periods.append([str(range_from.date()), str(range_to.date())])

    return periods


class CtaSignal(CtaSignalBase):

    def __init__(self, period: int, array_size: int, interval: Interval = Interval.MINUTE, *, filter_n_available=1,
                 strict=False, base_price_type=PriceTypeEnum.close.name, vt_symbol=None,
                 strategy_obj=None, **kwargs):
        """

        :param period 周期数
        :param array_size 行情队列大小
        :param interval 周期类型
        :param filter_n_available 有效信号过滤器,超过指定次数后才真正改变 signal_pos 信号数值
        :param strict 是否使用 strict 模式生成 window bar
        :param base_price_type 基础价格类型，用于计算 am 的指标
        :param vt_symbol 合约
        :param strategy_obj 策略实例
        """
        super().__init__()
        self.period = period
        self.interval = interval
        self.array_size = array_size
        # 2021-07-29 MG
        # 回测状态下无法通过 tick 合成 bar 而是直接通过 template 的 on_bar 事件，将 bar 传入 bg.on_bar(bar)
        # 为了避免实盘情况下，on_tick 合成 bar 与 on_bar 中bar重复调用 bg.on_bar 的问题，这里将 bg 的 on_bar 事件替换掉
        self.bg = BarGenerator(
            on_bar=lambda bar: bar, window=self.period, on_window_bar=self.on_window, interval=self.interval,
            strict=strict)
        self.am = ArrayManager(size=array_size, base_price_type=base_price_type)
        self.bar: Optional[BarData] = None
        self.win_bar: Optional[BarData] = None
        self.win_bar_count = 0
        self.filter_n_available = filter_n_available
        self._n_available_counter = 0
        self._n_available_pos = self.signal_pos
        self.vt_symbol = vt_symbol
        from vnpy_extra.backtest.cta_strategy.template import CtaTemplate
        from vnpy_extra.backtest.portfolio_strategy.template import StrategyTemplate
        if strategy_obj:
            if not isinstance(strategy_obj, CtaTemplate) and not isinstance(strategy_obj, StrategyTemplate):
                raise ValueError(f"{strategy_obj}{type(strategy_obj)} 必須是 CtaTemplate 或 StrategyTemplate 的子类")
            self._strategy_obj: Callable[[], Optional[CtaTemplate]] = weakref.ref(strategy_obj)
            # 一跳价格单位
            self.price_scale = strategy_obj.vt_symbol_price_tick
        else:
            raise ValueError(f"{self.__class__.__name__} 需要传入 strategy_obj 参数")

        # 对应 TB 中用于记录上一次进场到现在的数量
        self.bar_count_since_entry = 0
        # 对应 TB 中用于记录上一次出场到现在的数量
        self.bar_count_since_exit = 0
        # 记录上一状态时的 market_position
        self._market_position_at_last_window_bar = 0

    # def on_tick(self, tick: TickData):
    #     """
    #     Callback of new tick data update.
    #     """
    #     self.bg.update_tick(tick)

    @property
    def pos(self):
        return self._strategy_obj().pos

    @property
    def strategy_parameters(self):
        return self._strategy_obj().parameters

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bar = bar
        self.bg.update_bar(bar)

    def on_window(self, bar: BarData):
        """"""
        market_position = self.market_position
        if self._market_position_at_last_window_bar == 0 and market_position != 0:
            self.bar_count_since_entry = self.win_bar_count
        elif self._market_position_at_last_window_bar != 0 and market_position == 0:
            self.bar_count_since_exit = self.win_bar_count

        self._market_position_at_last_window_bar = market_position
        self.am.update_bar(bar)
        self.win_bar = bar
        self.win_bar_count += 1

    def set_signal_pos(self, signal_pos, ignore_filter=False):
        """对 set_signal_pos 增加过滤器,重复超过 self.filter_n_available 次时才算有效"""
        if ignore_filter or signal_pos != self._n_available_pos:
            self._n_available_pos = signal_pos
            self._n_available_counter = 1
        else:
            self._n_available_counter += 1

        if ignore_filter or self._n_available_counter >= self.filter_n_available:
            super().set_signal_pos(signal_pos)

    def daily_bars_needed_at_least(self, symbol: Optional[str] = None):
        """返回至少需要多少日线数据"""
        if symbol is None:
            symbol = self.vt_symbol

        if self.interval == Interval.MINUTE:
            min_bar_count = get_daily_min_bar_count(symbol)
            step = 1 / min_bar_count
        elif self.interval == Interval.HOUR:
            min_bar_count = get_daily_min_bar_count(symbol)
            step = 60 / min_bar_count
        elif self.interval == Interval.DAILY:
            step = 1
        elif self.interval == Interval.WEEKLY:
            step = 7
        else:
            raise ValueError(f"interval={self.interval} 无效")

        daily_bar_count = math.ceil(self.period * self.am.size * step)
        if self.interval != Interval.WEEKLY:
            daily_bar_count *= 1.5

        return daily_bar_count

    @classmethod
    def get_short_name(cls, name: Optional[str] = None) -> str:
        """返回信号简称，用于设置 signal_name_list 以及相应的参数头部字段"""
        if hasattr(cls, "short_name"):
            short_name = getattr(cls, "short_name")
        else:
            signal_cls_name = cls.__name__.lower() if name is None else name
            short_name = signal_cls_name[:-len('signal')] if signal_cls_name.endswith(
                'signal') else signal_cls_name
        return short_name

    @classmethod
    def get_signal_name_header(cls, name: Optional[str] = None) -> str:
        """返回类名称剔除尾部 Signal"""
        signal_cls_name = cls.__name__ if name is None else name
        cls_name_header = signal_cls_name[:-len('Signal')] if signal_cls_name.endswith(
            'Signal') else signal_cls_name
        return cls_name_header

    @property
    def bars_since_entry(self):
        if self.bar_count_since_entry == 0:
            return 0
        else:
            return self.win_bar_count - self.bar_count_since_entry

    @property
    def bars_since_exit(self):
        return self.win_bar_count - self.bar_count_since_exit if self.bar_count_since_exit != 0 else 0

    @property
    def market_position(self):
        return self._strategy_obj().pos

    @property
    def entry_price(self):
        return self._strategy_obj().entry_price

    @property
    def exit_price(self):
        return self._strategy_obj().exit_price

    @property
    def current_bar(self):
        return self.bg.last_finished_bar if self.bg.window_bar is None else self.bg.window_bar

    @property
    def open_current(self):
        return self.current_bar.open_price

    @property
    def high_current(self):
        return self.current_bar.high_price

    @property
    def low_current(self):
        return self.current_bar.low_price

    @property
    def close_current(self):
        return self.current_bar.close_price

    @property
    def volume_current(self):
        return self.current_bar.volume

    @property
    def open(self):
        return self.am.open_array[-1]

    @property
    def high(self):
        return self.am.high_array[-1]

    @property
    def low(self):
        return self.am.low_array[-1]

    @property
    def close(self):
        return self.am.close_array[-1]

    @property
    def volume(self):
        return self.am.volume_array[-1]

    @property
    def open_array(self):
        return self.am.open_array

    @property
    def high_array(self):
        return self.am.high_array

    @property
    def low_array(self):
        return self.am.low_array

    @property
    def close_array(self):
        return self.am.close_array

    @property
    def volume_array(self):
        return self.am.volume_array

    @property
    def lowest_after_entry(self):
        return self._strategy_obj().lowest_after_entry

    @property
    def highest_after_entry(self):
        return self._strategy_obj().highest_after_entry


class CtaExitSignal(CtaSignal):
    def __init__(self, period: int, array_size: int, *,
                 strategy_obj, enable_on_tick_signal=False, enable_on_bar_signal=True, **kwargs):
        """
        用于产生平仓信号
        :param period 周期数
        :param array_size 行情队列大小
        :param strategy_obj 策略实例
        :param enable_on_tick_signal tick级别信号更新
        :param enable_on_bar_signal bar 级别信号更新
        """
        super().__init__(period=period, array_size=array_size, strategy_obj=strategy_obj, **kwargs)
        self.enable_on_tick_signal = enable_on_tick_signal
        self.enable_on_bar_signal = enable_on_bar_signal
        # 用于记录当前信号从产生平仓信号前的持仓状态：持仓N
        # self.close_from_position != 0 即为平仓信号
        self.close_from_position = 0
        # 上一次仓位改变时的仓位状态
        self.last_pos = 0
        # # 进场以来最高价、最低价
        # self.highest_after_entry = None
        # self.lowest_after_entry = None
        self.stop_order_price = 0
        self.kwargs = kwargs

    def on_tick(self, tick: TickData):
        if self.enable_on_tick_signal:
            # 平仓信号出现之前，与当前持仓保持一致
            self._set_signal_pos_equal_current_pos()

        super().on_tick(tick)

    def on_bar(self, bar: BarData):
        if self.enable_on_bar_signal:
            # 平仓信号出现之前，与当前持仓保持一致
            self._set_signal_pos_equal_current_pos()

        # # 更新 highest_after_entry, lowest_after_entry
        # if self.pos <= 0 <= self.signal_pos or self.pos >= 0 >= self.signal_pos:
        #     self.highest_after_entry = None
        #     self.lowest_after_entry = None
        # else:
        #     if not self.highest_after_entry or self.highest_after_entry < bar.high_price:
        #         self.highest_after_entry = bar.high_price
        #
        #     if not self.lowest_after_entry or self.lowest_after_entry > bar.low_price:
        #         self.lowest_after_entry = bar.low_price

        super().on_bar(bar)

    def reset_status(self):
        """重置平仓信号：仓位方向已经调整，此前平仓信号将被重置"""
        self.close_from_position = 0
        self.stop_order_price = 0

    def _set_signal_pos_equal_current_pos(self):
        """平仓信号出现之前，与当前持仓保持一致"""
        # self.set_signal_pos(self._strategy_obj().pos)
        pos = self.pos
        if self.last_pos == pos:
            return
        if (self.close_from_position > 0 and pos > 0) or (self.close_from_position < 0 and pos < 0):
            # 当前状态已经出现平仓信号，不再进行重置状态操作
            return
        elif self.close_from_position < 0 < pos or self.close_from_position > 0 > pos:
            # 重置平仓信号：仓位方向已经调整，此前平仓信号将被重置
            self.reset_status()

        # 由于 BASE_POSITION 乘数存在，因此 self._strategy_obj().pos 不一定等于 signal_pos
        base_position = getattr(self._strategy_obj(), BASE_POSITION, 1)
        signal_pos = math.ceil(pos / base_position) if pos > 0 else math.floor(pos / base_position)
        self.set_signal_pos(signal_pos, ignore_filter=True)
        self.last_pos = pos

    def set_signal_pos(self, signal_pos, *, ignore_filter=False):
        pos = self.pos
        if self.signal_pos != signal_pos and signal_pos == 0 and pos != 0:
            # 触发平仓信号，但当前持仓！=0。
            # 记录平仓信号发出时，持仓状态。
            self.close_from_position = pos

        super().set_signal_pos(signal_pos, ignore_filter=ignore_filter)

    def get_signal_pos(self) -> int:
        return self.signal_pos

    def set_stop_order_price(self, price):
        """设置停损价格，当多头时，价格低于此价格将强制平仓，当空头是，价格高于此价格将强制平仓"""
        self.stop_order_price = price


if __name__ == "__main__":
    pass
