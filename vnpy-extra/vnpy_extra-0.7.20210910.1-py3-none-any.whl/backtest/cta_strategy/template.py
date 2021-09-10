"""
@author  : MG
@Time    : 2020/11/16 10:20
@File    : template.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import math
import re
import threading
import time
import warnings
from collections import defaultdict, namedtuple
from datetime import datetime, date, timedelta
from enum import Enum
from itertools import chain
from typing import Optional, Dict, List, Tuple, Type

import numpy as np
import pandas as pd
from ibats_utils.json import obj_2_json
from ibats_utils.os import create_instance
from ibats_utils.transfer import datetime_2_str
from vnpy.app.cta_strategy import CtaTemplate as CtaTemplateBase, TargetPosTemplate as TargetPosTemplateBase
from vnpy.trader.constant import Offset, Direction, Interval
from vnpy.trader.object import OrderData, BarData, TickData, TradeData, Status

from vnpy_extra.backtest import check_datetime_available, StopOpeningPos, check_datetime_trade_available, \
    generate_mock_load_bar_data
from vnpy_extra.config import logging
from vnpy_extra.constants import SYMBOL_MINUTES_COUNT_DIC, GeneralPeriodEnum, BASE_POSITION, \
    STOP_OPENING_POS_PARAM, ENABLE_COLLECT_DATA_PARAM
from vnpy_extra.db.orm import AccountStrategyStatusEnum
from vnpy_extra.report.collector import trade_data_collector, order_data_collector, latest_price_collector
from vnpy_extra.report.monitor import AccountStrategyStatusMonitor
from vnpy_extra.utils.enhancement import BarGenerator, PriceTypeEnum, CtaSignal, CtaExitSignal
from vnpy_extra.utils.exception import MissMatchParametersError
from vnpy_extra.utils.symbol import get_instrument_type, get_vt_symbol_multiplier, get_vt_symbol_rate, get_price_tick

TradeWinLossStatsTuple = namedtuple(
    'TradeWinLossStatsTuple',
    ['start', 'end', 'entry_price', 'avg_entry_price', 'exit_price', 'volume', 'is_win',
     'pl', 'gross_pl', 'rr', 'gross_rr']
)


class AllowTradeDirectionEnum(Enum):
    LONG_ONLY = 'long_only'
    Short_ONLY = 'short_only'
    ALL = 'all'


class CtaTemplate(CtaTemplateBase):
    # 该标识位默认为0（关闭状态）。为1时开启，程序一旦平仓后则停止后续交易。该标识位用于在切换合约时使用
    stop_opening_pos = StopOpeningPos.open_available.value
    # 考虑到六、周日、节假日等非交易日因素，保险起见，建议初始化日期 * 2 + 7
    init_load_days = 0
    # 加载主连连续合约作为合约历史行情数据（默认为False)
    load_main_continuous_md = False
    # 跟踪止损 （0为不启用）
    trailing_stop_rate: float = 0.0
    # 跟踪止损价格类型
    trailing_stop_price_type: str = PriceTypeEnum.auto.value
    # 成本线止损 （0为不启用）
    stop_loss_rate: float = 0.0
    # 如果 setting 里面有不在 parameters 里面的字段，则报错。这个开关主要是为了防止出现参数定义错误导致的无效回测
    raise_error_if_setting_not_in_parameters = True
    # 初始化加载数据日期跨度（天）。0代表关闭此功能。
    # 此功能主要是为了节省缓存空间，多个策略可以产生同一个初始化天数，从而减少数据库加载量，以及内存中的数据缓存空间。
    load_days_span = 30
    # 建仓基数，建立空头或多头仓位的数量
    base_position = 1
    # 当前持仓首次建仓时的 bar_count
    curr_open_bar_count = 0

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        self._logger_name = f'strategies.cta.{self.__class__.__name__}' \
            if self.__class__.__name__ == strategy_name \
            else f'strategies.cta.{self.__class__.__name__}.{strategy_name}'
        self.logger = logging.getLogger(self._logger_name)
        for _ in (STOP_OPENING_POS_PARAM, BASE_POSITION):
            if _ not in self.parameters:
                self.parameters.append(_)  # 增加 stop_opening_pos 用于合约切换是关闭当前线程

        if self.raise_error_if_setting_not_in_parameters:
            mismatches = []
            for _ in setting.keys():
                if _ in {'class_name', }:
                    continue
                if _ not in self.parameters:
                    self.logger.error(f"setting中 {_} 字段未在 parameters 中定义，请检查 setting 字段是否设置正确")
                    mismatches.append(_)

            if mismatches:
                raise MissMatchParametersError(
                    f"{mismatches} don't existed in parameters=\n{self.parameters}\nsetting=\n{setting}")

        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        # setting 不包含 stop_opening_pos key
        self.setting = {k: v for k, v in setting.items() if k in self.parameters}
        # 写日志
        self.logger.info(f"{strategy_name} on {vt_symbol} setting=\n{obj_2_json(setting, indent=4)}")
        # 基于假设：相同 direction, offset 的操作不会短期内连续发生，
        # 因此，对每一类交易单独记录订单的发送时间，避免出现时间记录混淆的问题
        self.send_and_on_order_dt_dic: Dict[
            Tuple[Direction, Offset],
            List[Optional[datetime], Optional[datetime], Optional[Status]]] = defaultdict(lambda: [None, None, None])
        # 记录所有订单数据
        self.on_order_received_dic: Dict[str, OrderData] = {}
        self.send_order_id_info_dic: Dict[str, Tuple[Direction, Offset]] = {}
        self.send_order_dic_lock = threading.Lock()
        # 仅用于 on_order 函数记录上一个 order 使用，解决vnpy框架重复发送order的问题
        self._last_order: Optional[OrderData] = None
        self._trades = []  # 记录所有成交数据
        self.current_bar: Optional[BarData] = None
        self.bar_count = 0
        self.bg = BarGenerator(self.on_bar)
        # 是否实盘环境
        self._is_realtime_mode = self.strategy_name is not None and self.strategy_name != self.__class__.__name__
        self._strategy_status = AccountStrategyStatusEnum.Created
        # 最近一个tick的时间
        self.last_tick_time: Optional[datetime] = None
        self.time_diff_seconds_local_2_server: int = 0
        # 最近一次接受到订单回报的时间，被 send_and_on_order_dt_dic 替代
        # self.last_order_dt: Optional[datetime] = None
        # 最近一次发送订单的时间，被 send_and_on_order_dt_dic 替代
        # self.last_send_order_dt: Optional[datetime] = None
        # 是否收集申请单以及交易单记录
        self.enable_collect_data = setting.get(ENABLE_COLLECT_DATA_PARAM, False)
        self._strategy_status_monitor: Optional[AccountStrategyStatusMonitor] = None
        self._lock: Optional[threading.Lock] = None
        # 最近一条提示信息
        self._last_msg = ''
        # 最近一个 tick
        self.last_tick: Optional[TickData] = None
        self.latest_reject_response_order: Optional[OrderData] = None
        self.latest_cancel_response_order: Optional[OrderData] = None
        # 策略启动时查询数据库加载 entry_price 最近一次建仓时的价格。（已废弃）目前通过 self.variables 实现
        # self.enable_entry_exit_price = False
        # 最近一次建仓时间
        self.entry_datetime = None
        # 最近一次建仓价格
        self.entry_price = 0
        # 最近一次离场价格
        self.exit_price = 0
        # 平均建仓价格
        self.avg_entry_price = 0
        # Drawback rate
        self.drawback_rate = 0
        # Acc Drawback rate: 不包含当前交易的亏损或盈利
        self.acc_drawback_rate = 0
        # highest after entry
        self.highest_after_entry = None
        # lowest after entry
        self.lowest_after_entry = None
        # add variables
        for variable in [
            "entry_price", "exit_price", "avg_entry_price",
            "highest_after_entry", "lowest_after_entry",
            "acc_drawback_rate", "drawback_rate", "curr_open_bar_count",
        ]:
            if variable not in self.variables:
                self.variables.append(variable)

        if self.trailing_stop_rate != 0 and "trailing_stop_hl_price" not in self.variables:
            self.variables.append("trailing_stop_hl_price")

        # —————————————————— 合约基本信息 ————————————————
        self.vt_symbol_multiplier = get_vt_symbol_multiplier(self.vt_symbol)
        self.vt_symbol_rate = get_vt_symbol_rate(self.vt_symbol)
        self.vt_symbol_price_tick = get_price_tick(self.vt_symbol)
        self._gross_rr_minus_fee = self.vt_symbol_rate * self.vt_symbol_multiplier
        # —————————————————— 止损功能相关变量 ————————————————
        # 跟踪止损价格类型
        self.trailing_stop_price_type_enum = PriceTypeEnum(self.trailing_stop_price_type)
        # 建仓点算起的最高或最低价
        self.trailing_stop_hl_price = 0
        # 跟踪止损价格
        self.trailing_stop_price = 0
        # 成本线止损价格
        self.stop_loss_price = 0
        # 当前止损价
        self.stop_price_curr = 0
        # 止损单订单
        self.stop_vt_orderids = None
        # 启用使用 STOP 单进行止损（该参数将禁止开启 Stop 单）
        # 该参数仅用于子类以其他方式实现止损，为了避免重复发单，因此关闭 stop 止损单。
        # 该开关仅对实盘模式有效，回测模式依然使用 stop 单方式进行止损。
        self.enable_stop_order = True
        # —————————————————— 盘中盈亏统计变量 ————————————————
        self.daily_trade_stats_list: Dict[date, List[TradeWinLossStatsTuple]] = defaultdict(list)
        self.keep_win_loss_counter = 0

    def set_is_realtime_mode(self, is_realtime_mode):
        self._is_realtime_mode = is_realtime_mode

    def get_id_name(self):
        """获取 id_name"""
        param_str = '_'.join([
            make_param_2_str(self.setting[key]) for key in self.parameters
            if (
                    key in self.setting
                    and key not in (STOP_OPENING_POS_PARAM, BASE_POSITION, ENABLE_COLLECT_DATA_PARAM)
                    and not (key == 'allow_trade_direction' and self.setting[key] == AllowTradeDirectionEnum.ALL.value)
            )
        ])
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
                self.write_log(f"策略 [{self.vt_symbol}] 状态 "
                               f"{self._strategy_status.name} -> {status.name} 被远程启动")
                self._strategy_status = status
            finally:
                if self._lock is not None:
                    self._lock.release()

            self.on_start()

        elif status == AccountStrategyStatusEnum.StopPending \
                and self._strategy_status == AccountStrategyStatusEnum.Running:
            # AccountStrategyStatusEnum.StopPending 状态只从数据库端发起
            if self._lock is not None:
                self._lock.acquire()

            try:
                # 保险起见，为防止出现死循环调用，在 on_stop 先把状态调整过来
                self.write_log(f"策略 [{self.vt_symbol}] 状态 "
                               f"{self._strategy_status.name} -> {status.name} 被远程停止")
                self._strategy_status = status
            finally:
                if self._lock is not None:
                    self._lock.release()

            self.on_stop()
        else:
            self.write_log(f"策略 [{self.vt_symbol}] 状态 "
                           f"{self._strategy_status.name} -> {status.name}")
            self._strategy_status = status

    def _get_strategy_status(self) -> AccountStrategyStatusEnum:
        return self._strategy_status

    def on_init(self) -> None:
        super().on_init()
        self.bar_count = 0
        self._set_strategy_status(AccountStrategyStatusEnum.Initialized)
        if self._is_realtime_mode and self._strategy_status_monitor is None:
            # 该语句一定不能放在 __init__ 中
            # 因为 strategy_name 在回测阶段模块中，在 __init__ 后可能会被重写赋值
            self._strategy_status_monitor = AccountStrategyStatusMonitor(
                self.strategy_name,
                self._get_strategy_status,
                self._set_strategy_status,
                self.vt_symbol,
                self.setting,
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

            # 初始化历史行情数据
            if self._is_realtime_mode and self.load_main_continuous_md:
                with generate_mock_load_bar_data(self.write_log):
                    self.load_bar(self.init_load_days)
            else:
                self.load_bar(self.init_load_days)

        # if self.enable_entry_exit_price and self._is_realtime_mode:
        #     # 回测情况下不需要获取历史成交价格
        #     # 加载历史交易数据
        #     trade_data_open, trade_data_close = TradeDataModel.get_latest_trade_data_by_stg(
        #         self.strategy_name, self.vt_symbol)
        #
        #     if trade_data_open is not None:
        #         # 记录开仓价格
        #         self.entry_price = trade_data_open.price
        #     if trade_data_close is not None:
        #         # 记录平仓价格
        #         self.exit_price = trade_data_close.price

        self.write_log(f"策略初始化完成. 加载{self.vt_symbol} {self.init_load_days}天数据")

    def on_start(self) -> None:
        super().on_start()
        self._set_strategy_status(AccountStrategyStatusEnum.Running)
        # 整理持仓信息
        self.write_log(f"策略启动，当前初始持仓： {self.vt_symbol} {self.pos}")
        self.put_event()
        # 初始化相关数据,可以在重启策略时清空历史订单对当前策略的影响.
        self.send_and_on_order_dt_dic: Dict[
            Tuple[Direction, Offset],
            List[Optional[datetime], Optional[datetime], Optional[Status]]] = defaultdict(lambda: [None, None, None])
        # 记录所有订单数据
        self.on_order_received_dic: Dict[str, OrderData] = {}
        # 仅用于 on_order 函数记录上一个 order 使用，解决vnpy框架重复发送order的问题
        self._last_order: Optional[OrderData] = None
        self._trades = []  # 记录所有成交数据

        # if self._is_realtime_mode:
        #     start_strategy_position_monitor()

    def on_tick(self, tick: TickData) -> bool:
        """判断当前tick数据是否有效,如果无效数据直接返回 False,否则更新相应bar数据"""
        super().on_tick(tick)
        self.last_tick = tick
        is_available = check_datetime_available(tick.datetime)
        if not is_available:
            return is_available
        # 如果有仓位则更新追踪止损价格
        if self.pos != 0:
            self.update_trailing_stop_price(tick.ask_price_1 if self.pos > 0 else tick.bid_price_1)

        # 激活分钟线 on_bar
        self.bg.update_tick(tick)
        latest_price_collector.put_nowait(tick)
        last_tick_time = tick.datetime.replace(tzinfo=None)
        if self.last_tick_time is None:
            # 仅首次运行的时候计算本地与服务器时间差
            # 不可以使用 .seconds 在负时间的情况下 second 将会是一天的时间差
            self.time_diff_seconds_local_2_server = (datetime.now() - last_tick_time).total_seconds()

        self.last_tick_time = tick.datetime.replace(tzinfo=None) + timedelta(
            seconds=self.time_diff_seconds_local_2_server)

        return is_available

    def on_bar(self, bar: BarData):
        super().on_bar(bar)
        self.current_bar: BarData = bar
        self.bar_count += 1
        # 计算盘中相关变量，包括 lowest_after_entry, highest_after_entry, acc_drawback_rate, drawback_rate 等
        self.calc_holding_relative_properties()
        # 更新跟踪止损价格
        self.update_trailing_stop_price()
        # 检查是否触发止损，并发送止损单
        self.check_and_do_stop()

    def cancel_order(self, vt_orderid):
        if vt_orderid in self.on_order_received_dic:
            order = self.on_order_received_dic[vt_orderid]
            key = (order.direction,
                   Offset.CLOSE if order.offset in (Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY)
                   else order.offset)
            self.write_log(f"取消订单 {vt_orderid} {order.offset.value} {order.direction.value}", 'debug')
            with self.send_order_dic_lock:
                self.send_and_on_order_dt_dic[key][0] = datetime.now()
        elif vt_orderid.startswith('STOP.'):
            # 取消停止单
            self.write_log(f"取消停止单 {vt_orderid}", 'debug')
        elif vt_orderid in self.send_order_id_info_dic:
            direction, offset = self.send_order_id_info_dic[vt_orderid]
            self.write_log(f"取消订单 {vt_orderid} {offset.value} {direction.value}", 'debug')
        else:
            self.write_log(
                f"订单{vt_orderid} 不在 send_order_dic 列表中。send_order_dic.keys={self.on_order_received_dic.keys()}",
                'warning')

        super().cancel_order(vt_orderid)

    def send_order(
            self,
            direction: Direction,
            offset: Offset,
            price: float,
            volume: float,
            stop: bool = False,
            lock: bool = False
    ):
        if not stop:
            vt_symbol = self.vt_symbol
            current_pos = int(self.pos)
            order_datetime = self.last_tick_time if self.last_tick_time is not None else None
            ignore_order = False
            log_level = 'debug'
            msg = ''
            if price <= 0.0:
                log_level = 'warning'
                if self.current_bar is not None and self.current_bar.close_price > 0:
                    price = self.current_bar.close_price
                    msg = '【价格无效】，使用上一根K线收盘价'
                elif self.last_tick is not None:
                    # 使用被动价格
                    price = self.last_tick.bid_price_1 if direction == Direction.LONG else self.last_tick.ask_price_1
                    msg = f'【价格无效】，使用上一Tick{"买1价格" if direction == Direction.LONG else "卖1价格"}'
                else:
                    msg = f'【价格无效】'
                    log_level = 'error'
                    ignore_order = True

            if order_datetime is not None and not check_datetime_trade_available(
                    order_datetime) and self._is_realtime_mode:
                log_level = 'warning'
                msg += '【非交易时段】'
                ignore_order = True
            elif self.stop_opening_pos != StopOpeningPos.open_available.value and offset == Offset.OPEN:
                log_level = 'warning'
                msg += '【禁止开仓】'
                ignore_order = True
            elif self.latest_reject_response_order:
                dt = self.latest_reject_response_order.datetime.replace(tzinfo=None)
                if abs(datetime.now() - dt).seconds <= 300 and \
                        self.latest_reject_response_order.offset == offset and \
                        self.latest_reject_response_order.direction == direction and \
                        self.latest_reject_response_order.price == price and \
                        self.latest_reject_response_order.volume == volume:
                    log_level = 'warning'
                    msg += '【与上一个被拒单相同】5分钟内不再发送同样的订单'
                    ignore_order = True
                else:
                    self.latest_reject_response_order = None

            elif self.latest_cancel_response_order:
                dt = self.latest_cancel_response_order.datetime.replace(tzinfo=None)
                if abs(datetime.now() - dt).seconds <= 30 and \
                        self.latest_cancel_response_order.offset == offset and \
                        self.latest_cancel_response_order.direction == direction and \
                        self.latest_cancel_response_order.price == price and \
                        self.latest_cancel_response_order.volume == volume:
                    log_level = 'warning'
                    msg += '【与上一个被撤单相同】30秒内不再发送同样的订单'
                    ignore_order = True
                else:
                    self.latest_cancel_response_order = None

            if offset == Offset.OPEN:
                if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                    self.write_log(
                        f"{vt_symbol:>11s} {direction.value} {offset.value:4s} {price:.1f} "
                        f"{current_pos:+d} {volume:+.0f} {'停止单' if stop else ''} {msg}"
                        if order_datetime is None else
                        f"{datetime_2_str(order_datetime)} {vt_symbol:>11s} {direction.value} {offset.value:4s} {price:.1f} "
                        f"{current_pos:+d} {volume:+.0f} {'停止单' if stop else ''} {msg}",
                        log_level
                    )

                if self.stop_opening_pos != StopOpeningPos.open_available.value:
                    self.write_log(f"当前策略 stop_opening_pos="
                                   f"{self.stop_opening_pos}<{StopOpeningPos(self.stop_opening_pos).name}>，"
                                   f"所有开仓操作将被屏蔽（用于主力合约切换,或关闭失效策略使用）", log_level)
                    self.stop_opening_pos = StopOpeningPos.stop_opening_and_nolog.value

            else:
                self.write_log(
                    f"{vt_symbol:>11s} {direction.value} {offset.value:4s} {price:.1f} "
                    f"      {current_pos:+d} {-volume:+.0f} {'停止单' if stop else ''} {msg}"
                    if order_datetime is None else
                    f"{datetime_2_str(order_datetime)} {vt_symbol:>11s} {direction.value} {offset.value:4s} {price:.1f} "
                    f"      {current_pos:+d} {-volume:+.0f} {'停止单' if stop else ''} {msg}",
                    log_level
                )

            if ignore_order:
                return []

            key = (direction,
                   Offset.CLOSE if offset in (Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY)
                   else offset)
            with self.send_order_dic_lock:
                self.send_and_on_order_dt_dic[key][0] = datetime.now()

        vt_orderids = super().send_order(direction, offset, price, volume, stop, lock)
        if len(vt_orderids) >= 1:
            self.send_order_id_info_dic[vt_orderids[0]] = (direction, offset)

        return vt_orderids

    def on_order(self, order: OrderData):
        super().on_order(order)
        # 2021-02-02 不能使用服务器时间，与本地时间作比较。
        # if order.datetime is not None:
        #     # 本地时间与服务器时间存在时差，将会导致判断异常。
        #     last_order_dt = order.datetime.replace(tzinfo=None)
        #     if self.last_order_dt is None or self.last_order_dt < last_order_dt:
        #         self.last_order_dt = last_order_dt
        #         self.write_log(f"last_order_dt={last_order_dt}")
        #     self.last_order_dt = datetime.now()
        if not self._is_realtime_mode:
            return
        key = (order.direction,
               Offset.CLOSE if order.offset in (Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY)
               else order.offset)
        with self.send_order_dic_lock:
            if order.status in (Status.ALLTRADED,):
                # 已经完成的交易直接剔除
                try:
                    self.send_and_on_order_dt_dic.pop(key)
                except KeyError:
                    pass
            else:
                self.send_and_on_order_dt_dic[key][1] = datetime.now()
                self.send_and_on_order_dt_dic[key][2] = order.status

            if order.status in (Status.REJECTED, Status.CANCELLED):
                # 已经完成的交易直接剔除
                try:
                    self.on_order_received_dic.pop(order.vt_orderid)
                except KeyError:
                    pass
            else:
                self.on_order_received_dic[order.vt_orderid] = order

        self._last_order = order
        # self.write_log(f'on_order:   key={key}, send_dt, on_dt={self.send_and_on_order_dt_dic[key]}')
        current_pos = int(self.pos)
        order_datetime = order.datetime
        if order.status is None:
            order_status_str = ''
        else:
            order_status_str = order.status.value
            if order.status == Status.REJECTED:
                if order.datetime is None:
                    order.datetime = datetime.now()
                self.latest_reject_response_order = order
            elif order.status == Status.CANCELLED and order.traded == 0:
                self.latest_cancel_response_order = order

        order_volume = order.volume if order.direction == Direction.LONG else -order.volume
        traded_volume = -order.traded if order.direction == Direction.LONG else order.traded
        traded_volume_str = f'{traded_volume:+.0f}'
        if order.offset == Offset.OPEN:
            self.write_log(
                f"{'order.datetime=None' if order_datetime is None else datetime_2_str(order_datetime)} "
                f"{order.vt_symbol} {order.direction.value} {order.offset.value:4s} "
                f"{order.price:6.1f} {current_pos:+d} "
                f"{order_volume:+.0f}{'' if traded_volume == 0 else traded_volume_str}"
                f"{order_status_str}[{order.orderid}]"
            )
        else:
            self.write_log(
                f"{'order.datetime=None' if order_datetime is None else datetime_2_str(order_datetime)} "
                f"{order.vt_symbol} {order.direction.value} {order.offset.value:4s} "
                f"{order.price:6.1f}       {current_pos:+d} "
                f"{order_volume:+.0f}{'' if traded_volume == 0 else traded_volume_str}"
                f"{order_status_str}[{order.orderid}]"
            )

        if self.enable_collect_data and (self._last_order is None or self._last_order.orderid != order.orderid):
            order_data_collector.put_nowait(self.strategy_name, order)

        # 条件止损单全部成交、拒绝、取消，需要清除条件止损单号
        with self.send_order_dic_lock:
            if self.stop_vt_orderids is not None and \
                    order.status.value in (Status.ALLTRADED, Status.REJECTED) and \
                    order.vt_orderid == self.stop_vt_orderids:
                self.write_log("订单已成交，清空 stop_vt_orderids", 'debug')
                self.stop_vt_orderids = None

        # debug use only
        # with self.send_order_dic_lock:
        #     order_count = len(self.on_order_received_dic)
        #     for num, order in enumerate(self.on_order_received_dic.values(), start=1):
        #         if order.is_active():
        #             self.write_log(
        #                 f"{num}/{order_count}) on order: {order.orderid} {order.offset}
        #                 active={order.is_active()} dt={order.datetime}")

    def on_trade(self, trade: TradeData):
        super().on_trade(trade)
        self._trades.append(trade)
        if self.enable_collect_data:
            trade_data_collector.put_nowait(self.strategy_name, trade)

        # if self.enable_entry_exit_price:
        # 更新 entry_price, exit_price
        if trade.offset == Offset.OPEN:
            # 更新开仓价格
            self.entry_datetime = trade.datetime
            self.entry_price = trade.price
            if self.pos == 0:
                self.write_log(f"{trade.price} {trade.offset}{trade.direction} {trade.volume}手成交，当前持仓0", 'warning')
            else:
                abs_pos = abs(self.pos)
                trade_price = trade.price
                trade_volume = trade.volume
                self.avg_entry_price = ((abs_pos - trade_volume) * self.avg_entry_price
                                        + trade_volume * trade_price) / abs(self.pos)
                # 首次开仓
                if trade_volume == abs_pos:
                    self.highest_after_entry = self.lowest_after_entry = trade_price
                    self.curr_open_bar_count = self.bar_count

        else:
            self.exit_price = trade.price
            if self.pos == 0:
                # 平仓盈亏统计
                if trade.direction == Direction.LONG:
                    gross_rr = 1 - self.exit_price / self.avg_entry_price
                    gross_pl = (self.exit_price - self.avg_entry_price) * self.vt_symbol_multiplier
                else:
                    gross_rr = self.exit_price / self.avg_entry_price - 1
                    gross_pl = (self.avg_entry_price - self.exit_price) * self.vt_symbol_multiplier

                rr = gross_rr - self.vt_symbol_rate
                pl = gross_pl - (self.avg_entry_price + self.exit_price) * self._gross_rr_minus_fee
                # 平多 即代表此前持有为空仓；平空 即代表此前持有多仓
                is_win = rr > 0
                self.daily_trade_stats_list[trade.datetime.date()].append(TradeWinLossStatsTuple(
                    start=self.entry_datetime,
                    end=trade.datetime,
                    entry_price=self.entry_price,
                    avg_entry_price=self.avg_entry_price,
                    exit_price=self.exit_price,
                    volume=trade.volume,
                    is_win=is_win,
                    rr=rr,
                    gross_rr=gross_rr,
                    pl=pl,
                    gross_pl=gross_pl,
                ))
                # 连续盈亏统计
                if is_win:
                    if self.keep_win_loss_counter > 0:
                        self.keep_win_loss_counter += 1
                    else:
                        self.keep_win_loss_counter = 1
                else:
                    if self.keep_win_loss_counter < 0:
                        self.keep_win_loss_counter -= 1
                    else:
                        self.keep_win_loss_counter = -1

                # 重置 highest_after_entry lowest_after_entry
                self.highest_after_entry = self.lowest_after_entry = None
                # 取消所有平仓单以及停止单。
                # 停止单只在回测中使用，实盘环境下不适用停止单。
                # 取消平仓单主要是为了防止重复平仓的情况出现。（这种情况在回测情况下又发生，实盘环境下理论上不会发生）
                self.cancel_all_stop_orders()
                self.cancel_all_close_orders()
                # self.cancel_all()
                # 计算累计回撤
                self.acc_drawback_rate += rr
                # 交易期间回车如果大于历史回撤，则以两者最小的为准
                if self.acc_drawback_rate > self.drawback_rate:
                    self.acc_drawback_rate = self.drawback_rate

        # 根据仓位方向，更新相应的跟踪止损价格、成本线止损价格
        self.update_trailing_stop_price(trade.price)
        self.update_stop_loss_price()

    def on_stop(self):
        super().on_stop()
        if self._is_realtime_mode:
            self._set_strategy_status(AccountStrategyStatusEnum.Stopped)
            self.latest_reject_response_order = None
        self.put_event()

    def write_log(self, msg: str, logger_method='info'):
        if self._last_msg == msg:
            return
        try:
            super().write_log(msg)
        except AttributeError:
            # create_instance 的方法建立实例时可能引发如下异常：
            #   File "D:\IDE\vnstudio\lib\site-packages\vnpy\app\portfolio_strategy\template.py", line 231, in write_log
            #     self.strategy_engine.write_log(msg, self)
            # AttributeError: 'NoneType' object has no attribute 'write_log'
            pass

        msg_new = f"{self.strategy_name} {msg}"
        getattr(self.logger, logger_method)(msg_new)
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

    def get_price_by_price_type(self, price_type: PriceTypeEnum) -> float:
        """根据 price_type 获取当前 bar 的对应价格"""
        if price_type == PriceTypeEnum.auto:
            if self.pos > 0:
                price = self.current_bar.high_price
            elif self.pos < 0:
                price = self.current_bar.low_price
            else:
                raise ValueError("pos")
        else:
            price = getattr(self.current_bar, f"{price_type.value}_price")

        return price

    def update_trailing_stop_price(self, price=None):
        """根据仓位方向，更新跟踪止损价格"""
        if self.pos == 0:
            self.trailing_stop_hl_price = 0
            self.trailing_stop_price = 0
            return
        elif self.pos > 0 and self.trailing_stop_rate > 0:
            # 设置跟踪止损价格
            if price is None:
                price = self.get_price_by_price_type(self.trailing_stop_price_type_enum)

            if self.trailing_stop_hl_price == 0 or price > self.trailing_stop_hl_price:
                self.trailing_stop_hl_price = price
                self.trailing_stop_price = price * (1 - self.trailing_stop_rate)

        elif self.pos < 0 < self.trailing_stop_rate:
            # 设置跟踪止损价格
            if price is None:
                price = self.get_price_by_price_type(self.trailing_stop_price_type_enum)

            if self.trailing_stop_hl_price == 0 or price < self.trailing_stop_hl_price:
                self.trailing_stop_hl_price = price
                self.trailing_stop_price = price * (1 + self.trailing_stop_rate)

    def update_stop_loss_price(self):
        """根据仓位方向，更新成本线止损价格"""
        if self.pos == 0:
            self.stop_loss_price = 0
            return
        elif self.pos > 0 and self.stop_loss_rate > 0:
            # 设置成本线止损价格
            self.stop_loss_price = self.avg_entry_price * (1 - self.stop_loss_rate)

        elif self.pos < 0 < self.stop_loss_rate:
            # 设置成本线止损价格
            self.stop_loss_price = self.avg_entry_price * (1 + self.stop_loss_rate)

    def update_stop_price_curr(self) -> bool:
        """
        根据 stop_loss_price 和 trailing_stop_price 更新 stop_price_curr
        :return: True：价格更新 False价格未更新
        """
        if self.pos == 0:
            self.stop_price_curr = 0
            stop_price = 0
        elif self.pos > 0:
            if self.stop_loss_rate > 0:
                stop_price = self.stop_loss_price
            else:
                stop_price = 0

            if self.trailing_stop_rate > 0:
                if stop_price == 0 or stop_price > self.trailing_stop_price:
                    stop_price = self.trailing_stop_price
        else:  # self.pos < 0
            if self.stop_loss_rate > 0:
                stop_price = self.stop_loss_price
            else:
                stop_price = 0

            if self.trailing_stop_rate > 0:
                if stop_price == 0 or stop_price < self.trailing_stop_price:
                    stop_price = self.trailing_stop_price

        if stop_price != self.stop_price_curr:
            self.stop_price_curr = stop_price
            return True

        return False

    def check_and_do_stop(self):
        """检查止损价格，设置条件止损单"""
        if self.update_stop_price_curr() and (self.enable_stop_order or not self._is_realtime_mode):
            if self.stop_vt_orderids is not None and len(self.stop_vt_orderids) > 0:
                for vt_orderid in self.stop_vt_orderids:
                    self.cancel_order(vt_orderid)

                self.stop_vt_orderids = None

            if self.pos > 0:
                self.stop_vt_orderids = self.sell(self.stop_price_curr, abs(self.pos), stop=True)
            elif self.pos < 0:
                self.stop_vt_orderids = self.cover(self.stop_price_curr, abs(self.pos), stop=True)

    def cancel_all_stop_orders(self):
        with self.send_order_dic_lock:
            stop_vt_orderids = self.stop_vt_orderids
            if stop_vt_orderids:
                self.write_log(f"取消所有止损单:{stop_vt_orderids}", 'debug')
                for vt_orderid in stop_vt_orderids:
                    self.cancel_order(vt_orderid=vt_orderid)

            self.stop_vt_orderids = None

    def cancel_all_close_orders(self):
        """取消所有平仓单"""
        with self.send_order_dic_lock:
            if not self._is_realtime_mode:
                close_order_list = [
                    vt_orderid for vt_orderid, (direction, offset) in self.send_order_id_info_dic.items()
                    if offset != Offset.OPEN
                ]
                for vt_orderid in close_order_list:
                    self.cancel_order(vt_orderid)
                    self.send_order_id_info_dic.pop(vt_orderid)
            else:
                close_order_list = [
                    vt_orderid for vt_orderid, order in self.on_order_received_dic.items()
                    if order.offset != Offset.OPEN and order.status in (
                        Status.SUBMITTING, Status.NOTTRADED, Status.PARTTRADED)
                ]
                for vt_orderid in close_order_list:
                    self.cancel_order(vt_orderid)

    def is_same_as_order(self, order: OrderData, direction: Direction, vol: int, price: float):
        """
        判断当前订单是否与目标订单一致
        由于存在时间同步问题，因此对于订单 Vol 的判断，只要在尚未成交部分 到 全部订单之间的数值即为一致
        """
        return order.direction == direction and (order.volume - order.traded) <= vol <= order.volume and np.round(
            order.price / self.vt_symbol_price_tick) == np.round(price / self.vt_symbol_price_tick)

    def calc_holding_relative_properties(self):
        """计算盘中相关变量，包括 lowest_after_entry, highest_after_entry, acc_drawback_rate, drawback_rate 等"""
        if self.pos != 0:
            # 首次建仓时去收盘价
            self.lowest_after_entry = self.current_bar.close_price \
                if self.lowest_after_entry is None else min(self.lowest_after_entry, self.current_bar.low_price)
            self.highest_after_entry = self.current_bar.close_price \
                if self.highest_after_entry is None else max(self.highest_after_entry, self.current_bar.high_price)

            if self.pos > 0:
                self.drawback_rate = self.current_bar.close_price / self.highest_after_entry - 1
            elif self.pos < 0:
                self.drawback_rate = 1 - self.current_bar.close_price / self.lowest_after_entry
        else:
            self.drawback_rate = 0

        return self.drawback_rate

    def calc_acc_drawback_rate(self):
        """计算盘中的累计回撤"""
        if self.pos > 0:
            return min(
                self.acc_drawback_rate + self.current_bar.close_price / self.avg_entry_price - 1,
                self.drawback_rate)
        elif self.pos < 0:
            return min(
                self.acc_drawback_rate + 1 - self.current_bar.close_price / self.avg_entry_price,
                self.drawback_rate)
        else:
            return self.acc_drawback_rate

    def reset_acc_drawback_rate(self):
        """
        重置最大回测，
        由于 drawback_rate 的计算过程需要 lowest_after_entry、highest_after_entry因此两个同时也被重置为当前bar的close
        """
        self.acc_drawback_rate = 0
        self.drawback_rate = 0
        self.lowest_after_entry = self.current_bar.close_price
        self.highest_after_entry = self.current_bar.close_price


class TargetPosAndPriceTemplate(CtaTemplate):
    """
    该模板将逐步被 TargetPosAndPriceNoStopOrderTemplate 替代
    """
    # 目标仓位
    _target_pos = 0
    # 目标价格
    target_price = 0
    # 目标方向是否
    allow_trade_direction = AllowTradeDirectionEnum.ALL.value

    variables = ["target_pos", "target_price", "bar_count", "fire_stop_order"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        if "target_pos" not in self.variables:
            # 使用 TargetPosAndPriceTemplate 目标，target_pos 变量必须在 variables 列表中，否则会出现隔夜目标持仓数据丢失的情况。
            self.variables.append("target_pos")
        self.allow_trade_direction_enum = AllowTradeDirectionEnum(self.allow_trade_direction)
        # 算法交易线程
        self.algo_trading_thread = None
        self.algo_trading_running = True
        # 部分情况下服务器响应比较慢,测试中存在5秒钟才给返回状态的情况,因此这里将等待延迟加长到 20s
        self.send_order_wait_seconds = 20
        # 补充 variables
        for _ in ["target_pos", "target_price", "bar_count"]:
            if _ not in self.variables:
                self.variables.append(_)

        # —————————————————— 止损功能相关变量开始 ————————————————
        self.fire_stop_order = False
        self.fire_stop_order_dt = None
        if "fire_stop_order" not in self.variables and (self.stop_loss_rate > 0 or self.trailing_stop_rate > 0):
            self.variables.append("fire_stop_order")
        # —————————————————— 止损功能相关变量结束 ————————————————

    def on_start(self) -> None:
        super().on_start()
        if self._is_realtime_mode:
            # 实盘情况，执行异步算法交易
            self.algo_trading_running = True
            self.algo_trading_thread = threading.Thread(target=self._algo_trading_2_target_pos_thread, daemon=True)
            self.algo_trading_thread.start()

    @property
    def target_pos(self):
        if self.fire_stop_order:
            return 0
        else:
            return self._target_pos

    @target_pos.setter
    def target_pos(self, value):
        self._target_pos = value

    def set_target_pos(self, target_pos, price=None):
        """设置目标持仓以及价格"""
        if price is None:
            self.target_price = self.current_bar.close_price
        else:
            self.target_price = np.round(price / self.vt_symbol_price_tick) * self.vt_symbol_price_tick

        # 检查是否存在方向限制
        if (
                self.allow_trade_direction_enum == AllowTradeDirectionEnum.LONG_ONLY and target_pos < 0
        ) or (
                self.allow_trade_direction_enum == AllowTradeDirectionEnum.Short_ONLY and target_pos > 0
        ):
            target_pos = 0

        # 当仓位从 非0 -> 0 或 反向建仓 时
        # 1) 情况此前的停止单
        # 2) 重置 fire_stop_order 状态
        if self._target_pos < 0 <= target_pos or self._target_pos > 0 >= target_pos:
            if self.stop_vt_orderids is not None and len(self.stop_vt_orderids) > 0:
                self.write_log(f"目标仓位方向改变，取消停止单 {self.stop_vt_orderids}", 'debug')
                # self.cancel_all_stop_orders()
                self.cancel_all()

            if self.fire_stop_order:
                self.fire_stop_order = False
                self.fire_stop_order_dt = None

        self.target_pos = int(target_pos)
        if not self.trading:
            return

        if target_pos != self.pos and not self.fire_stop_order and not self.stop_opening_pos:
            self.write_log(f"最新持仓目标 {target_pos} {self.target_price}", 'debug')

        if not self._is_realtime_mode:
            # 回测环境下走同步交易
            self.handle_pos_2_target_backtest_only()

    def handle_pos_2_target_backtest_only(self):
        """按目标价格及持仓进行处理(仅回测使用)"""
        if not self.trading:
            return
        if self.fire_stop_order:
            return
        self.write_log(f"handle_pos_2_target_backtest_only 取消全部订单", 'debug')
        self.cancel_all()
        current_pos = self.pos
        price = self.target_price
        target_pos = self.target_pos
        volume = abs(target_pos - current_pos)
        if 0 <= target_pos < current_pos:
            # 减仓
            # self.write_log(f"平多 {current_pos} -> {target_pos}")
            self.sell(price, volume)
        elif target_pos < 0 < current_pos:
            # 多翻空
            # self.write_log(f"多翻空 {current_pos} -> {target_pos}")
            self.sell(price, abs(current_pos))
            self.short(price, abs(target_pos))  # 实盘情况会造成丢单现象
        elif target_pos < current_pos <= 0:
            volume = abs(target_pos - current_pos)
            # self.write_log(f"开空 {current_pos} -> {target_pos}")
            self.short(price, volume)
        elif current_pos < target_pos <= 0:
            # self.write_log(f"平空 {current_pos} -> {target_pos}")
            volume = abs(target_pos - current_pos)
            self.cover(price, volume)
        elif current_pos < 0 < target_pos:
            # self.write_log(f"空翻多 {current_pos} -> {target_pos}")
            self.cover(price, abs(current_pos))
            self.buy(price, abs(target_pos))  # 实盘情况会造成丢单现象
        elif 0 <= current_pos < target_pos:
            # self.write_log(f"开多 {current_pos} -> {target_pos}")
            volume = abs(target_pos - current_pos)
            self.buy(price, volume)

    def _algo_trading_2_target_pos_thread(self):
        self.write_log("开启算法交易")
        try:
            while self.algo_trading_running:
                time.sleep(0.5)
                if not self._can_do_algo_trading():
                    continue
                # self.write_log('可以执行算法交易')
                self.algo_trading_2_target_pos()
        except:
            self.write_log(f"算法交易异常", 'error')
            self.logger.exception("%s 算法交易异常", self.strategy_name)
        finally:
            self.write_log("关闭算法交易", "warning")

    def _can_do_algo_trading(self) -> bool:
        """检查是否可以执行算法交易"""
        if not self.trading:
            return False
        if self.last_tick_time is None:
            # 未开盘期间不进行算法交易
            return False
        if self.fire_stop_order:
            # 已触发止损单，关闭算法交易
            return False

        now = datetime.now()
        # 多线程情况下可能存在 last_tick_time > now 的情况，因此用绝对值
        seconds_since_last_tick = abs(now - self.last_tick_time).seconds
        if seconds_since_last_tick > 5:
            return False
        if self.latest_reject_response_order is not None:
            dt = self.latest_reject_response_order.datetime.replace(tzinfo=None)
            if abs(datetime.now() - dt).seconds <= 60:
                return False

        # 检查所有类型的交易是否存在均处于有效状态。
        # 如果存在已经发报，但尚未得到服务器响应的情况则需要等待服务器响应后继续后续的操作
        with self.send_order_dic_lock:
            for num, ((direction, offset), (send_dt, on_dt, status)) in enumerate(
                    self.send_and_on_order_dt_dic.items(), start=1):
                if status in (Status.ALLTRADED, Status.CANCELLED, Status.REJECTED):
                    # 已经成交的订单不影响算法交易判断
                    continue
                if send_dt is None:
                    self.write_log(f"交易状态存在异常，send_dt={send_dt}，on_dt={on_dt}, status={status}", 'error')
                    return False
                if on_dt is None or send_dt > on_dt:
                    if abs(min(now, self.last_tick_time) - send_dt).seconds > self.send_order_wait_seconds:
                        # 发送订单 回应时间超时
                        # 无须取消订单，因为服务端没有确认收到订单
                        continue
                    else:
                        self.write_log(
                            f"订单已发送，但尚未得到回应，且尚未超时，继续等待，"
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, {offset} {direction}",
                            'warning'
                        )
                        return False
                elif status == Status.SUBMITTING:
                    # 2021-02-27
                    # 夜盘时,有时会发生服务器返回 submit 状态后,不再处理的清空.导致订单堵塞,无法进行后续交易.
                    # 以下代码针对此种清空进行了修补及相关数据的清理.
                    if abs(min(now, self.last_tick_time) - send_dt).seconds > self.send_order_wait_seconds * 2:
                        # 发送订单 回应时间严重超时 不等待回应,继续执行后面的交易逻辑
                        self.write_log(
                            f"订单已提交，且严重超时,取消订单后继续后面的交易逻辑."
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, "
                            f"orderid={self._last_order.orderid if self._last_order is not None else '(None)'}",
                            'warning'
                        )
                        # 清理无效订单:包括非活跃,以及严重超时订单
                        for vt_orderid in list(self.on_order_received_dic.keys()):
                            order = self.on_order_received_dic[vt_orderid]
                            order_status = Offset.CLOSE if order.offset in (
                                Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY) else order.offset
                            if not (order.is_active()):
                                del self.on_order_received_dic[vt_orderid]
                            if order.direction == direction and (order_status == offset):
                                del self.on_order_received_dic[vt_orderid]

                    if abs(min(now, self.last_tick_time) - send_dt).seconds > self.send_order_wait_seconds:
                        # 发送订单 回应时间超时 取消订单
                        self.cancel_order(self._last_order.vt_orderid)
                        self.write_log(
                            f"订单已提交，且超时,取消订单."
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, "
                            f"orderid={self._last_order.orderid if self._last_order is not None else '(None)'}",
                            'warning'
                        )
                        return False
                    else:
                        self.write_log(
                            f"订单已提交，但未进一步处理，存在被拒绝可能，需要等待结果方可进行后续操作，"
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, "
                            f"orderid={self._last_order.orderid if self._last_order is not None else '(None)'}",
                            'warning'
                        )
                        return False

        return True

    def algo_trading_2_target_pos(self):
        """
        算计交易，绝对下单实际
        """
        # 检查持仓
        # 计算是否存在仓位不匹配情况
        current_pos = self.pos
        target_pos = self.target_pos
        volume = abs(target_pos - current_pos)
        if volume == 0:
            return
        # self.logger.info(f"执行算法交易 {current_pos} -> {target_pos}")
        if self.target_price <= 0.0:
            if self.current_bar is not None and self.current_bar.close_price > 0:
                self.target_price = self.current_bar.close_price
                msg = 'target_price 价格无效，使用上一根K线收盘价'
                self.write_log(msg, 'warning')
            elif self.last_tick is not None:
                # 使用被动价格
                self.target_price = self.last_tick.bid_price_1 \
                    if target_pos > current_pos else self.last_tick.ask_price_1
                msg = f'target_price 价格无效，使用上一Tick{"买1价格" if target_pos > current_pos else "卖1价格"}'
                self.write_log(msg, 'warning')

        price = self.target_price
        # self.write_log('运行算法交易')
        # 检查是否存在未成交订单
        active_order_close: Optional[OrderData] = None
        active_order_open: Optional[OrderData] = None
        has_unavailable_order = False
        # list(self.active_order_list) 为了防止将 self.active_order_list 锁住，
        # 避免影响交易
        with self.send_order_dic_lock:
            active_order_list = list(self.on_order_received_dic.values())
            # order_count = len(self.on_order_received_dic)

        for num, order in enumerate(active_order_list, start=1):
            if not order.is_active():
                # 仅选取活跃订单
                continue
            order_dt = order.datetime
            # 即使 order_dt is None 依然需要被算作服务器已经接受到order，否则会出现重复下单的情况
            # if order_dt is None:
            #     # order_dt is None 代表订单还没有被服务器处理
            #     continue
            # self.write_log(
            #     f"{num}/{order_count}) algo thread: {order.orderid} {order.offset}
            #     active={order.is_active()} dt={order.datetime}")
            if order.offset == Offset.OPEN:
                active_order_open = order
            else:
                active_order_close = order

            if order_dt is not None:
                now = datetime.now().replace(tzinfo=order_dt.tzinfo)
                if abs(now - order_dt).seconds >= 60 and order.status == Status.SUBMITTING:
                    # 取消超时未成交订单
                    # order.create_cancel_request()
                    self.write_log("取消超过时限未响应的订单")
                    self.cancel_order(order.vt_orderid)
                    has_unavailable_order = True
                    continue

        if has_unavailable_order:
            # 待所有无效订单取消后才可以下新的订单
            return

        # if active_order_close is not None:
        #     self.write_log("存在未成交的平仓单")
        # if active_order_open is not None:
        #     self.write_log("存在未成交的开仓单")

        if 0 <= target_pos < current_pos:
            # 平多
            if active_order_open:
                # 如果存在开仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_open.create_cancel_request()
                self.write_log("平多 取消已存在的开仓单")
                self.cancel_order(active_order_open.vt_orderid)

            elif active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.SHORT, volume, price):
                    # 与当前订单一致
                    self.write_log(f"平多 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                   f"{active_order_close.vt_orderid} 一致，不再重复下单")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log("平多 目标订单与当前订单不一致， 取消原订单")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
            else:
                self.write_log(f"平多 {current_pos} -> {target_pos}")
                self.sell(price, volume)

        elif target_pos < 0 < current_pos:
            # 多翻空
            # 先检查平仓单是否已经下出去了
            # 如果平仓单已经下出去了，再下开仓单
            is_close_available = True
            close_pos = abs(current_pos)
            if active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.SHORT, close_pos, price):
                    # 与当前订单一致
                    self.write_log(f"多翻空 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                   f"{active_order_close.vt_orderid} 一致，不再重复下单")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log("多翻空 平仓操作目标订单与当前订单不一致， 取消原订单")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
                    is_close_available = False
            else:
                self.write_log(f"多翻空 {current_pos} -> {target_pos} 先平仓")
                self.sell(price, close_pos)
                is_close_available = False

            if active_order_close:
                open_pos = abs(target_pos)
                if active_order_open:
                    if not is_close_available:
                        self.write_log("多翻空 平仓单未生效前，现存开仓单需要取消")
                        self.cancel_order(active_order_open.vt_orderid)
                    elif self.is_same_as_order(active_order_open, Direction.SHORT, open_pos, price):
                        # 检查现存订单是否与当前订单一致：
                        # 如果一致，则不再重新下单
                        # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                        # 与当前订单一致
                        self.write_log(f"多翻空 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                       f"{active_order_open.vt_orderid} 一致，不再重复下单")
                        pass
                    else:
                        # 与当前订单不一致
                        self.write_log("多翻空 开仓操作目标订单与当前订单不一致， 取消原订单")
                        # self.last_send_order_dt = datetime.now()
                        # active_order_open.create_cancel_request()
                        self.cancel_order(active_order_open.vt_orderid)
                elif is_close_available:
                    if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                        self.write_log(f"多翻空 {current_pos} -> {target_pos} 再开仓")
                        self.short(price, open_pos)
                else:
                    self.write_log(f"多翻空 平仓单未生效前，开仓单暂不下单")

        elif target_pos < current_pos <= 0:
            # 开空
            volume = abs(target_pos - current_pos)
            if active_order_close:
                # 如果存在平仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_close.create_cancel_request()
                self.write_log("开空 取消已存在的平仓单")
                self.cancel_order(active_order_close.vt_orderid)

            elif active_order_open:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_open, Direction.SHORT, volume, price):
                    # 与当前订单一致
                    self.write_log(f"开空 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                   f"{active_order_open.vt_orderid} 一致，不再重复下单")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log("开空 目标订单与当前订单不一致， 取消原订单")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_open.create_cancel_request() 无效
                    self.cancel_order(active_order_open.vt_orderid)
            else:
                if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                    self.write_log(f"开空 {current_pos} -> {target_pos}")
                    self.short(price, volume)

        elif current_pos < target_pos <= 0:
            # 平空
            if active_order_open:
                # 如果存在开仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_open.create_cancel_request()
                self.write_log("平空 取消已存在的开仓单")
                self.cancel_order(active_order_open.vt_orderid)

            elif active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.LONG, volume, price):
                    # 与当前订单一致
                    self.write_log(f"平空 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                   f"{active_order_close.vt_orderid} 一致，不再重复下单")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log("平空 目标订单与当前订单不一致， 取消原订单")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
            else:
                self.write_log(f"平空 {current_pos} -> {target_pos}")
                volume = abs(target_pos - current_pos)
                self.cover(price, volume)

        elif current_pos < 0 < target_pos:
            # 空翻多
            # 先检查平仓单是否已经下出去了
            # 如果平仓单已经下出去了，再下开仓单
            is_close_available = True
            close_pos = abs(current_pos)
            if active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.LONG, close_pos, price):
                    # 与当前订单一致
                    self.write_log(f"空翻多 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                   f"{active_order_close.vt_orderid} 一致，不再重复下单")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log("空翻多 平仓操作目标订单与当前订单不一致， 取消原订单")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
                    is_close_available = False
            else:
                self.write_log(f"空翻多 {current_pos} -> {target_pos} 先平仓")
                self.cover(price, close_pos)
                is_close_available = False

            if active_order_close:
                open_pos = abs(target_pos)
                if active_order_open:
                    if not is_close_available:
                        self.write_log("空翻多 平仓单未生效前，现存开仓单需要取消")
                        self.cancel_order(active_order_open.vt_orderid)
                    elif self.is_same_as_order(active_order_open, Direction.LONG, open_pos, price):
                        # 检查现存订单是否与当前订单一致：
                        # 如果一致，则不再重新下单
                        # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                        # 与当前订单一致
                        self.write_log(f"空翻多 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                       f"{active_order_open.vt_orderid} 一致，不再重复下单")
                        pass
                    else:
                        # 与当前订单不一致
                        self.write_log("空翻多 开仓操作目标订单与当前订单不一致， 取消原订单")
                        # self.last_send_order_dt = datetime.now()
                        # active_order_open.create_cancel_request() 无效
                        self.cancel_order(active_order_open.vt_orderid)
                elif is_close_available:
                    if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                        self.write_log(f"空翻多 {current_pos} -> {target_pos} 再开仓")
                        self.buy(price, open_pos)
                else:
                    self.write_log(f"空翻多 平仓单未生效前，开仓单暂不下单")

        elif 0 <= current_pos < target_pos:
            # 开多
            if active_order_close:
                # 如果存在平仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_close.create_cancel_request() 无效
                self.write_log("开多 取消已存在的平仓单")
                self.cancel_order(active_order_close.vt_orderid)

            elif active_order_open:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_open, Direction.LONG, volume, price):
                    # 与当前订单一致
                    self.write_log(f"开多 {current_pos} -> {target_pos} 目标订单与当前订单 "
                                   f"{active_order_open.vt_orderid} 一致，不再重复下单")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"开多 目标订单与当前订单不一致，取消原订单。"
                                   f"\n原订单 {active_order_open.volume} {active_order_open.price}。"
                                   f"\n新订单 {volume} {price}")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_open.create_cancel_request() 无效
                    self.cancel_order(active_order_open.vt_orderid)
            else:
                if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                    self.write_log(f"开多 {current_pos} -> {target_pos} {price}")
                    volume = abs(target_pos - current_pos)
                    self.buy(price, volume)

    def on_tick(self, tick: TickData) -> bool:
        ret = super().on_tick(tick)
        # 仅实盘环境下进行检查，其实回测环境下通常都是 Minute bar 数据因此不会触发 on_tick 函数
        if self._is_realtime_mode:
            self.update_fire_stop_order(tick.last_price)

        return ret

    def on_bar(self, bar: BarData):
        super().on_bar(bar)
        # 仅回测环境下检查，实盘环境下通过 on_tick 触发检查
        if not self._is_realtime_mode:
            self.update_fire_stop_order(bar.close_price)

    def update_fire_stop_order(self, price):
        if self.pos > 0 and self.stop_price_curr != 0 and price < self.stop_price_curr:
            self.fire_stop_order = True
        elif self.pos < 0 and self.stop_price_curr != 0 and price > self.stop_price_curr:
            self.fire_stop_order = True


class TargetPosAndPriceNoStopOrderTemplate(CtaTemplate):
    """
    在上一个版本 TargetPosAndPriceTemplate 的基础上将 stop单 统一使用 set_target_pos 方式实现。
    避免出现 stop 单没有成交出去的可能
    具体实现逻辑：
    1）tick数据检查是否触发止损。
    2）执行止损过程中，进行超时检查。超过时间限制则撤单后已盘口加执行止损
    3）执行止损后，移除所有止损单。
    """
    # 目标仓位
    _target_pos = 0
    # 目标价格
    target_price = 0
    # 建仓基数，建立空头或多头仓位的数量
    base_position = 1
    # 目标方向是否
    allow_trade_direction = AllowTradeDirectionEnum.ALL.value

    variables = ["target_pos", "target_price", "bar_count", "fire_stop_order"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        # 算法交易线程
        self.algo_trading_thread = None
        self.algo_trading_running = True
        # 部分情况下服务器响应比较慢,测试中存在5秒钟才给返回状态的情况,因此这里将等待延迟加长到 20s
        self.send_order_wait_seconds = 20
        # 记录当前策略是否被拒绝平仓
        self.close_rejected = False
        self.allow_trade_direction_enum: AllowTradeDirectionEnum = AllowTradeDirectionEnum(self.allow_trade_direction)
        # —————————————————— 止损功能相关变量开始 ————————————————
        self.fire_stop_order = False
        self.fire_stop_order_dt = None
        # 禁止 以 stop 单进行止损
        self.enable_stop_order = False
        # 补充 variables
        for _ in ["target_pos", "target_price", "bar_count"]:
            if _ not in self.variables:
                self.variables.append(_)

        if "fire_stop_order" not in self.variables and (self.stop_loss_rate > 0 or self.trailing_stop_rate > 0):
            self.variables.append("fire_stop_order")
        # —————————————————— 止损功能相关变量结束 ————————————————

    def on_start(self) -> None:
        super().on_start()
        if self._is_realtime_mode:
            # 实盘情况，执行异步算法交易
            self.algo_trading_running = True
            self.algo_trading_thread = threading.Thread(target=self._algo_trading_2_target_pos_thread, daemon=True)
            self.algo_trading_thread.start()

    @property
    def target_pos(self):
        if self.fire_stop_order:
            return 0
        else:
            return self._target_pos

    @target_pos.setter
    def target_pos(self, value):
        self._target_pos = value

    def set_target_pos(self, target_pos, price=None):
        """设置目标持仓以及价格"""
        if price is None:
            self.target_price = self.current_bar.close_price
        else:
            self.target_price = np.round(price / self.vt_symbol_price_tick) * self.vt_symbol_price_tick

        # 检查是否存在方向限制
        if (
                self.allow_trade_direction_enum == AllowTradeDirectionEnum.LONG_ONLY and target_pos < 0
        ) or (
                self.allow_trade_direction_enum == AllowTradeDirectionEnum.Short_ONLY and target_pos > 0
        ):
            target_pos = 0

        # 当仓位从 非0 -> 0 或 反向建仓 时
        # 1) 情况此前的停止单
        # 2) 重置 fire_stop_order 状态
        if self._target_pos < 0 <= target_pos or self._target_pos > 0 >= target_pos:
            if self.stop_vt_orderids is not None and len(self.stop_vt_orderids) > 0:
                self.write_log(f"目标仓位方向改变，取消停止单 {self.stop_vt_orderids}", 'debug')
                # self.cancel_all_stop_orders()
                self.cancel_all()

            if self.fire_stop_order:
                self.write_log(f"fire_stop_order 状态被重置为 False", 'debug')
                self.fire_stop_order = False
                self.fire_stop_order_dt = None

        self.target_pos = target_pos = int(target_pos)
        if not self.trading:
            return

        if target_pos != self.pos and not self.fire_stop_order and not self.stop_opening_pos:
            self.write_log(f"最新持仓目标 {target_pos} {self.target_price}", 'debug')

        if not self._is_realtime_mode:
            # 回测环境下走同步交易
            self.handle_pos_2_target_backtest_only()

    def handle_pos_2_target_backtest_only(self):
        """按目标价格及持仓进行处理(仅回测使用)"""
        if not self.trading:
            return
        if self.fire_stop_order:
            return
        self.write_log(f"handle_pos_2_target_backtest_only 取消全部订单", 'debug')
        self.cancel_all()
        current_pos = self.pos
        price = self.target_price
        target_pos = self.target_pos
        volume = abs(target_pos - current_pos)
        if 0 <= target_pos < current_pos:
            # 减仓
            # self.write_log(f"平多 {current_pos} -> {target_pos}")
            self.sell(price, volume)
        elif target_pos < 0 < current_pos:
            # 多翻空
            # self.write_log(f"多翻空 {current_pos} -> {target_pos}")
            self.sell(price, abs(current_pos))
            self.short(price, abs(target_pos))  # 实盘情况会造成丢单现象
        elif target_pos < current_pos <= 0:
            volume = abs(target_pos - current_pos)
            # self.write_log(f"开空 {current_pos} -> {target_pos}")
            self.short(price, volume)
        elif current_pos < target_pos <= 0:
            # self.write_log(f"平空 {current_pos} -> {target_pos}")
            volume = abs(target_pos - current_pos)
            self.cover(price, volume)
        elif current_pos < 0 < target_pos:
            # self.write_log(f"空翻多 {current_pos} -> {target_pos}")
            self.cover(price, abs(current_pos))
            self.buy(price, abs(target_pos))  # 实盘情况会造成丢单现象
        elif 0 <= current_pos < target_pos:
            # self.write_log(f"开多 {current_pos} -> {target_pos}")
            volume = abs(target_pos - current_pos)
            self.buy(price, volume)

    def _algo_trading_2_target_pos_thread(self):
        self.write_log("开启算法交易")
        try:
            while self.algo_trading_running:
                time.sleep(0.5)
                if not self._can_do_algo_trading():
                    # self.write_log(f'无法执行算法交易 {self.pos} -> {self.target_pos}')
                    continue
                # self.write_log(f'可以执行算法交易 {self.pos} -> {self.target_pos}')
                self.algo_trading_2_target_pos()
        except:
            self.write_log(f"算法交易异常", 'error')
            self.logger.exception("%s 算法交易异常", self.strategy_name)
        finally:
            self.write_log("关闭算法交易", "warning")

    def _can_do_algo_trading(self) -> bool:
        """检查是否可以执行算法交易"""
        if not self.trading:
            return False
        # self.logger.info(f"检查算法交易 last_tick_time={self.last_tick_time} "
        #                  f"latest_reject_response_order={self.latest_reject_response_order}")
        if self.last_tick_time is None:
            # 未开盘期间不进行算法交易
            return False
        # if self.fire_stop_order:
        #     # 已触发止损单，关闭算法交易
        #     return False

        now = datetime.now()
        # 多线程情况下可能存在 last_tick_time > now 的情况，因此用绝对值
        seconds_since_last_tick = abs(now - self.last_tick_time).seconds
        if seconds_since_last_tick > 5:
            # self.logger.info(
            #     f"检查算法交易 last_tick_time= {self.last_tick_time} {seconds_since_last_tick}")
            return False
        if self.latest_reject_response_order is not None:
            dt = self.latest_reject_response_order.datetime.replace(tzinfo=None)
            if abs(datetime.now() - dt).seconds <= 60:
                # self.logger.info(
                #     f"检查算法交易 latest_reject_response_order= {self.latest_reject_response_order}")
                return False

        # 检查所有类型的交易是否存在均处于有效状态。
        # 如果存在已经发报，但尚未得到服务器响应的情况则需要等待服务器响应后继续后续的操作
        with self.send_order_dic_lock:
            # self.logger.info(
            #     f"检查算法交易 len(send_and_on_order_dt_dic)={len(self.send_and_on_order_dt_dic)}")
            for num, ((direction, offset), (send_dt, on_dt, status)) in enumerate(
                    self.send_and_on_order_dt_dic.items(), start=1):
                if status in (Status.ALLTRADED, Status.REJECTED, Status.CANCELLED):
                    # 已经成交的订单不影响算法交易判断
                    continue
                if send_dt is None:
                    self.write_log(f"交易状态存在异常，send_dt={send_dt}，on_dt={on_dt}, status={status}", 'error')
                    return False
                if on_dt is None or send_dt > on_dt:
                    if abs(min(now, self.last_tick_time) - send_dt).seconds > self.send_order_wait_seconds:
                        # 发送订单 回应时间超时
                        # 无须取消订单，因为服务端没有确认收到订单
                        continue
                    else:
                        self.write_log(
                            f"订单已发送，但尚未得到回应，且尚未超时，继续等待，"
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, {offset} {direction}",
                            'warning'
                        )
                        return False
                elif status == Status.SUBMITTING:
                    # 2021-02-27
                    # 夜盘时,有时会发生服务器返回 submit 状态后,不再处理的情况.导致订单堵塞,无法进行后续交易.
                    # 以下代码针对此种清空进行了修补及相关数据的清理.
                    if abs(min(now, self.last_tick_time) - send_dt).seconds > self.send_order_wait_seconds * 2:
                        # 发送订单 回应时间严重超时 不等待回应,继续执行后面的交易逻辑
                        self.write_log(
                            f"订单已提交，且严重超时,取消订单后继续后面的交易逻辑."
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, "
                            f"orderid={self._last_order.orderid if self._last_order is not None else '(None)'}",
                            'warning'
                        )
                        # 清理无效订单:包括非活跃,以及严重超时订单
                        for vt_orderid in list(self.on_order_received_dic.keys()):
                            order = self.on_order_received_dic[vt_orderid]
                            order_status = Offset.CLOSE if order.offset in (
                                Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY) else order.offset
                            if not (order.is_active()):
                                del self.on_order_received_dic[vt_orderid]
                            if order.direction == direction and (order_status == offset):
                                del self.on_order_received_dic[vt_orderid]

                    if abs(min(now, self.last_tick_time) - send_dt).seconds > self.send_order_wait_seconds:
                        # 发送订单 回应时间超时 取消订单
                        self.cancel_order(self._last_order.vt_orderid)
                        self.write_log(
                            f"订单已提交，且超时,取消订单."
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, "
                            f"orderid={self._last_order.orderid if self._last_order is not None else '(None)'}",
                            'warning'
                        )
                        return False
                    else:
                        self.write_log(
                            f"订单已提交，但未进一步处理，存在被拒绝可能，需要等待结果方可进行后续操作，"
                            f"send_dt={send_dt}，on_dt={on_dt}, status={status}, "
                            f"orderid={self._last_order.orderid if self._last_order is not None else '(None)'}",
                            'warning'
                        )
                        return False

        return True

    def algo_trading_2_target_pos(self):
        """
        算计交易，绝对下单实际
        """
        # 检查持仓
        # 计算是否存在仓位不匹配情况
        current_pos = self.pos
        target_pos = self.target_pos
        volume = abs(target_pos - current_pos)
        if volume == 0:
            # 重置 self.close_rejected 标志位
            self.close_rejected = False
            return
        if self.target_price <= 0.0:
            if self.current_bar is not None and self.current_bar.close_price > 0:
                self.target_price = self.current_bar.close_price
                msg = f'target_price 价格无效，{current_pos} -> {target_pos} 使用上一根K线收盘价'
                self.write_log(msg, 'warning')
            elif self.last_tick is not None:
                # 使用被动价格
                self.target_price = self.last_tick.bid_price_1 \
                    if target_pos > current_pos else self.last_tick.ask_price_1
                msg = f'target_price 价格无效，{current_pos} -> {target_pos} 使用(被动价格)上一Tick' \
                      f'{"买1价格" if target_pos > current_pos else "卖1价格"}'
                self.write_log(msg, 'warning')

        elif self.fire_stop_order and (
                self.fire_stop_order_dt is None or
                (datetime.now() - self.fire_stop_order_dt).seconds > self.send_order_wait_seconds
        ):
            # 止损单超时，更新止损价格。优先通过tick数据更新价格，如果没有则使用bar数据进行更新
            target_price_last = self.target_price
            if self.last_tick is not None:
                # 使用主动价格
                if target_pos > current_pos:
                    target_price = self.last_tick.ask_price_1
                    if self.target_price < target_price:
                        self.target_price = target_price
                else:  # target_pos < current_pos
                    target_price = self.last_tick.bid_price_1
                    if self.target_price > target_price:
                        self.target_price = target_price

                if target_price_last != self.target_price:
                    msg = f'止损价格 {target_price_last} 保单时间超时，' \
                          f'{current_pos} -> {target_pos} 使用(主动价格)上一Tick' \
                          f'{"卖1价格" if target_pos > current_pos else "买1价格"} {self.target_price}'
                    self.write_log(msg, 'warning')

            elif self.current_bar is not None and self.current_bar.close_price > 0:
                if (
                        self.current_bar.close_price > target_price_last and target_pos > current_pos
                ) or (
                        self.current_bar.close_price < target_price_last and target_pos < current_pos
                ):
                    self.target_price = self.current_bar.close_price
                    msg = f'止损价格 {target_price_last} 保单时间超时，' \
                          f'{current_pos} -> {target_pos} 使用上一根K线收盘价 {self.target_price}'
                    self.write_log(msg, 'warning')
            else:
                msg = f'止损价格 {target_price_last} 保单时间超时，没有找到新的可用价格'
                self.write_log(msg, 'error')

        # self.write_log('运行算法交易')
        # 检查是否存在未成交订单
        active_order_close: Optional[OrderData] = None
        active_order_open: Optional[OrderData] = None
        has_unavailable_order = False
        # list(self.active_order_list) 为了防止将 self.active_order_list 锁住，
        # 避免影响交易
        with self.send_order_dic_lock:
            active_order_list = list(self.on_order_received_dic.values())
            # order_count = len(self.on_order_received_dic)

        for num, order in enumerate(active_order_list, start=1):
            if not order.is_active():
                # 仅选取活跃订单
                continue
            order_dt = order.datetime
            # 即使 order_dt is None 依然需要被算作服务器已经接受到order，否则会出现重复下单的情况
            # if order_dt is None:
            #     # order_dt is None 代表订单还没有被服务器处理
            #     continue
            # self.write_log(
            #     f"{num}/{order_count}) algo thread: {order.orderid} {order.offset}
            #     active={order.is_active()} dt={order.datetime}")
            if order.offset == Offset.OPEN:
                active_order_open = order
            else:
                active_order_close = order

            if order_dt is not None:
                now = datetime.now().replace(tzinfo=order_dt.tzinfo)
                if abs(now - order_dt).seconds >= 60 and order.status == Status.SUBMITTING:
                    # 取消超时未成交订单
                    # order.create_cancel_request()
                    self.write_log(f"取消超过时限未响应的订单[{order.vt_orderid}] "
                                   f"{order.offset}{order.direction} {order.status}")
                    self.cancel_order(order.vt_orderid)
                    has_unavailable_order = True
                    continue

        if has_unavailable_order:
            # 待所有无效订单取消后才可以下新的订单
            return

        if self.close_rejected:
            # 平仓动作被拒绝，因此直接开仓的方式达到目标仓位
            self.send_order_2_target_pos_close_rejected(active_order_close, active_order_open)
        else:
            self.send_order_2_target_pos(active_order_close, active_order_open)

    def send_order_2_target_pos(self, active_order_close, active_order_open):
        """用于发送订单平衡目标仓位"""
        price = self.target_price
        current_pos = self.pos
        target_pos = self.target_pos
        volume = abs(target_pos - current_pos)
        if 0 <= target_pos < current_pos:
            # 平多
            if active_order_open:
                # 如果存在开仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_open.create_cancel_request()
                self.write_log(f"平多 取消已存在的开仓单[{active_order_open.vt_orderid}]")
                self.cancel_order(active_order_open.vt_orderid)

            elif active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.SHORT, volume, price):
                    # 与当前订单一致
                    # self.write_log("平多 目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"平多 目标订单与当前订单不一致， 取消原订单[{active_order_close.vt_orderid}]")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
            else:
                self.write_log(f"平多 {current_pos} -> {target_pos}")
                self.sell(price, volume)

        elif target_pos < 0 < current_pos:
            # 多翻空
            # 先检查平仓单是否已经下出去了
            # 如果平仓单已经下出去了，再下开仓单
            is_close_available = True
            close_pos = abs(current_pos)
            if active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.SHORT, close_pos, price):
                    # 与当前订单一致
                    # self.write_log("多翻空 平仓操作目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"多翻空 平仓操作目标订单与当前订单不一致， 取消原订单[{active_order_close.vt_orderid}]")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
                    is_close_available = False
            else:
                self.write_log(f"多翻空 {current_pos} -> {target_pos} 先平仓")
                self.sell(price, close_pos)
                is_close_available = False

            if active_order_close:
                open_pos = abs(target_pos)
                if active_order_open:
                    if not is_close_available:
                        self.write_log(f"多翻空 平仓单未生效前，现存开仓单需要取消[{active_order_open.vt_orderid}]")
                        self.cancel_order(active_order_open.vt_orderid)
                    elif self.is_same_as_order(active_order_open, Direction.SHORT, open_pos, price):
                        # 检查现存订单是否与当前订单一致：
                        # 如果一致，则不再重新下单
                        # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                        # 与当前订单一致
                        # self.write_log("多翻空 开仓操作目标订单与当前订单一致")
                        pass
                    else:
                        # 与当前订单不一致
                        self.write_log(f"多翻空 开仓操作目标订单与当前订单不一致， 取消原订单[{active_order_open.vt_orderid}]")
                        # self.last_send_order_dt = datetime.now()
                        # active_order_open.create_cancel_request()
                        self.cancel_order(active_order_open.vt_orderid)
                elif is_close_available:
                    if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                        self.write_log(f"多翻空 {current_pos} -> {target_pos} 再开仓")
                        self.short(price, open_pos)
                else:
                    self.write_log(f"多翻空 平仓单未生效前，开仓单暂不下单")

        elif target_pos < current_pos <= 0:
            # 开空
            volume = abs(target_pos - current_pos)
            if active_order_close:
                # 如果存在平仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_close.create_cancel_request()
                self.write_log(f"开空 取消已存在的平仓单[{active_order_close.vt_orderid}]")
                self.cancel_order(active_order_close.vt_orderid)

            elif active_order_open:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_open, Direction.SHORT, volume, price):
                    # 与当前订单一致
                    # self.write_log("开空 目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"开空 目标订单与当前订单不一致， 取消原订单[{active_order_open.vt_orderid}]")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_open.create_cancel_request() 无效
                    self.cancel_order(active_order_open.vt_orderid)
            else:
                if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                    self.write_log(f"开空 {current_pos} -> {target_pos}")
                    self.short(price, volume)

        elif current_pos < target_pos <= 0:
            # 平空
            if active_order_open:
                # 如果存在开仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_open.create_cancel_request()
                self.write_log(f"平空 取消已存在的开仓单[{active_order_open.vt_orderid}]")
                self.cancel_order(active_order_open.vt_orderid)

            elif active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.LONG, volume, price):
                    # 与当前订单一致
                    # self.write_log("平空 目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"平空 目标订单与当前订单不一致， 取消原订单[{active_order_close.vt_orderid}]")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
            else:
                self.write_log(f"平空 {current_pos} -> {target_pos}")
                volume = abs(target_pos - current_pos)
                self.cover(price, volume)

        elif current_pos < 0 < target_pos:
            # 空翻多
            # 先检查平仓单是否已经下出去了
            # 如果平仓单已经下出去了，再下开仓单
            is_close_available = True
            close_pos = abs(current_pos)
            if active_order_close:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_close, Direction.LONG, close_pos, price):
                    # 与当前订单一致
                    # self.write_log("空翻多 平仓操作目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"空翻多 平仓操作目标订单与当前订单不一致， 取消原订单[{active_order_close.vt_orderid}]")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_close.create_cancel_request() 无效
                    self.cancel_order(active_order_close.vt_orderid)
                    is_close_available = False
            else:
                self.write_log(f"空翻多 {current_pos} -> {target_pos} 先平仓")
                self.cover(price, close_pos)
                is_close_available = False

            if active_order_close:
                open_pos = abs(target_pos)
                if active_order_open:
                    if not is_close_available:
                        self.write_log(f"空翻多 平仓单未生效前，现存开仓单需要取消[{active_order_open.vt_orderid}]")
                        self.cancel_order(active_order_open.vt_orderid)
                    elif self.is_same_as_order(active_order_open, Direction.LONG, open_pos, price):
                        # 检查现存订单是否与当前订单一致：
                        # 如果一致，则不再重新下单
                        # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                        # 与当前订单一致
                        # self.write_log("空翻多 开仓操作目标订单与当前订单一致")
                        pass
                    else:
                        # 与当前订单不一致
                        self.write_log(f"空翻多 开仓操作目标订单与当前订单不一致， 取消原订单[{active_order_open.vt_orderid}]")
                        # self.last_send_order_dt = datetime.now()
                        # active_order_open.create_cancel_request() 无效
                        self.cancel_order(active_order_open.vt_orderid)
                elif is_close_available:
                    if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                        self.write_log(f"空翻多 {current_pos} -> {target_pos} 再开仓")
                        self.buy(price, open_pos)
                else:
                    self.write_log(f"空翻多 平仓单未生效前，开仓单暂不下单")

        elif 0 <= current_pos < target_pos:
            # 开多
            if active_order_close:
                # 如果存在平仓操作，直接取消
                # self.last_send_order_dt = datetime.now()
                # active_order_close.create_cancel_request() 无效
                self.write_log(f"开多 取消已存在的平仓单[{active_order_close.vt_orderid}]")
                self.cancel_order(active_order_close.vt_orderid)

            elif active_order_open:
                # 检查现存订单是否与当前订单一致：
                # 如果一致，则不再重新下单
                # 如果不一致，取消原有订单，且原订单取消确认后（无有效订单），才可以下新订单
                if self.is_same_as_order(active_order_open, Direction.LONG, volume, price):
                    # 与当前订单一致
                    # self.write_log("开多 目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"开多 目标订单与当前订单不一致，取消原订单。[{active_order_open.vt_orderid}]"
                                   f"\n原订单 {active_order_open.volume} {active_order_open.price}。"
                                   f"\n新订单 {volume} {price}")
                    # self.last_send_order_dt = datetime.now()
                    # active_order_open.create_cancel_request() 无效
                    self.cancel_order(active_order_open.vt_orderid)
            else:
                if self.stop_opening_pos != StopOpeningPos.stop_opening_and_nolog.value:
                    self.write_log(f"开多 {current_pos} -> {target_pos} {price}")
                    volume = abs(target_pos - current_pos)
                    self.buy(price, volume)

    def send_order_2_target_pos_close_rejected(self, active_order_close, active_order_open):
        """用于 close_rejected 的状态下发送开仓单平衡目标仓位"""
        if active_order_close:
            self.write_log(f"取消订单：{active_order_close.vt_orderid}，"
                           f"close_rejected={self.close_rejected} 状态下，不应该有活跃的平仓单存在", 'error')
            self.cancel_order(active_order_close.vt_orderid)
            return

        price = self.target_price
        current_pos = self.pos
        target_pos = self.target_pos
        volume = abs(target_pos - current_pos)
        if target_pos < current_pos:
            # 平多被拒绝，直接开空
            if active_order_open:
                if self.is_same_as_order(active_order_open, Direction.SHORT, volume, price):
                    # 与当前订单一致
                    # self.write_log("开空 目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"平多被拒绝，直接开空 当前平仓操作目标订单与当前订单不一致， 取消原订单[{active_order_close.vt_orderid}]")
                    self.cancel_order(active_order_open.vt_orderid)
            else:
                self.write_log(f"平多被拒绝，直接开空 {current_pos} -> {target_pos}")
                self.short(price, volume)

        elif current_pos < target_pos:
            # 平空被拒绝，直接开多
            if active_order_open:
                if self.is_same_as_order(active_order_open, Direction.LONG, volume, price):
                    # 与当前订单一致
                    # self.write_log("开多 目标订单与当前订单一致")
                    pass
                else:
                    # 与当前订单不一致
                    self.write_log(f"平空被拒绝，直接开多 当前平仓操作目标订单与当前订单不一致， 取消原订单[{active_order_close.vt_orderid}]")
                    self.cancel_order(active_order_open.vt_orderid)
            else:
                self.write_log(f"平空被拒绝，直接开多 {current_pos} -> {target_pos}")
                self.buy(price, volume)

    def on_tick(self, tick: TickData) -> bool:
        ret = super().on_tick(tick)
        # 仅实盘环境下进行检查，其实回测环境下通常都是 Minute bar 数据因此不会触发 on_tick 函数
        if self._is_realtime_mode:
            self.update_stop_price_curr()
            self.update_fire_stop_order(tick.last_price)

        return ret

    def on_bar(self, bar: BarData):
        super().on_bar(bar)
        # 仅回测环境下检查，实盘环境下通过 on_tick 触发检查
        if not self._is_realtime_mode:
            # on_bar 的父类已经有 update_stop_price_curr 的动作，因此无需重复计算
            self.update_fire_stop_order(bar.close_price)
            # if self.fire_stop_order:
            #     self.set_target_pos(0)

    def update_fire_stop_order(self, price):
        """比较 stop_price_curr 与 price 决定是否修改 fire_stop_order 状态"""
        if self.pos > 0 and self.stop_price_curr != 0 and price < self.stop_price_curr:
            self.fire_stop_order = True
            self.fire_stop_order_dt = datetime.now()
        elif self.pos < 0 and self.stop_price_curr != 0 and price > self.stop_price_curr:
            self.fire_stop_order = True
            self.fire_stop_order_dt = datetime.now()

    # 2021-06-28 MG
    # 剔除相关 cancel_all 逻辑
    # on_trade 中增加 cancel_all() 将导致 回测过程中引发如下异常：
    # ...
    # File "D:\IDE\vnstudio\lib\site-packages\vnpy_extra\backtest\cta_strategy\engine.py",
    # line 187, in cross_limit_order
    #     self.active_limit_orders.pop(order.vt_orderid)
    # KeyError: 'BACKTESTING.1039'
    # ...
    # def on_trade(self, trade: TradeData):
    #     super().on_trade(trade)
    #     if self.pos == 0 and self.fire_stop_order:
    #         # 停止单已触犯情况下仅撤销停止单而没有撤销实际平仓单将导致出错
    #         # self.cancel_all_stop_orders()
    #         self.cancel_all()

    def on_order(self, order: OrderData):
        super().on_order(order)
        if order.status == Status.REJECTED and order.offset in (Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY):
            # 平仓被拒绝，可能由于当期账户已经没有持仓，这种情况可能是由于此前算法或策略过度平仓导致的。
            # 出现这种问题情况通常是多空反转的情况下。当期账户实际已经没有对应方向持仓，因此可以直接反向开仓解决。
            self.close_rejected = True


class TargetPosTemplate(TargetPosTemplateBase, CtaTemplate):
    """
        CtaTemplateBase(vnpy原始的 CtaTemplate)
               ↖
        TargetPosTemplateBase               CtaTemplateMixin
                            ↖               ↗
                            TargetPosTemplate
    """

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)


def calc_bar_count_per(symbol, size, interval: Interval, days):
    """根据 PERIOD_DIC SYMBOL_MINUTES_COUNT_DIC 字典计算指定 days 需要多少个 bars"""
    instrument_type = get_instrument_type(symbol)
    if interval == Interval.MINUTE:
        bar_count = int(np.ceil(SYMBOL_MINUTES_COUNT_DIC[instrument_type] / size * days))
    elif interval == Interval.HOUR:
        bar_count = int(np.ceil(SYMBOL_MINUTES_COUNT_DIC[instrument_type] / size / 60 * days))
    elif interval == Interval.DAILY:
        bar_count = int(np.ceil(days / size))
    elif interval == Interval.WEEKLY:
        bar_count = int(np.ceil(days / size / 7))
    else:
        raise ValueError("interval %s 无效", interval)

    return bar_count


def get_interval_str(size, interval: Interval):
    """根据size, interval 返回相应的字符串"""
    return f"{size:02d}{interval.value[-1] if isinstance(interval, Interval) else str(interval)[-1]}"


def get_interval_str_by_period(period_enum):
    """更加 GeneralPeriodEnum 返回对应的时间周期字符串"""
    return get_interval_str(*GeneralPeriodEnum[period_enum].value)


def make_param_2_str(param):
    """将param转化为str，用于合成id_name"""
    if isinstance(param, bool):
        return str(param)
    if isinstance(param, int):
        return f"{param:02d}"
    if isinstance(param, float):
        return f'{param:.1f}'
    if str(param).isdigit():
        return f"{int(param):02d}"
    if isinstance(param, Enum):
        return str(param.value)
    else:
        return str(param)


def get_name_by_param(*, period_enum=None, period=None, interval=None, signal_type='', class_name='',
                      filter_available=0, reverse_bs=0, enable=True, **kwargs):
    """通过信号参数生成 id_name 的信号部分"""
    # 外层函数使用 signal_name 显示名称,因此此处无需处理, signal_type 变量
    if not enable:
        return ""
    names = [
        signal_type if signal_type else class_name,
        f'{get_interval_str_by_period(period_enum)}' if period_enum else get_interval_str(period, interval),
    ]
    params = [make_param_2_str(_) for key, _ in kwargs.items() if key not in ('module_name',)]
    tail_params = [
        f"f{filter_available}" if filter_available > 1 else "",  # filter for signal m
        "r" if reverse_bs else "",  # reverse bs
    ]
    return '_'.join([_ for _ in chain(names, params, tail_params) if _])


class Signal2PositionMethodEnum(Enum):
    or_ = 'or'  # 所有信号只有出现相反的时候才会为 0
    and_ = 'and'  # 所有信号只要有不一样的即为 0
    sum_ = 'sum'  # 所有信号算数相加


class MultiSignalsTemplate(TargetPosAndPriceNoStopOrderTemplate):
    signal_module_name = 'vnpy_extra.utils.cta_signal'
    signal_name_list = []
    exit_signal_name_list = []
    fire_close_signal = False
    # 'and', 'or', 'sum'
    position_method = Signal2PositionMethodEnum.and_.value
    # 多空反转逐步完成：1 逐步完成；0 一步切换完成；
    step_by_step = 1
    # set_target_pos 过滤器，交易信号N次改动才真正修改。防止信号抖动。
    filter_set_target_pos = 1

    signal_pos = {}

    parameters = [
        # 信号 M 参数
        # ....
        # 策略参数
        # 基础仓位、仓位合成策略[and\or\sum]
        BASE_POSITION, "position_method",
        # 多空仓位切换、目标仓位过滤器
        "step_by_step", "filter_set_target_pos",
        # 追踪止损、成本线止损
        "trailing_stop_rate", "stop_loss_rate",
    ]
    variables = ["signal_pos", "target_pos", "bar_count", "fire_close_signal"]
    load_main_continuous_md = True
    signal_must_have_params = ['signal_type']
    init_load_days = 30

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        # 内部变量，用于记录信号名称与信号类对应关系
        self._signal_name_instance_dic: Dict[str, CtaSignal] = {}
        # 内部变量，用于记录信号名称与信号参数对应关系
        self._signal_name_kwargs_dic = {}
        for signal_name in self.signal_name_list:
            is_enable = getattr(self, f'{signal_name}_enabled', True)
            if not is_enable:
                continue
            # 获取所有以 signal_name 开头的信号的变量 f"{signal_name}_***"
            self._signal_name_kwargs_dic[signal_name] = params_kwargs = self.get_signal_params(signal_name)
            # Clone params_kwargs 防止造成联动修改
            params_kwargs = params_kwargs.copy()
            # 参数有效性检查
            # for _ in self.signal_must_have_params:
            #     if _ not in params_kwargs:
            #         raise ValueError(f"信号 {signal_name} 至少需要设置 '{signal_name}_{_}' 变量")
            if 'period_enum' in params_kwargs:
                period_enum: GeneralPeriodEnum = params_kwargs.pop('period_enum')
                if isinstance(period_enum, str):
                    period_enum = GeneralPeriodEnum[period_enum]

                params_kwargs.setdefault('period', period_enum.value[0])
                params_kwargs.setdefault('interval', period_enum.value[1])
            # strict 默认为 True
            params_kwargs.setdefault('strict', True)
            params_kwargs.setdefault('module_name', self.signal_module_name)
            if 'signal_type' in params_kwargs:
                signal_type = params_kwargs.pop('signal_type')
                params_kwargs.setdefault(f'class_name', f"{signal_type}Signal")
            # 动态创建 signal_name 信号
            signal: CtaSignal = create_instance(
                **params_kwargs,
                vt_symbol=self.vt_symbol,
                strategy_obj=self,
            )
            self._signal_name_instance_dic[signal_name] = signal
            daily_bar_count = signal.daily_bars_needed_at_least()
            if self.init_load_days < daily_bar_count:
                self.init_load_days = daily_bar_count

        self._exit_signal_name_instance_dic: Dict[str, CtaExitSignal] = {}
        for signal_name in self.exit_signal_name_list:
            is_enable = getattr(self, f'{signal_name}_enabled', True)
            if not is_enable:
                continue
            # 获取所有以 signal_name 开头的信号的变量 f"{signal_name}_***"
            self._signal_name_kwargs_dic[signal_name] = params_kwargs = self.get_signal_params(
                signal_name, check_signal_name_list=self.exit_signal_name_list)
            # Clone params_kwargs 防止造成联动修改
            params_kwargs = params_kwargs.copy()
            # 参数有效性检查
            # for _ in self.signal_must_have_params:
            #     if _ not in params_kwargs:
            #         raise ValueError(f"信号 {signal_name} 至少需要设置 '{signal_name}_{_}' 变量")
            if 'period_enum' in params_kwargs:
                period_enum: GeneralPeriodEnum = params_kwargs.pop('period_enum')
                if isinstance(period_enum, str):
                    period_enum = GeneralPeriodEnum[period_enum]

                params_kwargs.setdefault('period', period_enum.value[0])
                params_kwargs.setdefault('interval', period_enum.value[1])

            # strict 默认为 True
            params_kwargs.setdefault('strict', True)
            params_kwargs.setdefault('module_name', self.signal_module_name)
            if 'signal_type' in params_kwargs:
                signal_type = params_kwargs.pop('signal_type')
                params_kwargs.setdefault(f'class_name', f"{signal_type}ExitSignal")
            # 动态创建 signal_name 信号
            signal: CtaExitSignal = create_instance(
                **params_kwargs,
                vt_symbol=self.vt_symbol,
                strategy_obj=self,
            )
            if not isinstance(signal, CtaExitSignal):
                raise ValueError(f"{signal_name} 必须是 CtaCloseSignal 类型")

            self._exit_signal_name_instance_dic[signal_name] = signal
            daily_bar_count = signal.daily_bars_needed_at_least()
            if self.init_load_days < daily_bar_count:
                self.init_load_days = daily_bar_count

            # 设置初始状态
            self.signal_pos[signal_name] = 0

        if "fire_close_signal" not in self.variables and len(self._exit_signal_name_instance_dic) > 0:
            self.variables.append("fire_close_signal")

        # 设置初始状态
        self.signal_pos = {_: 0 for _ in self.signal_name_list}
        self.signal_2_position_method = Signal2PositionMethodEnum(self.position_method)
        # 低层信号级别以及留有余量,此处无需进一步扩大加载天数
        self.init_load_days = max([self.init_load_days, 30])
        # target_pos 的临时变量
        self._target_pos_tmp = self.target_pos
        self._target_pos_count = 0

    def get_signal_params(self, signal_name: str, check_signal_name_list: list = None):
        """
        signal_name 应该是 'm' 或 'n'
        从 parameters 将指定的信号值整理成实际 Signal 需要的参数
        """
        signal_name_list = (self.signal_name_list
                            if check_signal_name_list is None else check_signal_name_list)
        if signal_name not in signal_name_list:
            raise ValueError(f"{signal_name} 不在 {signal_name_list} 列表中")

        params_kwargs = {}
        signal_param_header = f'{signal_name}_'

        for param_name in dir(self):
            if not param_name.startswith(signal_param_header):
                continue
            signal_param_name = param_name[len(signal_param_header):]
            if not hasattr(self, param_name):
                continue
            value = getattr(self, param_name)
            if value is None or str(value).lower() == 'none':
                continue
            if param_name == f'{signal_param_header}period_enum':
                params_kwargs[signal_param_name] = GeneralPeriodEnum[value]
            elif param_name == f'{signal_param_header}period':
                if isinstance(value, str):
                    msg = f"该参数用法已经废弃，建议使用 '{signal_param_header}period_enum' 的参数名称"
                    warnings.warn(msg, PendingDeprecationWarning)
                    self.logger.warning(msg)
                    params_kwargs[signal_param_name] = GeneralPeriodEnum[value]
                else:
                    params_kwargs[signal_param_name] = value
            elif isinstance(value, str):
                if value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

            params_kwargs[signal_param_name] = value

        return params_kwargs

    def on_tick(self, tick: TickData) -> bool:
        """on_tick"""
        ret = super().on_tick(tick)
        if ret:
            for signal_name, instance in self._exit_signal_name_instance_dic.items():
                if not instance.enable_on_tick_signal:
                    continue
                instance.on_tick(tick)
                self.signal_pos[signal_name] = _target_pos = instance.get_signal_pos()
                stop_order_price = instance.stop_order_price
                if (
                        self.pos > 0 and (_target_pos == 0 or 0 < tick.ask_price_1 < stop_order_price)
                ) or (
                        self.pos < 0 and (_target_pos == 0 or tick.bid_price_1 > stop_order_price > 0)
                ):
                    # 触发平仓信号
                    self.fire_close_signal = True

        return ret

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        super().on_bar(bar)
        # if self.m_enable_period:
        #     self.signal_m.on_bar(bar)
        # 更新cta信号
        for signal_name, instance in self._signal_name_instance_dic.items():
            instance.on_bar(bar)

        # 更新出场信号
        for signal_name, instance in self._exit_signal_name_instance_dic.items():
            if not instance.enable_on_bar_signal:
                continue
            instance.on_bar(bar)
            self.signal_pos[signal_name] = _target_pos = instance.get_signal_pos()
            stop_order_price = instance.stop_order_price
            if (
                    self.pos > 0 and (_target_pos == 0 or 0 < bar.low_price < stop_order_price)
            ) or (
                    self.pos < 0 and (_target_pos == 0 or bar.high_price > stop_order_price > 0)
            ):
                # 触发平仓信号
                self.fire_close_signal = True

        self.calculate_target_pos()
        self.put_event()

    def calculate_target_pos(self):
        """"""
        if not self.inited:
            return

        # 在有效日期范围内
        target_pos, is_first = 0, True
        for signal_name, instance in self._signal_name_instance_dic.items():
            self.signal_pos[signal_name] = _target_pos = instance.get_signal_pos()
            if is_first:
                target_pos = _target_pos
                is_first = False
            elif self.signal_2_position_method == Signal2PositionMethodEnum.and_:
                # 所有信号只要有不一样的即为 0
                if target_pos != _target_pos:
                    target_pos = 0

            elif self.signal_2_position_method == Signal2PositionMethodEnum.or_:
                # 所有信号只有出现相反的时候才会为 0
                if (target_pos == 1 and _target_pos == -1) or (target_pos == -1 and _target_pos == 1):
                    target_pos = 0

            elif self.signal_2_position_method == Signal2PositionMethodEnum.sum_:
                # 所有信号算数想加
                target_pos += _target_pos

        if self.step_by_step and (self.pos < 0 < target_pos or self.pos > 0 > target_pos):
            target_pos = 0

        self.set_target_pos(target_pos * self.base_position)

    def update_stop_price_curr(self):
        """更新追踪平仓价格"""
        is_updated = super().update_stop_price_curr()
        # 更新追踪平仓价格
        for signal_name, instance in self._exit_signal_name_instance_dic.items():
            if instance.stop_order_price:
                if self.pos == 0:
                    # 清仓情况下，重置状态
                    instance.reset_status()
                if self.pos > 0 and self.stop_price_curr < instance.stop_order_price:
                    # 多单情况下，以非零的最高价为准
                    self.stop_price_curr = instance.stop_order_price
                    is_updated = True
                elif self.pos < 0 and (
                        (self.stop_price_curr == 0 and instance.stop_order_price > 0)
                        or (self.stop_price_curr > instance.stop_order_price > 0)
                ):
                    # 空单情况以非零的最低价为准
                    self.stop_price_curr = instance.stop_order_price
                    is_updated = True

        return is_updated

    @property
    def target_pos(self):
        if self.fire_stop_order or self.fire_close_signal:
            return 0
        else:
            return self._target_pos

    @target_pos.setter
    def target_pos(self, value):
        self._target_pos = value

    def set_target_pos(self, target_pos, price=None):
        """
        设置目标持仓以及价格。
        特别注意：
            对于强制平仓信号 CtaExitSignal 以及追踪平仓，成本线止损等强制平仓机制，
            请务必通过 设置 fire_close_signal、fire_stop_order 的方式设置平仓。
            而不要通过当前方法 target_pos=0 的方式设置止损。
        """
        # filter_set_target_pos 用于对交易信号进行滤波,防止信号都懂,并进行信号延迟变化
        if self._target_pos_tmp == target_pos:
            self._target_pos_count += 1
        else:
            self._target_pos_tmp = target_pos
            self._target_pos_count = 1

        if self._target_pos_count >= self.filter_set_target_pos:
            if self._target_pos < 0 <= target_pos or self._target_pos > 0 >= target_pos:
                if self.fire_close_signal:
                    self.fire_close_signal = False

            super().set_target_pos(target_pos, price)

    def get_class_short_name(self) -> str:
        """生成类名的简称（尚未启用）"""
        if len(self.signal_name_list) == 1:
            class_short_name = f"{self.signal_name_list[0].capitalize()}Only"
        else:
            names = [_.capitalize() for _ in self.signal_name_list]
            names.append(self.position_method.capitalize())
            class_short_name = '_'.join(names)
        return class_short_name

    def get_id_name(self) -> str:
        """返回 id_name """
        # signal_name_id_name_dic = {
        #     signal_name: get_name_by_param(**params_kwargs)
        #     for signal_name, params_kwargs in self._signal_name_kwargs_dic.items()}
        signal_name_id_name_dic = {}
        for signal_name, signal_obj in self._signal_name_instance_dic.items():
            if hasattr(signal_obj, 'get_id_name'):
                signal_id_name = signal_obj.get_id_name()
            else:
                signal_id_name = get_name_by_param(**self._signal_name_kwargs_dic[signal_name])

            signal_name_id_name_dic[signal_name] = signal_id_name

        if len(signal_name_id_name_dic) == 1:
            params_str = list(signal_name_id_name_dic.values())[0]
        else:
            params_str = '_'.join([str(v) for v in signal_name_id_name_dic.values()])

        tail_params = [
            "ls" if self.step_by_step == 1 else "",  # long short step by step
            "d" + str(self.filter_set_target_pos) if self.filter_set_target_pos > 1 else "",  # delay n bar
            f"ts{self.trailing_stop_rate * 1000:.0f}" if self.trailing_stop_rate != 0 else "",
            f"ss{self.stop_loss_rate * 1000:.0f}" if self.stop_loss_rate != 0 else "",
            self.allow_trade_direction_enum.value if self.allow_trade_direction_enum != AllowTradeDirectionEnum.ALL
            else '',
        ]
        tail_params_str = "_".join([_ for _ in tail_params if _ != ""])
        stg_name = self.__class__.__name__
        if stg_name.endswith('Strategy'):
            stg_name = stg_name[:-len('Strategy')]
        if len(tail_params_str) > 0:
            name = f"{stg_name}_{params_str}_{tail_params_str}"
        else:
            name = f"{stg_name}_{params_str}"

        return name

    def get_name_by_pattern(self, name_pattern):
        """根据 name_pattern 返回对应的名称，主要用于自动化生成 short_name, shown_name"""
        name_part_list = []
        for signal_name, params_kwargs in self._signal_name_kwargs_dic.items():
            name_part = f"{params_kwargs['signal_type']}{params_kwargs['period']}" \
                        f"{'r' if 'reverse_bs' in params_kwargs else ''}"
            name_part_list.append(name_part)

        s_part = self.vt_symbol.split('.')[0]
        signal_part = '_'.join(name_part_list)
        stg_part = self.__class__.__name__
        if stg_part.endswith('Strategy'):
            stg_part = stg_part[:-len('Strategy')]

        name = re.sub(r'\[F]', f"{stg_part}_{s_part}_{signal_part}", name_pattern)
        name = re.sub(r'\[N]', stg_part, name)
        name = re.sub(r'\[S]', s_part, name)
        name = re.sub(r'\[G]', signal_part, name)
        return name

    @classmethod
    def create_cls_by_signals(cls, **kwargs: Type[CtaSignal]) -> Type[TargetPosAndPriceTemplate]:
        """
        根据信号，动态创建多信号共振类
        """
        import inspect
        # print("kwargs", kwargs)
        signal_name_list = []
        parameters = [
            # 策略参数
            # 基础仓位、仓位合成策略[and\or\sum]
            BASE_POSITION, "position_method",
            # 多空仓位切换、目标仓位过滤器
            "step_by_step", "filter_set_target_pos",
            # 追踪止损、成本线止损
            "trailing_stop_rate", "stop_loss_rate",
        ]
        init_attr_dic = {
            "__module__": cls.__module__,
            "signal_name_list": signal_name_list,  # signal_name_list 将会随着下面的 for 循环动态增长
            "position_method": cls.position_method,
            "parameters": parameters,  # parameters 将会随着下面的 for 循环动态增长
        }
        signal_cls_list = []
        for signal_name, signal_cls in kwargs.items():
            signal_name_list.append(signal_name)
            signal_cls_list.append(signal_cls)
            # 设置信号类型
            cls_name_header = signal_cls.get_signal_name_header()
            init_attr_dic[f'{signal_name}_signal_type'] = cls_name_header
            # 设置默认周期，默认所有周期都是 m1 1分钟周期
            attr_name = f'{signal_name}_period'
            parameters.append(attr_name)
            init_attr_dic[attr_name] = 'm1'
            # 其他初始化参数及默认值设置如下
            for param_name, param in inspect.signature(signal_cls).parameters.items():
                if param_name in ('period', 'interval', 'args', 'kwargs'):
                    # 'period', 'interval' 将会在类创建过程中被 period: GeneralPeriodEnum 参数进行动态设置
                    continue
                attr_name = f'{signal_name}_{param_name}'
                parameters.append(attr_name)
                # 参数赋值，没有默认值的，设置默认值为 0
                if param.default == param.empty:
                    init_attr_dic[attr_name] = 0
                else:
                    init_attr_dic[attr_name] = param.default

        cls_name = cls.get_cls_name_by_signals(signal_cls_list)
        cls_new: Type[MultiSignalsTemplate] = type(cls_name, (cls,), init_attr_dic)
        return cls_new

    @classmethod
    def get_cls_name_by_signals(cls, signal_cls_list: List[Type[CtaSignal]]):
        return f"{''.join([_.get_short_name().capitalize() for _ in signal_cls_list])}" \
               f"MS{cls.position_method.capitalize()}"

    def is_available(self, stats: dict, df: pd.DataFrame) -> bool:
        balance_s = df["balance"]
        is_available = not (
                stats['total_days'] <= 250  # 部分情况下,加载日数据过多,导致可回测天数小于1年
                or stats['total_net_pnl'] <= 0
                or stats['daily_trade_count'] < 0.2  # 1/0.2 每一次交易平仓再开仓需要2次交易，因此相当于10天交易一次
                or stats['return_drawdown_ratio'] < 1.5
                or stats['max_new_higher_duration'] >= 180  # 最长不创新高周期<180
                or stats['max_new_higher_duration'] / stats['total_days'] > 0.5  # 最长不创新高周期超过一半的总回测天数
                or balance_s is None  # 没有交易
                or np.sum((balance_s - stats['capital']) <= 0) / stats['total_days'] > 0.5  # 50%以上交易日处于亏损状态
                or np.all(df["drawdown"][df["drawdown"].idxmin():] < 0)  # 最大回撤到最后一个交易日需要出现新高
        )
        return is_available

    def get_id_name(self) -> str:
        """返回 id_name """
        # signal_name_id_name_dic = {
        #     signal_name: get_name_by_param(**params_kwargs)
        #     for signal_name, params_kwargs in self._signal_name_kwargs_dic.items()}
        signal_name_id_name_dic = {}
        for signal_name, signal_obj in chain(
                self._signal_name_instance_dic.items(),
                self._exit_signal_name_instance_dic.items()
        ):
            if not self._signal_name_kwargs_dic[signal_name].get('enable', True):
                continue
            if hasattr(signal_obj, 'get_id_name'):
                signal_id_name = signal_obj.get_id_name()
            else:
                signal_id_name = get_name_by_param(**self._signal_name_kwargs_dic[signal_name])

            signal_name_id_name_dic[signal_name] = signal_id_name

        # if len(signal_name_id_name_dic) == 1:
        #     params_str = list(signal_name_id_name_dic.values())[0]
        # else:
        params_str = '_'.join([str(v) for v in signal_name_id_name_dic.values()])

        tail_params = [
            "ls" if self.step_by_step == 1 else "",  # long short step by step
            "d" + str(self.filter_set_target_pos) if self.filter_set_target_pos > 1 else "",  # delay n bar
            f"ts{self.trailing_stop_rate * 1000:.0f}" if self.trailing_stop_rate != 0 else "",
            f"ss{self.stop_loss_rate * 1000:.0f}" if self.stop_loss_rate != 0 else "",
        ]
        tail_params_str = "_".join([_ for _ in tail_params if _ != ""])
        stg_name = self.__class__.__name__
        if stg_name.endswith('Strategy'):
            stg_name = stg_name[:-len('Strategy')]
        if len(tail_params_str) > 0:
            name = f"{stg_name}_{params_str}_{tail_params_str}"
        else:
            name = f"{stg_name}_{params_str}"

        return name


class MultiSignalsAndTemplate(MultiSignalsTemplate):
    position_method = Signal2PositionMethodEnum.and_.value


class MultiSignalsOrTemplate(MultiSignalsTemplate):
    position_method = Signal2PositionMethodEnum.or_.value


class MultiSignalsSumTemplate(MultiSignalsTemplate):
    position_method = Signal2PositionMethodEnum.sum_.value


if __name__ == "__main__":
    pass
