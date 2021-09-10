"""
@author  : MG
@Time    : 2020/11/16 10:20
@File    : template.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import math
import threading
import time
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from ibats_utils.decorators import thread_save
from ibats_utils.mess import datetime_2_str, obj_2_json
from vnpy.app.portfolio_strategy import StrategyEngine
from vnpy.app.portfolio_strategy import StrategyTemplate as StrategyTemplateBase
from vnpy.trader.constant import Direction, Offset, Interval
from vnpy.trader.object import BarData, TickData, TradeData

from vnpy_extra.constants import STOP_OPENING_POS_PARAM, ENABLE_COLLECT_DATA_PARAM
from vnpy_extra.backtest import StopOpeningPos, check_datetime_trade_available, generate_mock_load_bar_data
from vnpy_extra.config import logging
from vnpy_extra.constants import GeneralPeriodEnum, BASE_POSITION
from vnpy_extra.db.orm import AccountStrategyStatusEnum
from vnpy_extra.report.collector import trade_data_collector, order_data_collector, latest_price_collector
from vnpy_extra.report.monitor import AccountStrategyStatusMonitor
from vnpy_extra.utils.enhancement import BarGenerator, ArrayManager, get_daily_min_bar_count
from vnpy_extra.utils.symbol import PATTERN_SYMBOL_CALL_PUT_SPLIT


class StrategyTemplate(StrategyTemplateBase):
    # 该标识位默认为0（关闭状态）。为1时开启，程序一旦平仓后则停止后续交易。该标识位用于在切换合约时使用
    stop_opening_pos = StopOpeningPos.open_available.value
    # 考虑到六、周日、节假日等非交易日因素，保险起见，建议初始化日期 * 2 + 7
    init_load_days = 30
    # 加载主连连续合约作为合约历史行情数据（默认为False)
    load_main_continuous_md = False
    # 对应周期类型
    period_enum = None
    # 周期级别（如果设置 period_enum，则该字段无效）
    interval = None
    # 周期大小（如果设置 period_enum，则该字段无效）
    window = None
    # ArrayManager 队列长度
    array_size = 100
    # 如果 setting 里面有不在 parameters 里面的字段，则报错。这个开关主要是为了防止出现参数定义错误导致的无效回测
    raise_error_if_setting_not_in_parameters = True
    # 初始化加载数据日期跨度（天）。0代表关闭此功能。
    # 此功能主要是为了节省缓存空间，多个策略可以产生同一个初始化天数，从而减少数据库加载量，以及内存中的数据缓存空间。
    load_days_span = 30
    # 建仓基数，建立空头或多头仓位的数量
    base_position = 1

    def __init__(
            self,
            strategy_engine: StrategyEngine,
            strategy_name: str,
            vt_symbols: List[str],
            setting: dict
    ):
        self.logger_name = f'strategies.portfolio.{self.__class__.__name__}' \
            if self.__class__.__name__ == strategy_name \
            else f'strategies.portfolio.{self.__class__.__name__}.{strategy_name}'
        self.logger = logging.getLogger(self.logger_name)
        if STOP_OPENING_POS_PARAM not in self.parameters:
            self.parameters.append(STOP_OPENING_POS_PARAM)  # 增加 stop_opening_pos 用于合约切换是关闭当前线程

        if BASE_POSITION not in self.parameters:
            self.parameters.append(BASE_POSITION)

        if self.raise_error_if_setting_not_in_parameters:
            mismatch = False
            for _ in setting.keys():
                if _ in {'class_name', }:
                    continue
                if _ not in self.parameters:
                    self.logger.error(f"setting中 {_} 字段未在 parameters 中定义，请检查 setting 字段是否设置正确")
                    mismatch = True

            if mismatch:
                raise ValueError(f"setting.keys()={setting.keys()}\nparameters={self.parameters} 不匹配")

        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        # setting 不包含 stop_opening_pos key
        self.setting = {k: v for k, v in setting.items() if k in self.parameters}
        # 写日志
        self.logger.info(f"{strategy_name} on {vt_symbols} setting=\n{obj_2_json(setting, indent=4)}")
        # 仅用于 on_order 函数记录上一个 order 使用，解决vnpy框架重复发送order的问题
        self._last_order = {}
        self.received_trade_list = []  # 记录所有成交数据
        # 1分钟 bar 对象字典及bar数量
        self.current_bars: Optional[Dict[str, BarData]] = None
        self.bar_count = 0
        # 生成指定周期 bar 对象字典及 win bar 数量
        self.current_win_bars: Optional[Dict[str, BarData]] = None
        self.win_bar_count = 0
        # 是否实盘环境
        self._is_realtime_mode = self.strategy_name is not None and self.strategy_name != self.__class__.__name__
        self._strategy_status = AccountStrategyStatusEnum.Created
        # 是否收集申请单以及交易单记录
        self.enable_collect_data = ENABLE_COLLECT_DATA_PARAM in setting and setting[ENABLE_COLLECT_DATA_PARAM]
        self._strategy_status_monitor: Optional[AccountStrategyStatusMonitor] = None
        self._lock: Optional[threading.Lock] = None

        # 最近一个tick的时间
        self.last_tick_time: Optional[datetime] = None
        # 最近一次下单的时间
        self.last_order_dt: Dict[str, datetime] = {}
        # 最近一条提示信息
        self._log_dt_dic = defaultdict(lambda: datetime.now())
        self._logs_recent = []
        self._log_cache_size = 20
        # 是否主力合约元祖
        self.symbol_is_main_tuples: Optional[Tuple[Tuple[str, bool], Tuple[str, bool]]] = None
        self.latest_tick_dic: Dict[str, TickData] = {}

        def on_bar(bar: BarData):
            """"""
            pass

        self.bgs: Dict[str, BarGenerator] = {}
        self.ams: Dict[str, ArrayManager] = {}
        if self.period_enum is not None:
            period_enum: GeneralPeriodEnum = GeneralPeriodEnum[self.period_enum]
            self.window, self.interval = period_enum.value

        self._win_bars = {}
        for vt_symbols in self.vt_symbols:
            self.bgs[vt_symbols] = BarGenerator(
                on_bar, window=self.window, interval=self.interval, on_window_bar=self._on_win_bar)
            if self.array_size is not None:
                self.ams[vt_symbols] = ArrayManager(self.array_size)
            self._win_bars[vt_symbols] = None

    def set_is_realtime_mode(self, is_realtime_mode):
        self._is_realtime_mode = is_realtime_mode

    def get_id_name(self):
        """获取 id_name"""
        param_str = '_'.join([
            str(self.setting[key]) for key in self.parameters
            if key in self.setting and key != STOP_OPENING_POS_PARAM])
        id_name = f"{self.__class__.__name__}_{param_str}" if param_str != "" else f"{self.__class__.__name__}"
        return id_name

    def _set_strategy_status(self, status: AccountStrategyStatusEnum):
        if not self._is_realtime_mode:
            # 仅针对实时交易是使用
            return
        if self._strategy_status == status:
            return

        if status == AccountStrategyStatusEnum.RunPending and self._strategy_status not in (
                AccountStrategyStatusEnum.Created, AccountStrategyStatusEnum.Running
        ):
            # AccountStrategyStatusEnum.RunPending 状态只从数据库端发起
            if self._lock is not None:
                self._lock.acquire()

            try:
                # 保险起见，为防止出现死循环调用，在 on_start 先把状态调整过来
                self._strategy_status = status
                self.write_log(f"策略 {self.vt_symbols} 状态 "
                               f"{self._strategy_status.name} -> {status.name} 被远程启动")
            finally:
                if self._lock is not None:
                    self._lock.release()

            self.on_start()

        elif status == AccountStrategyStatusEnum.StopPending and self._strategy_status == AccountStrategyStatusEnum.Running:
            # AccountStrategyStatusEnum.StopPending 状态只从数据库端发起
            if self._lock is not None:
                self._lock.acquire()

            try:
                # 保险起见，为防止出现死循环调用，在 on_stop 先把状态调整过来
                self._strategy_status = status
                self.write_log(f"策略 {self.vt_symbols} 状态 "
                               f"{self._strategy_status.name} -> {status.name} 被远程停止")
            finally:
                if self._lock is not None:
                    self._lock.release()

            self.on_stop()
        else:
            self.write_log(f"策略 {self.vt_symbols} 状态 "
                           f"{self._strategy_status.name} -> {status.name}")
            self._strategy_status = status

    def _get_strategy_status(self) -> AccountStrategyStatusEnum:
        return self._strategy_status

    def on_init(self) -> None:
        super().on_init()
        self.bar_count = 0
        if self._is_realtime_mode:
            self._set_strategy_status(AccountStrategyStatusEnum.Initialized)

        if self._is_realtime_mode and self._strategy_status_monitor is None:
            # 该语句一定不能放在 __init__ 中
            # 因为 strategy_name 在回测阶段模块中，在 __init__ 后可能会被重写赋值
            self._strategy_status_monitor = AccountStrategyStatusMonitor(
                self.strategy_name,
                self._get_strategy_status,
                self._set_strategy_status,
                self.vt_symbols,
                self.setting
            )
            self._lock = self._strategy_status_monitor.lock

        if self._strategy_status_monitor is not None and not self._strategy_status_monitor.is_alive():
            self._strategy_status_monitor.start()

        self.enable_collect_data |= self._is_realtime_mode
        if self.enable_collect_data:
            trade_data_collector.queue_timeout = 90 if self._is_realtime_mode else 1
            order_data_collector.queue_timeout = 90 if self._is_realtime_mode else 1

        if self.init_load_days > 0:
            if self.load_days_span > 0:
                self.init_load_days = math.ceil(self.init_load_days / self.load_days_span) * self.load_days_span

            if self._is_realtime_mode and self.load_main_continuous_md:
                with generate_mock_load_bar_data(self.write_log, symbol_is_main_tuples=self.symbol_is_main_tuples):
                    self.load_bars(self.init_load_days)
            else:
                self.load_bars(self.init_load_days)

            self.write_log(f"策略初始化完成. 加载{self.init_load_days}天数据")

    def on_start(self) -> None:
        super().on_start()
        if self._is_realtime_mode:
            self._set_strategy_status(AccountStrategyStatusEnum.Running)
        # 整理持仓信息
        if len(self.pos) == 0:
            self.write_log(f"策略启动，当前初始持仓：(无)")
        else:
            pos_str = '\t'.join([f"{k}: {v}" for k, v in self.pos.items()])
            self.write_log(f"策略启动，当前初始持仓：\n{pos_str}")

        self.put_event()

        # 初始化相关数据,可以在重启策略时清空历史订单对当前策略的影响.
        # 仅用于 on_order 函数记录上一个 order 使用，解决vnpy框架重复发送order的问题
        self._last_order = {}
        self.received_trade_list = []  # 记录所有成交数据
        # 最近一次下单的时间
        self.last_order_dt: Dict[str, datetime] = {}
        # if self._is_realtime_mode:
        #     start_strategy_position_monitor()

    def on_tick(self, tick: TickData) -> bool:
        """判断当前tick数据是否有效,如果无效数据直接返回 False,否则更新相应bar数据"""
        super().on_tick(tick)
        is_available = check_datetime_available(tick.datetime)
        if not is_available:
            return is_available

        self.latest_tick_dic[tick.vt_symbol] = tick
        if (
                self.last_tick_time
                and self.last_tick_time.minute != tick.datetime.minute
        ):
            bars, all_none = {}, False
            for vt_symbol, bg in self.bgs.items():
                bars[vt_symbol] = bar = bg.generate()
                if bar is not None:
                    all_none = False

            if not all_none:
                self.on_bars(bars)

        bg: BarGenerator = self.bgs[tick.vt_symbol]
        bg.update_tick(tick)
        latest_price_collector.put_nowait(tick)
        self.last_tick_time = tick.datetime.replace(tzinfo=None)
        return is_available

    def on_bars(self, bars: Dict[str, BarData]) -> None:
        super().on_bars(bars)
        self.current_bars: Dict[str, BarData] = bars
        self.bar_count += 1
        for vt_symbol, bar in bars.items():
            if bar is not None:
                self.bgs[vt_symbol].update_bar(bar)

    def _on_win_bar(self, bar: BarData):
        """
        激活 on_win_bars 函数
        逻辑:
        通过 bg 生成对应 vt_symbol 的 win bar,当全部 vt_symbol 的 win bar 均生成完毕后,触发 on_win_bars 函数
        由于 on_tick 阶段 通过 gb.generate() 强行在同一时刻生成了所有 bar,因此可以保证,当生成对应 win bar 时,也会是同时生成,
        因此,此处不考虑部分生成的情况
        """
        self._win_bars[bar.vt_symbol] = bar
        bar_dt = None
        for bar in list(self._win_bars.values()):
            if bar is None:
                break
            if bar_dt is None:
                bar_dt = bar.datetime
            elif bar_dt != bar.datetime:
                # 判断bar时间是否同步
                break
        else:
            ret = self.on_win_bars(self._win_bars)
            if ret is None or ret:
                self.on_win_bars_finished(self._win_bars)
            else:
                self.on_win_bars_failed(self._win_bars)

            self._win_bars = {_: None for _ in self._win_bars.keys()}

    def on_win_bars(self, bars: Dict[str, BarData]) -> Optional[bool]:
        self.current_win_bars: Dict[str, BarData] = bars
        self.win_bar_count += 1
        for vt_symbols, bar in bars.items():
            if vt_symbols in self.ams:
                self.ams[vt_symbols].update_bar(bar)

        return True

    def on_win_bars_finished(self, bars: Dict[str, BarData]) -> None:
        """对 on_win_bars 逻辑进行收尾处理"""
        pass

    def on_win_bars_failed(self, bars: Dict[str, BarData]) -> None:
        """对 on_win_bars 逻辑进行异常处理"""
        pass

    def send_order(self,
                   vt_symbol: str,
                   direction: Direction,
                   offset: Offset,
                   price: float,
                   volume: float,
                   lock: bool = False
                   ) -> List[str]:
        current_pos = int(self.get_pos(vt_symbol))
        order_datetime = self.current_bars[vt_symbol].datetime if (
                self.current_bars is not None
                and vt_symbol in self.current_bars
                and self.current_bars[vt_symbol] is not None) else None
        ignore_order = False
        if price <= 0.0:
            log_level = 'error'
            msg = '【价格无效】【忽略该订单】'
            ignore_order = True
        elif order_datetime is not None and not check_datetime_trade_available(order_datetime):
            # 回测模式下提示此类信息
            log_level = 'warning' if self._is_realtime_mode else 'debug'
            msg = '【非交易时段】【忽略该订单】'
            ignore_order = True
        elif self.stop_opening_pos != StopOpeningPos.open_available.value and offset == Offset.OPEN:
            log_level = 'warning'
            msg = '【禁止开仓】【忽略该订单】'
            ignore_order = True
        else:
            log_level = 'debug'
            msg = ''

        order_volume = volume if direction == Direction.LONG else -volume
        if offset == Offset.OPEN:
            if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                self.write_log(
                    f"send_order {vt_symbol:>11s} {direction.value} {offset.value:4s} {price:.1f} "
                    f"{current_pos:+d} {order_volume:+.0f}{msg}"
                    if order_datetime is None else
                    f"send_order {datetime_2_str(order_datetime)} {vt_symbol} {direction.value} {offset.value:4s} {price:.1f} "
                    f"{current_pos:+d} {order_volume:+.0f}{msg}",
                    log_level
                )

            if self.stop_opening_pos != StopOpeningPos.open_available.value:
                self.write_log(f"当前策略 stop_opening_pos="
                               f"{self.stop_opening_pos}<{StopOpeningPos(self.stop_opening_pos).name}>，"
                               f"所有开仓操作将被屏蔽（用于主力合约切换,或关闭失效策略使用）", log_level)
                self.stop_opening_pos = StopOpeningPos.stop_opening_and_nolog.value

        else:
            self.write_log(
                f"send_order {vt_symbol:>11s} {direction.value} {offset.value:4s} {price:.1f} "
                f"      {current_pos:+d} {order_volume:+.0f}{msg}"
                if order_datetime is None else
                f"send_order {datetime_2_str(order_datetime)} {vt_symbol} {direction.value} {offset.value:4s} {price:.1f} "
                f"      {current_pos:+d} {order_volume:+.0f}{msg}",
                log_level
            )

        if order_datetime is None:
            order_datetime = datetime.now()

        if ignore_order:
            return []

        if vt_symbol in self._last_order:
            # 记录订单情况，跳过重复订单
            last_order = self._last_order[vt_symbol]
            if last_order['direction'] != direction.value \
                    or last_order['offset'] != offset.value \
                    or last_order['price'] != price \
                    or last_order['volume'] != volume:
                is_not_duplicate_order = True
            else:
                is_not_duplicate_order = False
        else:
            is_not_duplicate_order = True

        if is_not_duplicate_order:
            symbol, exchange = vt_symbol.split('.')
            order = {
                "datetime": order_datetime,
                "symbol": symbol,
                "exchange": exchange,
                "direction": direction.value,
                "offset": offset.value,
                "price": price,
                "volume": volume,
            }
            if self.enable_collect_data:
                order_data_collector.put_nowait(self.strategy_name, order)

            self._last_order[vt_symbol] = order

        self.last_order_dt[vt_symbol] = datetime.now()
        return super().send_order(vt_symbol, direction, offset, price, volume, lock)

    def on_stop(self):
        super().on_stop()
        if self._is_realtime_mode:
            self._set_strategy_status(AccountStrategyStatusEnum.Stopped)
        self.put_event()

    def update_trade(self, trade: TradeData):
        super().update_trade(trade)
        self.received_trade_list.append(trade)
        if self.enable_collect_data:
            trade_data_collector.put_nowait(self.strategy_name, trade)

    def write_log(self, msg: str, logger_method='info'):
        if (datetime.now() - self._log_dt_dic[msg]).seconds > 1:
            # 在缓存之内直接忽略
            return

        if len(self._logs_recent) > self._log_cache_size:
            # 清理缓存
            del self._log_dt_dic[self._logs_recent.pop(0)]

        try:
            super().write_log(msg)
        except AttributeError:
            # create_instance 的方法建立实例时可能引发如下异常：
            #   File "D:\IDE\vnstudio\lib\site-packages\vnpy\app\portfolio_strategy\template.py", line 231, in write_log
            #     self.strategy_engine.write_log(msg, self)
            # AttributeError: 'NoneType' object has no attribute 'write_log'
            pass

        new_msg = f"{self.strategy_name} {msg}"
        getattr(self.logger, logger_method)(new_msg)
        self._last_msg = msg

    def is_available(self, stats: dict, df: pd.DataFrame) -> bool:
        max_drawdown_end = stats.get("max_drawdown_end", -1)
        max_drawdown_end_gross = stats.get("max_drawdown_end_gross", -1)
        # 普通收益率曲线，或去极值收益率曲线两种有一个满足条件即可认为是有效策略
        is_available = bool(
            stats.get("total_return", 0) > 0
            and stats["daily_trade_count"] > 0.2  # 1/0.2 每一次交易平仓再开仓需要2次交易，因此相当于10天交易一次
            and stats["return_drawdown_ratio"] > 1.5
            and stats["max_new_higher_duration"] < 180  # 最长不创新高周期<180
            and stats["max_new_higher_duration"] / stats[
                "total_days"] < 0.5  # 最长不创新高周期超过一半的总回测天数
            and df is None  # 没有交易
            and np.sum(df["profit"] <= 0) / stats["total_days"] < 0.5  # 50%以上交易日处于亏损状态
            # 最大回撤到最后一个交易日需要出现新高
            and (np.any(df["drawdown"][max_drawdown_end:] > 0) if max_drawdown_end > 0 else True)
        ) or bool(
            stats.get("total_return_gross", 0) > 0
            and stats[
                "daily_trade_count_gross"] > 0.2  # 1/0.2 每一次交易平仓再开仓需要2次交易，因此相当于10天交易一次
            and stats["return_drawdown_ratio_gross"] > 1.5
            and stats["max_new_higher_duration_gross"] < 180  # 最长不创新高周期<180
            and stats["max_new_higher_duration_gross"] / stats[
                "total_days"] < 0.5  # 最长不创新高周期超过一半的总回测天数
            and df is None  # 没有交易
            and np.sum(df["profit_gross"] <= 0) / stats[
                "total_days"] < 0.5  # 50%以上交易日处于亏损状态
            # 最大回撤到最后一个交易日需要出现新高
            and (np.any(df["drawdown_gross"][max_drawdown_end_gross:] > 0) if max_drawdown_end_gross > 0 else True)
        )
        return is_available

    def get_daily_bar_count(self) -> int:
        """返回当前周期下每天的bar数量"""
        if self.interval == Interval.MINUTE:
            bar_count = int(np.ceil(max([get_daily_min_bar_count(_) for _ in self.vt_symbols]) / self.window))
        elif self.interval == Interval.HOUR:
            bar_count = int(np.ceil(max([get_daily_min_bar_count(_) for _ in self.vt_symbols]) / 60 / self.window))
        elif self.interval == Interval.DAILY:
            bar_count = 1
        elif self.interval == Interval.WEEKLY:
            bar_count = 1 / 7
        else:
            raise ValueError(f"interval={self.interval} 无效")

        return bar_count

    def calc_init_load_days(self):
        """返回至少需要多少日线数据"""
        if self.interval in (Interval.MINUTE, Interval.HOUR):
            min_bar_count = self.get_daily_bar_count()
            step = 1 / min_bar_count
        elif self.interval == Interval.DAILY:
            step = 1
        elif self.interval == Interval.WEEKLY:
            step = 7
        else:
            raise ValueError(f"interval={self.interval} 无效")

        daily_bar_count = math.ceil(self.window * self.array_size * step)
        if self.interval != Interval.WEEKLY:
            daily_bar_count *= 1.5

        return daily_bar_count


class TargetPosAndPriceTemplate(StrategyTemplate):
    # 该参数仅用于回测时使用（0，两腿同时下单，1：分不同的bar下单）
    handle_order_one_by_one = 0
    # 保持最近的 n 个tick 用于算法交易中进行成交难度评估使用, 0.5秒一个tick
    tick_arr_len = 60 * 2

    # 算法交易部分配置信息
    # 最大可容忍配对交易不平衡时间（秒）
    mismatch_endure_seconds = 20
    # 主动成交订单等待时长（秒）
    active_order_wait_seconds = 5

    variables = ["vt_symbols", "targets"]

    def __init__(
            self,
            strategy_engine: StrategyEngine,
            strategy_name: str,
            vt_symbols: List[str],
            setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        if "targets" not in self.variables:
            # 使用 TargetPosAndPriceTemplate 目标，targes 变量必须在 variables 列表中，否则会出现隔夜目标持仓数据丢失的情况。
            self.variables.append("targets")

        self.vt_symbol_count = len(vt_symbols)
        # 目标仓位
        self.targets: Dict[str, Tuple[int, Optional[float]]] = {}
        # 目标仓位刷新标识
        self.target_refreshed = False
        # 合约对不匹配的起始时间
        self.active_order_waiting_since_dt_dict: Dict[str, Optional[datetime]] = defaultdict(lambda: None)
        # 单腿情况下，首次尝试盘口成交时，使用盘口挂单方式成交（尝试一次不行后，该为盘口对价成交）
        self.use_market_active_order = False
        # 保存最近n个tick 价格及交易量数据用于计算开仓优先级
        # 其中 np.ndarray 是一个 np.zeros((tick_arr_len, 2)) 第一列是 价格，第二列是成交量
        self.tick_arr: Dict[str, np.ndarray] = {}
        # 成交难度系数。下单时，选择难度系数最高的先下单
        self.deal_difficult_ratio: Dict[str, Tuple[float, datetime]] = {}
        for vt_symbol in self.vt_symbols:
            self.targets[vt_symbol] = (0, 0.0)
            # last_price, last_volume
            self.tick_arr[vt_symbol] = np.zeros((self.tick_arr_len, 2))
            self.deal_difficult_ratio[vt_symbol] = (-1, datetime.now())

        self._estimate_seconds_arr = np.zeros(self.vt_symbol_count)
        self._estimate_deal_seconds_dt = datetime.now()
        # 算法交易线程
        self.algo_trading_thread = None
        self.algo_trading_running = True
        self.seconds_since_last_tick = 0

    @property
    def order_waiting_since(self):
        return {_: datetime_2_str(dt) for _, dt in self.active_order_waiting_since_dt_dict.items()}

    @order_waiting_since.setter
    def order_waiting_since(self, val):
        pass

    @thread_save
    def _handle_active_order(self, vt_symbol_list: List[str]):
        """执行主动单"""
        if len(vt_symbol_list) > 0:
            self.write_log(f"建立组合头寸 {vt_symbol_list} 主动交易。", 'debug')

        for vt_symbol in vt_symbol_list:
            waiting_since_dt = self.active_order_waiting_since_dt_dict[vt_symbol]
            if waiting_since_dt is None:
                self.active_order_waiting_since_dt_dict[vt_symbol] = datetime.now()
                mismatched_seconds = 0
            else:
                mismatched_seconds = (datetime.now() - waiting_since_dt).seconds

            # 是否超过被动交易可忍受时限
            intolerable = mismatched_seconds > self.mismatch_endure_seconds
            no_relative_order = True
            if len(self.active_orderids) > 0:
                for orderid in self.get_all_active_orderids():
                    order = self.get_order(orderid)
                    if order is None:
                        continue
                    if order.vt_symbol == vt_symbol:
                        no_relative_order = False

            if no_relative_order:
                if intolerable:
                    # 超过时限，对价主动成交
                    self.write_log(f"{self.get_vt_symbol_target_pos_str(vt_symbol)} 超过被动交易时限，对价主动成交")
                    self._handle_pos_2_target(vt_symbol, market_price=True, activate=self.use_market_active_order)
                    # 单腿情况下，首次尝试盘口成交时，使用盘口挂单方式成交（尝试一次不行后，该为盘口对价成交）
                    self.use_market_active_order = True
                else:
                    # 限价被动成交
                    self.write_log(f"{self.get_vt_symbol_target_pos_str(vt_symbol)} 在容忍时限内，限价被动交易")
                    self._handle_pos_2_target(vt_symbol)
            else:
                # 当前合约已存在订单，等待成交 或 取消订单重新下单
                # 距离上一次下单时间
                if vt_symbol in self.last_order_dt:
                    last_order_seconds = (datetime.now() - self.last_order_dt[vt_symbol]).seconds
                    order_wait_timeout = self.active_order_wait_seconds < last_order_seconds
                else:
                    order_wait_timeout = True

                if intolerable and order_wait_timeout:
                    self.write_log(f"{self.get_vt_symbol_target_pos_str(vt_symbol)} 单腿等待超时，撤单重下")
                    # self.cancel_all()
                    self.cancel_order_by_vt_symbol(vt_symbol)

    @thread_save
    def _handle_passive_order(self, vt_symbol_list: List[str]):
        """执行被动单（同时用于回测及实盘）"""
        if len(self.active_orderids) == 0:
            # 首次开仓
            if len(vt_symbol_list) > 0:
                self.write_log(f"建立组合头寸 {vt_symbol_list} 被动交易。", 'debug')
                for vt_symbol in vt_symbol_list:
                    self._handle_pos_2_target(vt_symbol)

            self.target_refreshed = False

        else:
            # 有开仓，等待成交，同时又有新的目标仓位更新
            if self.target_refreshed:
                # 如果超时，则重新下单
                # 检查新下单的价格是否与就单子相同，如果相同则不用 撤销重下单，继续等待即可
                # 注意：这里 list(self.active_orderids) 其中 list() 不能去掉，
                #       因为内部会 cancel_order(order.orderid) 造成 active_orderids 变化会抛异常
                for active_orderid in list(self.active_orderids):
                    order = self.get_order(active_orderid)
                    if order is None:
                        continue
                    if order.vt_symbol not in self.targets:
                        self.write_log(
                            f"active_orderid={active_orderid}[{order.vt_symbol}] "
                            f"{order.direction.value} {order.offset.value} {order.price} {order.volume}"
                            f"沒有找到对应的 targets 信息",
                            'warning')
                        continue
                    target_pos, target_price = self.targets[order.vt_symbol]
                    if order.price != target_price:
                        # 不要在订单取消后面直接下单，
                        # 因为 cancel_order 可能会失败，引发导致重复下单的情况。
                        # 订单取消成功后,通过 if len(self.active_orderids) == 0 状态进行重新下单
                        # 重新下单后 self.target_refreshed = False
                        # 发现 cancel_order(order.orderid) 总是找不到订单导致撤单失败
                        # self.cancel_order(order.orderid)
                        self.write_log(
                            f"{self.get_vt_symbol_target_pos_str(order.vt_symbol)} 价格已被刷新，取消旧订单[{active_orderid}]",
                            'debug')
                        self.cancel_all()

    def _algo_trading_2_target_pos_thread(self):
        self.write_log("开启算法交易")
        try:
            while self.algo_trading_running:
                time.sleep(0.5)
                if not self.trading:
                    continue

                if self.last_tick_time is None:
                    # 未开盘期间不进行算法交易
                    continue
                now = datetime.now().replace(tzinfo=self.last_tick_time.tzinfo)
                # 多线程情况下可能存在 last_tick_time > now 的情况，因此用绝对值
                self.seconds_since_last_tick = abs(now - self.last_tick_time).seconds
                if self.seconds_since_last_tick > 5:
                    continue
                self._algo_trading_2_target_pos()
        except:
            self.write_log(f"算法交易异常", 'error')
            self.logger.exception("%s 算法交易异常", self.strategy_name)
        finally:
            self.write_log("关闭算法交易", 'warning')

    def _estimate_deal_seconds_all(self) -> np.ndarray:
        """计算各个合约成交时间，生成与 self.vt_symbols 等长的 array
        -1 代表无法确定
        0 代表即时成交
        正数，代表预估相应秒左右成交
        """
        if (datetime.now() - self._estimate_deal_seconds_dt).seconds > 1:
            return self._estimate_seconds_arr
        for num, vt_symbol in enumerate(self.vt_symbols):
            self._estimate_seconds_arr[num] = self._estimate_deal_seconds(vt_symbol)

        self._estimate_deal_seconds_dt = datetime.now()
        return self._estimate_seconds_arr

    def _estimate_deal_seconds_all_backtest_only(self) -> np.ndarray:
        """通过最近一个bar判断成交难度（仅用于回测）"""
        for num, vt_symbol in enumerate(self.vt_symbols):
            try:
                target_pos, target_price = self.targets[vt_symbol]
            except KeyError:
                continue
            target_price = np.round(target_price, 2)
            current_pos = self.get_pos(vt_symbol)
            bar = self.current_bars[vt_symbol]
            pos_diff = target_pos - current_pos
            if pos_diff > 0:
                # 做多或平空
                # 当前bar 涨得越多，意味着越难成交
                seconds = 0 if target_price > bar.close_price else abs(target_price - bar.close_price)
            elif pos_diff < 0:
                # 做空或平多
                # 当前bar 涨得越多，意味着越易成交
                seconds = 0 if target_price < bar.close_price else abs(target_price - bar.close_price)
            else:
                seconds = -1

            self._estimate_seconds_arr[num] = seconds

        return self._estimate_seconds_arr

    def get_vt_symbol_target_pos_str(self, vt_symbol):
        return f"{vt_symbol}[{self.get_pos(vt_symbol)} -> {self.targets[vt_symbol][0]}] " \
               f"{self.targets[vt_symbol][1]:.2f}"

    def _generate_active_passive_symbols(self) -> Tuple[List[str], List[str]]:
        """生成主动成交合约列表、被动成交合约列表"""
        # 检查持仓
        # 计算是否存在仓位不匹配情况
        # 首先分别计算 symbol1, symbol2, ..., symboln 的仓位差
        active_symbols, passive_symbols, mismatch_symbols = [], [], []
        target_count = len(self.targets)
        pos_diff_arr = np.zeros(target_count)
        current_pos_arr = np.zeros(target_count)
        for num, (vt_symbol, (target_pos, target_price)) in enumerate(self.targets.items()):
            current_pos_arr[num] = current_pos = self.get_pos(vt_symbol)
            pos_diff_arr[num] = pos_diff = target_pos - current_pos
            if pos_diff != 0 and target_price > 0:
                # 价格 <= 0 的目标合约为无效合约
                mismatch_symbols.append(vt_symbol)

        pos_diff_abs_arr = np.abs(pos_diff_arr)
        if np.all(pos_diff_abs_arr == 0):
            # 没有需要操作的合约或订单
            self.cancel_all()
            self.active_order_waiting_since_dt_dict: Dict[str, Optional[datetime]] = defaultdict(lambda: None)
            self.target_refreshed = False
            # 单腿情况下，首次尝试盘口成交时，使用盘口挂单方式成交（尝试一次不行后，该为盘口对价成交）
            self.use_market_active_order = False
            return active_symbols, passive_symbols

        # 确定哪一条是主动腿，哪一条是被动腿。判断逻辑如下：
        # 是否为初始开仓交易阶段
        is_open_pos = np.all(current_pos_arr == 0)
        # 是否为初始关仓交易阶段
        is_close_pos = np.all(current_pos_arr != 0)
        is_not_init_open_or_close_pos = not (is_open_pos or is_close_pos)
        # 首先做是否单腿判断
        if is_not_init_open_or_close_pos:
            # 如果 leg1 leg2 ... leg n 数量不匹配，即，存在单腿，以瘸腿的一个为主动腿，另一条为被动腿
            # TODO: 目前算法如果有任何一个合约成交了，则其他合约直接设置为主动单，开始主动成交。日后优化
            active_symbols = mismatch_symbols
            # 重置主动单等待时间
            # self.active_order_waiting_since_dt = None
        else:
            # 初始建仓，或关仓阶段
            # 不存在单腿情况，进行成交评估。
            if len(self.active_orderids) > 0:
                for orderid in self.get_all_active_orderids():
                    order = self.get_order(orderid)
                    if order is None:
                        continue

                    passive_symbols.append(order.vt_symbol)

            if len(passive_symbols) == 0:
                # 选择评估时间长的作为被动腿（优先下单），主动腿等被动腿成交后在发交易申请
                # TODO: 将评估时间最长的合约作为被动单。
                if self._is_realtime_mode:
                    # 实盘环境下根据过去 tick_arr_len 根tick数据来判断交易难度
                    estimate_seconds_arr = self._estimate_deal_seconds_all()
                else:
                    # 回测环境下，根据最近一个bar判断成交难度（仅用于回测）
                    estimate_seconds_arr = self._estimate_deal_seconds_all_backtest_only()

                # 首先，无法确定成交时间的合约作为被动单
                passive_symbols = [
                    vt_symbol for vt_symbol, seconds in zip(self.vt_symbols, estimate_seconds_arr) if seconds == -1]
                if len(passive_symbols) == 0:
                    passive_symbols = [
                        self.vt_symbols[_] for _ in np.where(estimate_seconds_arr == np.max(estimate_seconds_arr))[0]]

        return active_symbols, passive_symbols

    def _algo_trading_2_target_pos(self):
        """执行算计交易，保证目标仓位与实际仓位一致"""
        active_symbols, passive_symbols = self._generate_active_passive_symbols()
        try:
            # 执行被动单
            self._handle_passive_order(passive_symbols)
            # 执行主动单
            self._handle_active_order(active_symbols)
        except:
            logging.exception(f"算法交易错误, passive_symbols={passive_symbols}, active_symbols={active_symbols}")

    def on_start(self) -> None:
        super().on_start()
        if self._is_realtime_mode:
            self.algo_trading_running = True
            self.algo_trading_thread = threading.Thread(target=self._algo_trading_2_target_pos_thread, daemon=True)
            self.algo_trading_thread.start()

    def on_stop(self):
        super().on_stop()
        if self._is_realtime_mode:
            self.algo_trading_running = False
            self.algo_trading_thread.join()

    def cancel_order_by_vt_symbol(self, vt_symbol) -> bool:
        """
        根据 vt_symbol 取消订单
        return: True 存在订单被取消的动作；False，没有订单被取消的动作发生（说明已经没有相关的订单）
        """
        canceled = False
        for vt_orderid in self.active_orderids.copy():
            if vt_orderid not in self.orders:
                continue
            order = self.orders[vt_orderid]
            # self.write_log(
            #     f"vt_orderid={vt_orderid} "
            #     f"mismatched={mismatched_vt_symbol} order.vt_symbol {order.vt_symbol} "
            #     f"match={order.vt_symbol == mismatched_vt_symbol}")
            if order.vt_symbol == vt_symbol:
                self.write_log(f'撤单{vt_orderid}[{vt_symbol}]')
                self.cancel_order(vt_orderid)
                canceled = True

        return canceled

    def has_no_activate_order(self, vt_symbol):
        """检查与当前 vt_symbol 相关的订单是否都已经被取消"""
        for vt_orderid in self.active_orderids.copy():
            if vt_orderid not in self.orders:
                continue
            order = self.orders[vt_orderid]
            if order.vt_symbol == vt_symbol:
                return False

        return True

    def set_targets_pos(self, targets: Dict[str, Tuple[int, Optional[float]]]):
        """设置目标仓位，目标价格（价格为None，则默认以最近的close下单）"""
        self.targets = targets
        self.target_refreshed = True

    def on_tick(self, tick: TickData) -> bool:
        """
        Callback of new tick data update.
        """
        is_available = super().on_tick(tick)
        if not is_available:
            return is_available
        # 更新 tick_arr
        tick_arr = self.tick_arr[tick.vt_symbol]
        tick_arr[:-1, :] = tick_arr[1:, :]
        tick_arr[-1, :] = [np.round(tick.last_price, 2), tick.volume]
        return is_available

    def _handle_order_to_target_pos_backtest_only(self, bars: Dict[str, BarData]) -> None:
        if not self._is_realtime_mode:
            # 实盘环境下通过tick进行交易触发
            # 回测环境下bar直接下单
            if self.handle_order_one_by_one:
                self._handle_order_to_target_pos_one_by_one_backtest_only()
            else:
                self._handle_order_to_target_pos_same_time_backtest_only(bars)

    def on_bars(self, bars: Dict[str, BarData]) -> None:
        super().on_bars(bars)
        self._handle_order_to_target_pos_backtest_only(bars)

    def on_win_bars_finished(self, bars: Dict[str, BarData]) -> None:
        """对 on_win_bars 逻辑进行收尾处理"""
        super().on_win_bars_finished(bars)
        self._handle_order_to_target_pos_backtest_only(bars)

        self.put_event()

    def _handle_order_to_target_pos_same_time_backtest_only(self, bars: Dict[str, BarData]):
        """【仅用于回测】on_bar 触发套利下单交易"""
        # clear existed orders
        self.cancel_all()
        # Execute orders
        for vt_symbol in self.vt_symbols:
            try:
                target_pos, target_price = self.targets[vt_symbol]
            except KeyError:
                continue

            current_pos = self.get_pos(vt_symbol)
            pos_diff = target_pos - current_pos
            volume = abs(pos_diff)
            if volume == 0:
                continue
            if vt_symbol not in bars:
                self.write_log(f"{vt_symbol} {current_pos} -> {target_pos} but vt_symbol not in bar", 'error')
                continue
            bar = bars[vt_symbol]
            if bar is None:
                self.write_log(f"{vt_symbol} {current_pos} -> {target_pos} but current bar is None", 'error')
                continue
            # datetime_str = datetime_2_str(bar.datetime)
            if pos_diff > 0:
                # self.write_log(
                #     f"{datetime_str} {vt_symbol} {current_pos} -> {target_pos} = {pos_diff} ↑ price={price}")

                if current_pos < 0:
                    self.cover(vt_symbol, target_price, abs(current_pos))
                    self.buy(vt_symbol, target_price, abs(target_pos))
                else:
                    self.buy(vt_symbol, target_price, volume)
            elif pos_diff < 0:
                # self.write_log(
                #     f"{datetime_str} {vt_symbol} {current_pos} -> {target_pos} = {pos_diff} ↓ price={price}")

                if current_pos > 0:
                    self.sell(vt_symbol, target_price, abs(current_pos))
                    self.short(vt_symbol, target_price, abs(target_pos))
                else:
                    self.short(vt_symbol, target_price, volume)
            else:
                # self.write_log(
                #     f"{datetime_str} {vt_symbol} {current_pos} no change")
                pass

        self.target_refreshed = False

    def _estimate_deal_seconds(self, vt_symbol):
        """评估指定价位成交所需花费的时间，按秒为单位计算
        -1 代表无法确定
        0 代表即时成交
        正数，代表预估相应秒左右成交
        """
        estimate_result = -1
        last_tick = self.bgs[vt_symbol].last_tick
        if last_tick is None or vt_symbol not in self.targets:
            return estimate_result
        target_pos, target_price = self.targets[vt_symbol]
        target_price = np.round(target_price, 2)
        current_pos = self.get_pos(vt_symbol)
        tick_arr = self.tick_arr[vt_symbol]
        pos_diff = target_pos - current_pos
        if pos_diff > 0:
            # 做多或平空
            if last_tick.ask_price_1 <= target_price:
                # 目标价格在 卖一价 以上，即时成交
                estimate_result = 0
            elif target_price < last_tick.bid_price_1:
                # 目标价格在 买一价 以下，无法确定成交时间
                pass
            else:
                indexes = np.where(tick_arr[:, 0] == target_price)
                if len(indexes) > 0 and len(indexes[0]) > 0:
                    # 从第一个目标价格位置开始计算，所有目标价格的成交量平均到每秒的平均成交量
                    idx_first = indexes[0][0]
                    tick_passed = tick_arr.shape[0] - idx_first
                    avg_vol = tick_arr[tick_arr[:, 0] == target_price, 1].sum() / tick_passed * 2
                else:
                    # 没有对应目标价格的为成交量数据，以总体成交量为样本进行计算平均每秒成交量
                    # mean() 为每个tick的成交量，*2 为每秒成交量，
                    # 但是预期未来不是所有成交量都会这个价格上成交，因此再 / 2，因此，相当于 *2/2 没有操作
                    avg_vol = tick_arr[:, 1].mean()  # * 2 / 2

                estimate_result = last_tick.volume / avg_vol

        elif pos_diff < 0:
            # 做空或平多
            if target_price <= last_tick.bid_price_1:
                # 目标价格在 买一价 以下，即时成交
                estimate_result = 0
            elif last_tick.ask_price_1 < target_price:
                # 目标价格在 买一价 以下，无法确定成交时间
                pass
            else:
                indexes = np.where(tick_arr[:, 0] == target_price)
                if len(indexes) > 0 and len(indexes[0]) > 0:
                    # 从第一个目标价格位置开始计算，所有目标价格的成交量平均到每秒的平均成交量
                    idx_first = indexes[0][0]
                    tick_passed = tick_arr.shape[0] - idx_first
                    avg_vol = tick_arr[tick_arr[:, 0] == target_price, 1].sum() / tick_passed * 2
                else:
                    # 没有对应目标价格的为成交量数据，以总体成交量为样本进行计算平均每秒成交量
                    # mean() 为每个tick的成交量，*2 为每秒成交量，
                    # 但是预期未来不是所有成交量都会这个价格上成交，因此再 / 2，因此，相当于 *2/2 没有操作
                    avg_vol = tick_arr[:, 1].mean()  # * 2 / 2

                estimate_result = last_tick.volume / avg_vol
        else:
            pass

        return estimate_result

    def _handle_pos_2_target(self, vt_symbol, add_price=None, market_price=False, activate=True):
        """将制定合约持仓数调整到目标仓位"""
        try:
            target_pos, target_price = self.targets[vt_symbol]
        except KeyError:
            return
        current_pos = self.get_pos(vt_symbol)

        if market_price:
            # 根据市场价格修正报单价格
            tick = self.bgs[vt_symbol].last_tick
            if target_pos - current_pos > 0:
                # 方向做多
                # activate==True 市价对手方主动成交，否则本方挂单成交
                target_price = tick.ask_price_1 if activate else tick.bid_price_1
            else:
                # 方向做空
                # activate==True 市价对手方主动成交，否则本方挂单成交
                target_price = tick.bid_price_1 if activate else tick.ask_price_1

            self.write_log(
                f"{self.get_vt_symbol_target_pos_str(vt_symbol)} 盘口{'对价' if activate else '挂单'} {target_price:.1f}",
                'debug')

        elif target_price <= 0:
            return

        elif add_price is not None:
            if target_pos - current_pos > 0:
                # 方向做空
                target_price += add_price
            else:
                target_price -= add_price

            self.write_log(f"{self.get_vt_symbol_target_pos_str(vt_symbol)} 对手方向加价挂单 {target_price:.1f}", 'debug')

        else:
            self.write_log(f"{self.get_vt_symbol_target_pos_str(vt_symbol)} 限价挂单 {target_price:.1f}", 'debug')

        # 根据目标持仓以及当前持仓，规划下单方式
        if 0 <= target_pos < current_pos:
            # 平多单(减仓)
            volume = abs(target_pos - current_pos)
            self.sell(vt_symbol, target_price, volume)
        elif target_pos < 0 < current_pos:
            # 多翻空
            self.sell(vt_symbol, target_price, current_pos)
            # 先平仓，之后再开仓
            # self.short(vt_symbol, target_price, abs(target_pos))
        elif target_pos < current_pos <= 0:
            # 追加空单
            volume = abs(target_pos - current_pos)
            self.short(vt_symbol, target_price, volume)
        elif current_pos < target_pos <= 0:
            # 平空单(减仓)
            volume = abs(target_pos - current_pos)
            self.cover(vt_symbol, target_price, volume)
        elif current_pos < 0 < target_pos:
            # 空翻多
            self.cover(vt_symbol, target_price, abs(current_pos))
            # 先平仓，之后再开仓
            # self.buy(vt_symbol, target_price, target_pos)
        elif 0 <= current_pos < target_pos:
            # 追加多单
            volume = abs(target_pos - current_pos)
            self.buy(vt_symbol, target_price, volume)

    def _handle_active_order_by_bar_backtest_only(self, vt_symbol, add_price=1):
        """执行主动单（仅依赖于 bar 数据），仅用于回测使用"""
        if len(self.active_orderids) == 0:
            # 首次开仓
            self.write_log(f"建立配对交易 {self.get_vt_symbol_target_pos_str(vt_symbol)} 优先配对。", 'debug')
            self._handle_pos_2_target(vt_symbol, add_price=add_price)
            self.target_refreshed = False

        else:
            # 有开仓，等待成交
            if self.target_refreshed:
                # 如果超时，则重新下单
                # 检查新下单的价格是否与就单子相同，如果相同则不用 撤销重下单，继续等待即可
                # 注意：这里 list(self.active_orderids) 其中 list() 不能去掉，
                #       因为内部会 cancel_order(order.orderid) 造成 active_orderids 变化会抛异常
                for active_orderid in list(self.active_orderids):
                    order = self.get_order(active_orderid)
                    if order is None:
                        continue
                    target_pos, target_price = self.targets[order.vt_symbol]
                    if order.price != target_price:
                        # 不要在订单取消后面直接下单，
                        # 因为 cancel_order 可能会失败，引发导致重复下单的情况。
                        # 订单取消成功后,通过 if len(self.active_orderids) == 0 状态进行重新下单
                        # 重新下单后 self.target_refreshed = False
                        # 发现 cancel_order(order.orderid) 总是找不到订单导致撤单失败
                        # self.cancel_order(order.orderid)
                        self.cancel_all()

    def _handle_order_to_target_pos_one_by_one_backtest_only(self):
        """【仅用于回测】on_bar 触发套利下单交易"""
        # clear existed orders
        # self.cancel_all()
        active_symbols, passive_symbols = self._generate_active_passive_symbols()
        # 执行被动单
        self._handle_passive_order(passive_symbols)
        # 执行主动单
        self._handle_active_order_by_bar_backtest_only(active_symbols)


class TargetPosAndPrice2SymbolTemplate(TargetPosAndPriceTemplate):

    def __init__(
            self,
            strategy_engine: StrategyEngine,
            strategy_name: str,
            vt_symbols: List[str],
            setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        self.vt_symbol1 = vt_symbols[0]
        self.vt_symbol2 = vt_symbols[1]


class SpreadTypeEnum(Enum):
    ratio = 'ratio'
    diff = 'diff'


class TargetPosAndPriceSpreadTemplate(TargetPosAndPrice2SymbolTemplate):
    # 当前价差
    curr_win_spread = 0
    # spread array size
    spread_array_size = 100
    spread_type = SpreadTypeEnum.diff

    def __init__(
            self,
            strategy_engine: StrategyEngine,
            strategy_name: str,
            vt_symbols: List[str],
            setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        self.variables.append('curr_spread')
        if 'curr_win_spread' not in self.variables and not (self.interval == Interval.MINUTE and self.window == 1):
            self.variables.append('curr_win_spread')
        # 价差数组
        self.spreads = np.zeros(self.spread_array_size)
        self.curr_spread = 0
        self.win_spreads = np.zeros(self.spread_array_size)
        self.win_am_spread = ArrayManager(self.spread_array_size)
        self._bg_spread = BarGenerator(
            on_bar=lambda x: None,
            window=self.window, on_window_bar=lambda bar: self.win_am_spread.update_bar(bar),
            interval=self.interval,
        )
        self.spread_symbol_name = f"{self.vt_symbol1}_{self.vt_symbol2}"
        if isinstance(self.spread_type, str):
            self.spread_type = SpreadTypeEnum[self.spread_type]
        elif not isinstance(self.spread_type, SpreadTypeEnum):
            raise ValueError(f"spread_type={self.spread_type} 无效")

    def on_init(self) -> None:
        super().on_init()
        self.win_spreads = np.zeros(self.spread_array_size)

    def _update_spread(self, spread):
        self.spreads[:-1] = self.spreads[1:]
        self.spreads[-1] = self.curr_spread = spread

    def _update_win_spread(self, spread):
        self.win_spreads[:-1] = self.win_spreads[1:]
        self.win_spreads[-1] = self.curr_win_spread = spread

    def on_bars(self, bars: Dict[str, BarData]) -> Optional[bool]:
        ret = super().on_bars(bars)
        bar1 = bars[self.vt_symbol1]
        spread = self.calc_spread_bar(bars)
        self._update_spread(spread)
        bar_spread = BarData(
            bar1.gateway_name, symbol=self.spread_symbol_name, exchange=bar1.exchange,
            datetime=bar1.datetime, interval=Interval.MINUTE,
            open_price=spread, high_price=spread, low_price=spread, close_price=spread
        )
        self._bg_spread.update_bar(bar_spread)
        return ret

    def calc_spread_bar(self, bars: Dict[str, BarData]) -> float:
        bar1 = bars[self.vt_symbol1]
        bar2 = bars[self.vt_symbol2]
        if bar1 is None or bar2 is None:
            self.write_log(f"calc_spread_bar bars={bars}", 'warning')
            spread = 0
        elif self.spread_type == SpreadTypeEnum.diff:
            spread = np.round(bar1.close_price - bar2.close_price, 2)
        elif self.spread_type == SpreadTypeEnum.ratio:
            spread = np.round(bar1.close_price / bar2.close_price, 4)
        else:
            raise ValueError(f"spread_type={self.spread_type} 无效")

        return spread

    def on_win_bars(self, bars: Dict[str, BarData]) -> Optional[bool]:
        ret = super().on_win_bars(bars)
        spread = self.calc_spread_bar(bars)
        self._update_win_spread(spread)
        return ret


class TargetPosAndPriceFutures2OptionTemplate(TargetPosAndPriceTemplate):
    """"期货CTA策略，多头与空头仓单通过期货put,call建立相应头寸"""

    def __init__(
            self,
            strategy_engine: StrategyEngine,
            strategy_name: str,
            vt_symbols: List[str],
            setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        for num, vt_symbol in enumerate(self.vt_symbols):
            # PATTERN_SYMBOL_CALL_PUT_SPLIT.split('ru2110C12250.DCE') -> ['', 'ru2110', 'C', '12250', '.DCE']
            # PATTERN_SYMBOL_CALL_PUT_SPLIT.split('ru2110.DCE') -> ['ru2110.DCE']
            splits = PATTERN_SYMBOL_CALL_PUT_SPLIT.split(vt_symbol)  # For commodity/finance options
            if len(splits) == 1:
                self.vt_symbol_future = vt_symbol
            elif splits[2].upper() == 'C':
                self.vt_symbol_call = vt_symbol
            elif splits[2].upper() == 'P':
                self.vt_symbol_put = vt_symbol
            else:
                raise ValueError(f"{vt_symbol} 不是有效的合约")

    def set_futures_target_pos(self, pos):
        """期货多头 -> 买 call 平 put； 期货空头 -> 买 put 平 call"""
        if pos >= 0:
            tick = self.latest_tick_dic.get(self.vt_symbol_call)
            if tick:
                price_call = tick.ask_price_1
            else:
                bar = self.current_bars.get(self.vt_symbol_call)
                if bar:
                    price_call = bar.close_price
                else:
                    price_call = 0

            tick = self.latest_tick_dic.get(self.vt_symbol_put)
            if tick:
                price_put = tick.bid_price_1
            else:
                bar = self.current_bars.get(self.vt_symbol_put)
                if bar:
                    price_put = bar.close_price
                else:
                    price_put = 0

            self.set_targets_pos({
                self.vt_symbol_call: (pos, price_call),
                self.vt_symbol_put: (0, price_put),
            })
        else:
            tick = self.latest_tick_dic.get(self.vt_symbol_call)
            if tick:
                price_call = tick.bid_price_1
            else:
                bar = self.current_bars.get(self.vt_symbol_call)
                if bar:
                    price_call = bar.close_price
                else:
                    price_call = 0

            tick = self.latest_tick_dic.get(self.vt_symbol_put)
            if tick:
                price_put = tick.ask_price_1
            else:
                bar = self.current_bars.get(self.vt_symbol_put)
                if bar:
                    price_put = bar.close_price
                else:
                    price_put = 0

            self.set_targets_pos({
                self.vt_symbol_call: (0, price_call),
                self.vt_symbol_put: (pos, price_put),
            })


if __name__ == "__main__":
    pass
