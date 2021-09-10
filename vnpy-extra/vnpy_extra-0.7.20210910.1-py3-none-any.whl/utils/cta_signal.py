"""
@author  : MG
@Time    : 2020/10/12 12:02
@File    : signal.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import math
import typing
import warnings

import numpy as np
from vnpy.app.cta_strategy import BarData
from vnpy.trader.constant import Interval

from vnpy_extra.utils.enhancement import CtaSignal, PriceTypeEnum, get_daily_min_bar_count
from vnpy_extra.utils.func import is_cross


class MACrossPriceSignal(CtaSignal):
    """"""
    short_name = "macp"

    def __init__(self, win_size: int = 9, ma_price_type=PriceTypeEnum.close, cross_price_type='high_low',
                 same_direction=False,
                 period: int = 30, interval: Interval = Interval.MINUTE, reverse_bs: int = 0,
                 filter_n_available=1, **kwargs):
        """
        价格穿越MA均线产生多空信号
        :param win_size: ma window 大小
        :param ma_price_type: ma 价格类型
        :param cross_price_type: 穿越价格类型，默认 "auto" 上穿时使用 low price 下穿时使用 high price
        :param same_direction: 默认为 False，是否上穿是，ma方向要向上，下穿时ma方向要向下。
        :param period: 周期大小
        :param interval: 间隔类型
        :param reverse_bs: 是否反转
        :param filter_n_available: 过滤器
        :param kwargs:
        """
        if isinstance(ma_price_type, str) and hasattr(PriceTypeEnum, ma_price_type):
            ma_price_type = PriceTypeEnum[ma_price_type]

        if isinstance(cross_price_type, str):
            if hasattr(PriceTypeEnum, cross_price_type):
                cross_price_type = PriceTypeEnum[cross_price_type]
            else:
                cross_price_types = cross_price_type.split('_')
                if len(cross_price_types) == 2:
                    cross_price_type = PriceTypeEnum[cross_price_types[0]], PriceTypeEnum[cross_price_types[1]]

        self.win_size = win_size
        self.ma_price_type = ma_price_type
        self.cross_price_type = cross_price_type
        self.same_direction = same_direction
        self.interval = interval
        self.reverse_bs = reverse_bs
        size = win_size + 2
        super().__init__(period=period, array_size=size, interval=interval, filter_n_available=filter_n_available,
                         base_price_type=ma_price_type, **kwargs)
        if isinstance(cross_price_type, PriceTypeEnum):
            self.cross_price: typing.Union[np.ndarray, typing.Tuple[np.ndarray, np.ndarray]] = \
                self.get_price_by_price_type(cross_price_type)
            self._cross_price_type_str = cross_price_type.value[0]
        elif isinstance(cross_price_type, tuple):
            self.cross_price: typing.Union[np.ndarray, typing.Tuple[np.ndarray, np.ndarray]] = \
                (self.get_price_by_price_type(cross_price_type[0]), self.get_price_by_price_type(cross_price_type[1]))
            self._cross_price_type_str = f"{cross_price_type[0].value[0]}{cross_price_type[1].value[0]}"
        else:
            raise ValueError(f"cross_price_type={cross_price_type} 无效")

    def get_price_by_price_type(self, price_type) -> np.ndarray:
        if price_type == PriceTypeEnum.close:
            price = self.am.close_array
        elif price_type == PriceTypeEnum.open:
            price = self.am.open_array
        elif price_type == PriceTypeEnum.high:
            price = self.am.high_array
        elif price_type == PriceTypeEnum.low:
            price = self.am.low_array
        else:
            raise ValueError(f"price_type={price_type} 无效")

        return price

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            self.set_signal_pos(0)
            return

        ma, = self.am.ma(self.win_size, array=True)
        if isinstance(self.cross_price_type, tuple):
            flag_up = is_cross(self.cross_price[0], ma, self.same_direction)
            flag_down = is_cross(self.cross_price[1], ma, self.same_direction)
            if flag_up == 1 and flag_down == -1:
                flag = 0
            elif flag_up == 1:
                flag = flag_up
            elif flag_down == -1:
                flag = flag_down
            else:
                flag = 0
        else:
            flag = is_cross(self.cross_price, ma, self.same_direction)

        if flag != 0:
            self.set_signal_pos(-flag if self.reverse_bs else flag)

    def get_id_name(self) -> str:
        # self.ma_price_type.value[0] 取 PriceTypeEnum 值的第一个字母 o h l c
        names = [
            f"{self.period:02d}{self.interval.value[-1]}_{self.win_size:03d}",
            f"{self.ma_price_type.value[0]}_{self._cross_price_type_str}_{'t' if self.same_direction else 'f'}",
            f"f{self.filter_n_available}" if self.filter_n_available > 1 else '',
            'r' if self.reverse_bs else '',
        ]
        return '_'.join([_ for _ in names if _ != ''])


class MACDSignal(CtaSignal):
    """"""
    short_name = "macd"

    def __init__(self, fast_window: int, slow_window: int, signal_period: int,
                 threshold: int = 1, z_score: int = 1,
                 period: int = 30, interval: Interval = Interval.MINUTE, reverse_bs: int = 0,
                 filter_n_available=1, z_score_days: typing.Optional[int] = None, **kwargs):
        """
        :param fast_window
        :param slow_window
        :param signal_period
        :param threshold 阈值，超过正的阈值或低于负的阈值才会产生信号。分钟级数据由于数值波动较小，要适度减少这个中间地带
        :param z_score 标准化转换，None、0为关闭，>=1 转化的bar数量
        :param period
        :param interval
        :param reverse_bs
        :param filter_n_available
        :param z_score_days 标准化转换计算天数.
        """
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signal_period = signal_period
        self.reverse_bs = reverse_bs
        # 分钟级数据由于数值波动较小，要适度减少这个中间地带
        self.threshold = threshold
        period = period if period != 0 else 30

        # 计算每日需要多少根 bar
        if interval == Interval.MINUTE:
            min_bar_count = get_daily_min_bar_count()
            step = 1 / min_bar_count
        elif interval == Interval.HOUR:
            min_bar_count = get_daily_min_bar_count()
            step = 60 / min_bar_count
        elif interval == Interval.DAILY:
            step = 1
        elif interval == Interval.WEEKLY:
            step = 7
        else:
            raise ValueError(f"interval={self.interval} 无效")

        daily_bar_count = math.ceil(1 / (period * step))

        if z_score_days:
            size = max(self.fast_window, self.slow_window, self.signal_period) * 2
            z_score = daily_bar_count * z_score_days
            size = np.max([size, z_score])
            self.z_score = True
        else:
            self.z_score = (z_score is None or z_score >= 1)  # 默认为True
            size = max(self.fast_window, self.slow_window, self.signal_period) * 2
            size = np.max([size, z_score]) if self.z_score else size
            z_score_days = size // daily_bar_count
            if self.z_score:
                warnings.warn('z_score args of MACDSignal will be deprecated', DeprecationWarning)

        super().__init__(period=period, array_size=size, interval=interval, filter_n_available=filter_n_available,
                         **kwargs)
        self.z_score_days = z_score_days

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            self.set_signal_pos(0)
            return

        _, _, macd = self.am.macd(self.fast_window, self.slow_window, self.signal_period, self.z_score)

        if macd < -self.threshold:
            self.set_signal_pos(1 if self.reverse_bs else -1)
        elif macd > self.threshold:
            self.set_signal_pos(-1 if self.reverse_bs else 1)
        else:
            # self.set_signal_pos(0)
            pass

    def daily_bars_needed_at_least(self, symbol: typing.Optional[str] = None):
        count = super().daily_bars_needed_at_least(symbol)
        return count if count > self.z_score_days else self.z_score_days


class KDJSignal(CtaSignal):
    """"""
    short_name = "kdj"

    def __init__(self, fastk_period: int = 9, slowk_period: int = 3, slowd_period: int = 3,
                 higher_boundary_add50: int = 20, enable_close: int = 1,
                 period: int = 30, interval: Interval = Interval.MINUTE, reverse_bs: int = 0,
                 filter_n_available=1, **kwargs):
        """"""

        self.fastk_period = fastk_period if fastk_period != 0 else 9
        self.slowk_period = slowk_period if slowk_period != 0 else 3
        self.slowd_period = slowd_period if slowd_period != 0 else 3
        if higher_boundary_add50 is None or higher_boundary_add50 == 0:
            higher_boundary_add50 = 20

        self.higher_boundary = 50 + higher_boundary_add50
        self.lower_boundary = 50 - higher_boundary_add50
        self.enable_close = enable_close
        self.reverse_bs = reverse_bs

        period = period if period != 0 else 30
        size = self.fastk_period + self.slowk_period + self.slowd_period
        super().__init__(period=period, array_size=size, interval=interval, filter_n_available=filter_n_available,
                         **kwargs)
        # logger.info(f"fast_window, slow_window, signal_period, period="
        #             f"{self.fast_window, self.slow_window, self.signal_period, self.period}")
        self._k, self._d, self._j = None, None, None

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            self.set_signal_pos(0)
            return

        k, d, j = self.am.kdj(self.fastk_period, self.slowk_period, self.slowd_period)
        if self._k is None:
            self._k, self._d, self._j = k, d, j
            return
        if k > d and self._k < self._d and self._k < self.lower_boundary:
            # 低位金叉
            self.set_signal_pos(-1 if self.reverse_bs else 1)
        elif k < d and self._k > self._d and self._k > self.higher_boundary:
            # 高位死叉
            self.set_signal_pos(1 if self.reverse_bs else -1)
        elif self.enable_close:
            pos = self.get_signal_pos()
            if pos != 0:
                if self.reverse_bs:
                    pos = -pos

                if pos > 0 and k < d and self._k > self._d:
                    # 死叉 平 多仓
                    self.set_signal_pos(0)
                elif pos < 0 and k > d and self._k < self._d:
                    # 金叉 平 空仓
                    self.set_signal_pos(0)

        self._k, self._d, self._j = k, d, j


class RSISignal(CtaSignal):
    """"""
    short_name = "rsi"

    def __init__(self, win_size: int = 9,
                 higher_boundary_add50: int = 20, period: int = 30,
                 enable_close: int = 0, interval: Interval = Interval.MINUTE, reverse_bs: int = 0,
                 filter_n_available=1, **kwargs):
        """"""
        self.win_size = win_size if win_size != 0 else 9
        self.interval = interval if interval != 0 else Interval.MINUTE
        self.higher_boundary = 50 + (higher_boundary_add50 if higher_boundary_add50 != 0 else 20)
        self.lower_boundary = 50 - (higher_boundary_add50 if higher_boundary_add50 != 0 else 20)
        self.enable_close = enable_close
        self.reverse_bs = reverse_bs

        period = period if period != 0 else 30
        size = win_size + 1
        super().__init__(period=period, array_size=size, interval=interval, filter_n_available=filter_n_available,
                         **kwargs)
        # logger.info(f"fast_window, slow_window, signal_period, period="
        #             f"{self.fast_window, self.slow_window, self.signal_period, self.period}")

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            self.set_signal_pos(0)
            return

        value = self.am.rsi(self.win_size)
        if value < self.lower_boundary:
            # 低位
            self.set_signal_pos(1 if self.reverse_bs else -1)
        elif value > self.higher_boundary:
            # 高位
            self.set_signal_pos(-1 if self.reverse_bs else 1)
        elif self.enable_close:
            pos = self.get_signal_pos()
            if self.reverse_bs:
                pos = -pos

            if pos > 0 and value < 50:
                # 平 多仓
                self.set_signal_pos(0)
            elif pos < 0 and value > 50:
                # 平 空仓
                self.set_signal_pos(0)


class BOLLSignal(CtaSignal):
    """"""
    short_name = "boll"

    def __init__(
            self, win_size: int = 26, dev: float = 1,
            period: int = 30, interval: Interval = Interval.MINUTE, reverse_bs: int = 0,
            filter_n_available=1, **kwargs):
        """"""
        self.win_size = win_size
        self.interval = interval
        self.dev = dev
        self.reverse_bs = reverse_bs

        size = win_size + 1
        super().__init__(period=period, array_size=size, interval=interval, filter_n_available=filter_n_available,
                         **kwargs)
        # logger.info(f"fast_window, slow_window, signal_period, period="
        #             f"{self.fast_window, self.slow_window, self.signal_period, self.period}")

    def on_window(self, bar: BarData):
        """"""
        super().on_window(bar)
        if not self.am.inited:
            self.set_signal_pos(0)
            return

        close = bar.close_price
        up, down = self.am.boll(self.win_size, self.dev)
        if close > up:
            # 低位
            self.set_signal_pos(-1 if self.reverse_bs else 1)
        elif close < down:
            # 高位
            self.set_signal_pos(1 if self.reverse_bs else -1)
        else:
            pos = self.get_signal_pos()
            pos = -pos if self.reverse_bs else pos
            mid = (up + down) / 2
            if pos > 0 and close < mid:
                self.set_signal_pos(0)
            elif pos < 0 and close > mid:
                self.set_signal_pos(0)


class MACrossSignal(CtaSignal):
    """
    signal_pos >=1:金叉， <=-1:死叉, 0 无交叉
    数字的绝对值为距离上一个金叉或死叉的距离
    """

    short_name = "macma"

    def __init__(self, fast, slow, array_size: typing.Optional[int] = None, period=1,
                 interval: Interval = Interval.MINUTE, reverse_bs: int = 0, same_direction=False, **kwargs):
        self.fast = fast
        self.slow = slow
        self.reverse_bs = reverse_bs
        self.same_direction = same_direction
        if not array_size:
            array_size = max(fast, slow) + 1

        super().__init__(period=period, array_size=array_size, interval=interval,
                         **kwargs)

    def on_window(self, bar: BarData):
        super().on_window(bar)
        if not self.am.inited:
            self.set_signal_pos(0)
            return

        fast_ma = self.am.sma(self.fast, array=True)
        slow_ma = self.am.sma(self.slow, array=True)
        flag = is_cross(fast_ma, slow_ma, self.same_direction)
        if flag == 1:
            # 金叉
            self.set_signal_pos(-1 if self.reverse_bs else 1)
        elif flag == -1:
            # 死叉
            self.set_signal_pos(1 if self.reverse_bs else -1)
        else:
            pass


if __name__ == "__main__":
    pass
