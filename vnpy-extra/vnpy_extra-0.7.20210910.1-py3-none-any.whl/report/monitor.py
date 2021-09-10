"""
@author  : MG
@Time    : 2020/12/11 8:00
@File    : monitor.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import calendar
import logging
import os
from datetime import time, date, datetime, timedelta
from threading import Thread, Lock
from time import sleep
from typing import Callable, Optional, Dict, Tuple, List

import pandas as pd
from ibats_utils.mess import date_2_str, str_2_datetime, datetime_2_str, str_2_date
from peewee import DatabaseError
from vnpy.trader.constant import Direction, Offset
from vnpy.trader.object import TickData

from vnpy_extra.constants import SYMBOL_SIZE_DIC
from vnpy_extra.db.orm import TradeDataModel, PositionStatusModel, StrategyStatus, \
    AccountStrategyStatusEnum, LatestTickPriceModel, PositionDailyModel, TradeDateModel, get_account, \
    AccountStrategyMapping, set_account
from vnpy_extra.utils.symbol import get_instrument_type


class StrategyPositionMonitor(Thread):
    logger = logging.getLogger("StrategyPositionMonitor")

    def __init__(self):
        super().__init__(daemon=True)
        self.is_running = True
        self.strategy_get_pos_func_dic: Dict[str, Callable[[], Dict[str, Tuple[int, TickData]]]] = {}
        # 预留2分钟避免应为延时或者时间不准导致的计算错误
        # 时间范围列表需要保持递增的时间顺序
        self.time_period_list = [
            ['09:02:30', '11:32:30'],
            ['13:32:30', '15:02:30'],
            ['21:02:30', '23:02:30']
        ]
        self.time_period_list = [[time.fromisoformat(_[0]), time.fromisoformat(_[1])]
                                 for _ in self.time_period_list]
        self._last_dt = None
        self.lock = Lock()

    def register_get_pos(self, strategy_name: str,
                         get_pos_and_price: Callable[[], Dict[str, Tuple[int, TickData]]]) -> None:
        """
        注册 get_position 方法
        """
        self.strategy_get_pos_func_dic[strategy_name] = get_pos_and_price

    def get_sleep_seconds(self, minutes=5) -> (datetime, float):
        now_dt = datetime.now()
        now_time = now_dt.time()
        today_str = date_2_str(date.today())
        for time_from, time_to in self.time_period_list:
            # 如果当前时间小于起始时间，则直接sleep，直到起始时间
            if now_time < time_from:
                target_dt = str_2_datetime(today_str + time_from.strftime(" %H:%M:%S"))
                delta = target_dt - now_dt
                seconds = delta.total_seconds()
                self._last_dt = target_dt
                break

            if self._last_dt is None:
                # 如果首次执行
                if time_from < now_time < time_to:
                    # 在时间区间内
                    target_dt = now_dt
                    seconds = 0.0
                    self._last_dt = now_dt
                    break
            elif time_from < self._last_dt.time() < time_to:
                # 如果此前执行过，且上一次执行时间在此区间内
                target_dt: datetime = max(
                    min(str_2_datetime(today_str + time_to.strftime(" %H:%M:%S")),
                        self._last_dt + timedelta(minutes=minutes)),
                    now_dt)
                delta = target_dt - now_dt
                seconds = delta.total_seconds()
                self._last_dt = target_dt
                break
        else:
            # 次日第一时间执行
            target_dt = str_2_datetime(
                date_2_str(date.today() + timedelta(days=1)) +
                self.time_period_list[0][0].strftime(" %H:%M:%S")
            )
            delta = target_dt - now_dt
            seconds = delta.total_seconds()
            self._last_dt = target_dt

        self.logger.debug("Next scan datetime is %s", datetime_2_str(target_dt))
        return target_dt, seconds

    def refresh_positions(self):
        """更新各个策略的持仓盈亏情况"""
        strategy_symbol_pos_status_dic: Dict[str, Dict[str, PositionStatusModel]] = \
            PositionStatusModel.query_latest_position_status(recent_n_days=0)
        strategy_status_list: List[StrategyStatus] = StrategyStatus.query_all()
        for strategy_status in strategy_status_list:
            strategy_name = strategy_status.strategy_name
            if strategy_name in strategy_symbol_pos_status_dic:
                self.refresh_positions_of_strategy(strategy_name, strategy_symbol_pos_status_dic[strategy_name])
            else:
                self.refresh_positions_of_strategy(strategy_name, None)

    def refresh_positions_of_strategy(
            self, strategy_name: str, symbol_pos_status_dic: Optional[Dict[str, PositionStatusModel]]):
        """按策略计算相关合约的持仓、收益计算"""
        next_trade_date_dic, last_trade_date_dic = TradeDateModel.get_trade_date_dic()
        # 获取交易记录
        if symbol_pos_status_dic is None:
            # 如果 symbol_pos_status_dic 空，加载全部策略相关交易记录进行重现计算
            symbol_trade_data_list_dic: Dict[str, List[TradeDataModel]] = \
                TradeDataModel.query_trade_data_by_strategy_since(strategy_name, None)
        else:
            # 获得最新更新时间，获取再次之后的算不交易记录
            symbol_trade_data_list_dic: Dict[str, List[TradeDataModel]] = {}
            for symbol, pos_status in symbol_pos_status_dic.items():
                max_trade_dt = pos_status.trade_dt
                symbol_trade_data_list_dic[symbol] = \
                    TradeDataModel.query_trade_data_by_strategy_symbol_since(strategy_name, symbol, max_trade_dt)

        # 将交易记录按照 symbol 进行分类，并分别计算
        symbol_set = set(symbol_trade_data_list_dic.keys())
        if symbol_pos_status_dic is not None:
            symbol_set |= set(symbol_pos_status_dic.keys())
        for symbol in symbol_set:
            pos_status = symbol_pos_status_dic[symbol] \
                if symbol_pos_status_dic is not None and symbol in symbol_pos_status_dic else None
            trade_data_list = symbol_trade_data_list_dic[symbol] if symbol in symbol_trade_data_list_dic else []
            self.refresh_positions_by_trade_data_list(
                strategy_name, symbol, pos_status, trade_data_list, next_trade_date_dic)

    def refresh_positions_by_trade_data_list(
            self, strategy_name: str, symbol: str,
            pos_status: Optional[PositionStatusModel],
            trade_data_list: List[TradeDataModel],
            next_trade_date_dic: Optional[Dict[date, date]] = None,
            last_trade_date_dic: Optional[Dict[date, date]] = None,
    ):
        """根据交易记录更新相应策略及symbol的持仓状态"""
        if trade_data_list is None or len(trade_data_list) == 0:
            return
        if next_trade_date_dic is None or last_trade_date_dic is None:
            next_trade_date_dic, last_trade_date_dic = TradeDateModel.get_trade_date_dic()

        self.logger.info("开始计算 %s [%s] 逐笔持仓状态信息", strategy_name, symbol)

        # 2021-1-14 交易数据保存时对日期进行了修正，因此以下修正不放不再需要
        # DCE 每天晚上9点以后的交易算作是下一个交易日的交易，例如 2021-01-08日 晚上21:04:05的交易
        # 记录的交易日期为 2021-01-11 21:04:05
        # 因此需要进行修正
        # need_resort = False
        # for trade_data in trade_data_list:
        #     if trade_data.exchange == Exchange.DCE.name and trade_data.datetime.hour >= 21:
        #         # new_dt_str = date_2_str(
        #         #     last_trade_date_dic[trade_data.datetime.date()]) \
        #         #              + datetime_2_str(trade_data.datetime, " %H:%M:%S")
        #         # trade_data.datetime = str_2_datetime(new_dt_str)
        #         _date = trade_data.datetime.date()
        #         _last_date = last_trade_date_dic[_date]
        #         delta = _last_date - _date
        #         trade_data.datetime += delta
        #         need_resort = True
        #
        # if need_resort:
        #     trade_data_list.sort(key=lambda x: x.datetime)

        def create_empty_pos_status_dic():
            return dict(
                tradeid='',
                strategy_name=strategy_name,
                symbol=symbol,
                exchange='',
                volume=0,
                avg_price=0,
                holding_gl=0,
                offset_gl=0,
                offset_daily_gl=0,
                offset_acc_gl=0,
                update_dt=datetime.now(),
            )

        def create_pos_status_dic_by_trade_data(data: TradeDataModel):
            return dict(
                tradeid=data.tradeid,
                strategy_name=strategy_name,
                symbol=symbol,
                exchange=data.exchange,
                trade_date=data.datetime.date(),
                trade_dt=data.datetime,
                direction=data.direction,
                avg_price=data.price,
                latest_price=data.price,
                volume=0,
                holding_gl=0,
                offset_gl=0,
                offset_daily_gl=0,
                offset_acc_gl=0,
                update_dt=datetime.now(),
            )

        instrument_type = get_instrument_type(symbol).upper()
        multiplier = SYMBOL_SIZE_DIC.setdefault(instrument_type, 10)
        if pos_status is not None:
            offset_acc_gl = pos_status.offset_acc_gl
            # 根据最近一个交易记录确定交易日
            trade_date = pos_status.trade_dt.date() if pos_status.trade_dt.hour < 21 else \
                next_trade_date_dic[pos_status.trade_dt.date()]

            pos_status_dict = dict(
                tradeid=pos_status.tradeid,
                strategy_name=strategy_name,
                symbol=symbol,
                exchange=pos_status.exchange,
                trade_date=trade_date,
                trade_dt=pos_status.trade_dt,
                direction=pos_status.direction,
                avg_price=pos_status.avg_price,
                volume=pos_status.volume,
                holding_gl=pos_status.holding_gl,
                offset_gl=pos_status.offset_gl,
                offset_daily_gl=pos_status.offset_daily_gl,
                offset_acc_gl=offset_acc_gl,
                update_dt=pos_status.update_dt,
            )
            trade_dt_last: Optional[datetime] = pos_status.trade_dt
        else:
            offset_acc_gl = 0
            pos_status_dict = create_empty_pos_status_dic()
            trade_dt_last: Optional[datetime] = None

        pos_status_new_list: List[dict] = []
        holding_trade_data_list: List[TradeDataModel] = []  # 相当于一个先入先出队列，用于处理平仓后的价格信息
        curr_closing_trade_data: Optional[TradeDataModel] = None
        curr_closing_trade_data_vol_left = 0  # 按照先入先出原则，“正在被平仓的那一笔开仓交易记录”中剩余的持仓
        offset_daily_gl = 0
        for trade_data in trade_data_list:
            # 检查是否到新的一个交易日，如果是，则 offset_daily_gl 重置为 0
            # TODO: 还需要考虑周五夜盘12点以后的情况，周六凌晨的单子，应该是下周一的交易日。目前交易的品种不存在跨夜。
            #  目前不会出错。但以后需要考虑
            curr_trade_date = next_trade_date_dic[trade_data.datetime.date()] \
                if trade_data.datetime.hour >= 21 else trade_data.datetime.date()

            if trade_dt_last is None:
                offset_daily_gl = 0
                trade_dt_last = trade_data.datetime
            else:
                # 计算上一个条交易记录的 交易日
                trade_date_last = next_trade_date_dic[trade_dt_last.date()] \
                    if trade_dt_last.hour >= 21 else trade_dt_last.date()
                if trade_date_last != curr_trade_date:
                    offset_daily_gl = 0
                    trade_dt_last = trade_data.datetime

            for _ in range(2):
                if trade_data.offset == Offset.OPEN.value:
                    # 开仓，检查方向一致的情况下更数据，方向不一致，warning，同时忽略
                    if pos_status_dict['volume'] != 0 and pos_status_dict['direction'] != trade_data.direction:
                        self.logger.error(
                            "交易记录 %s [%s] %s %s %s %.0f 与当前持仓方向不一致，当前记录持仓状态 %s %.0f 剔除历史不一致数据，以最近成交记录为准",
                            trade_data.strategy_name, trade_data.symbol,
                            trade_data.tradeid, trade_data.direction, trade_data.offset, trade_data.volume,
                            pos_status_dict['direction'], pos_status_dict['volume'],
                        )
                        pos_status_dict = create_empty_pos_status_dic()

                    volume = pos_status_dict['volume']
                    volume_new = trade_data.volume + volume
                    avg_price = pos_status_dict['avg_price']
                    avg_price_new = (trade_data.price * trade_data.volume + avg_price * volume) / volume_new
                    latest_price = trade_data.price

                    holding_gl = volume_new * (latest_price - avg_price_new) * multiplier
                    trade_date = trade_data.datetime.date() if trade_data.datetime.hour < 21 else \
                        next_trade_date_dic[trade_data.datetime.date()]
                    # 更新持仓状态信息
                    pos_status_new_dict = dict(
                        tradeid=trade_data.tradeid,
                        strategy_name=strategy_name,
                        symbol=symbol,
                        exchange=trade_data.exchange,
                        trade_date=trade_date,
                        trade_dt=trade_data.datetime,
                        direction=trade_data.direction,
                        avg_price=avg_price_new,
                        latest_price=latest_price,
                        volume=volume_new,
                        holding_gl=holding_gl,
                        offset_daily_gl=offset_daily_gl,
                        offset_acc_gl=offset_acc_gl,
                        update_dt=datetime.now(),
                    )
                    pos_status_new_list.append(pos_status_new_dict)
                    # 更新最新的持仓状态
                    pos_status_dict = pos_status_new_dict
                    holding_trade_data_list.append(trade_data)
                else:
                    # 平仓，检查持仓是否0，如果是则 warning，同时忽略
                    volume = pos_status_dict["volume"]
                    if volume == 0:
                        self.logger.warning(
                            "交易记录 %s [%s] %s %s %s %.0f 没有对应的持仓数据，将当前交易转为'开仓'交易，继续执行",
                            strategy_name, symbol, trade_data.tradeid, trade_data.direction,
                            trade_data.offset, trade_data.volume)
                        trade_data.offset = Offset.OPEN.value
                        continue
                    elif pos_status_dict['direction'] == trade_data.direction:
                        # 平仓，检查方向与持仓是否相反，如果方向一致，warning，同时忽略
                        self.logger.warning(
                            "交易记录 %s [%s] %s %s %s %.0f 与当前持仓方向一致，将当前交易转为'开仓'交易，继续执行",
                            strategy_name, symbol,
                            trade_data.tradeid, trade_data.direction, trade_data.offset, trade_data.volume
                        )
                        trade_data.offset = Offset.OPEN.value
                        continue
                    elif volume < trade_data.volume:
                        self.logger.warning(
                            "交易记录 %s [%s] %s %s %s %.0f 超过当前持仓 %.0f 手，剔除历史数据，当前持仓状态将被重置",
                            strategy_name, symbol, trade_data.tradeid, trade_data.direction,
                            trade_data.offset, trade_data.volume, pos_status_dict['volume'])
                        # 重置持仓状态信息
                        pos_status_new_dict = create_pos_status_dic_by_trade_data(trade_data)

                    else:
                        if len(holding_trade_data_list) > 0 and \
                                sum([_.volume for _ in holding_trade_data_list]) < trade_data.volume:
                            # 2021-06-30
                            # 当出现隔夜分批建仓的情况时，由于当日建仓部分可能无法满足全部平仓数量，
                            # 可能引发“当前持仓全部订单不足以处理当前平仓。。。” 异常
                            # 因此，清除 holding_trade_data_list 列表，依然使用 close_vol 直接相减的逻辑进行相应计算
                            holding_trade_data_list = []

                        if len(holding_trade_data_list) == 0:
                            # 计算平仓盈亏
                            # 平仓逻辑分为两条线
                            # 1）按照最近一个持仓状态计算仓位及平均价格，当 holding_trade_data_list 为空的情况下(当前分支的逻辑）
                            # 2）按照先入先出队列进行计算仓位及平均价格等
                            close_vol = trade_data.volume
                            curr_closing_trade_data_vol_left = volume - close_vol
                            # trade_data.direction 为“多”，说明持仓是“空”，所以，价差 * -1
                            offset_gl = close_vol * (trade_data.price - pos_status_dict["avg_price"]
                                                     ) * (-1 if trade_data.direction == Direction.LONG.value else 1)
                            # 平均价格不变
                            avg_price_new = pos_status_dict["avg_price"] if curr_closing_trade_data_vol_left != 0 else 0
                        else:
                            # 计算平仓盈亏
                            # 平仓逻辑分为两条线
                            # 1）按照最近一个持仓状态计算仓位及平均价格，当 holding_trade_data_list 为空的情况下
                            # 2）按照先入先出队列进行计算仓位及平均价格等(当前分支的逻辑）
                            offset_gl = 0
                            # 根据先入先出原则处理检查平仓了多少个历史的交易订单
                            close_vol = trade_data.volume
                            holding_price = pos_status_dict["avg_price"] \
                                if curr_closing_trade_data is None else curr_closing_trade_data.price
                            if curr_closing_trade_data_vol_left >= close_vol:
                                curr_closing_trade_data_vol_left -= close_vol
                                offset_gl += close_vol * (
                                        trade_data.price - holding_price
                                ) * (1 if trade_data.direction == Direction.SHORT.value else -1)
                            else:
                                if curr_closing_trade_data_vol_left > 0:
                                    offset_gl += curr_closing_trade_data_vol_left * (
                                            trade_data.price - holding_price
                                    ) * (1 if trade_data.direction == Direction.SHORT.value else -1)
                                    close_vol = trade_data.volume - curr_closing_trade_data_vol_left
                                else:
                                    close_vol = trade_data.volume

                                for i in range(len(holding_trade_data_list)):
                                    # 先入先出，总是从第一个位置去交易数据
                                    curr_closing_trade_data = holding_trade_data_list.pop(0)
                                    curr_closing_trade_data_vol_left = curr_closing_trade_data.volume
                                    if curr_closing_trade_data_vol_left >= close_vol:
                                        offset_gl += close_vol * (
                                                trade_data.price - curr_closing_trade_data.price
                                        ) * (1 if trade_data.direction == Direction.SHORT.value else -1)
                                        curr_closing_trade_data_vol_left -= close_vol
                                        close_vol = 0
                                        break
                                    else:
                                        offset_gl += curr_closing_trade_data_vol_left * (
                                                trade_data.price - curr_closing_trade_data.price
                                        ) * (1 if trade_data.direction == Direction.SHORT.value else -1)
                                        close_vol -= curr_closing_trade_data_vol_left
                                else:
                                    if close_vol > 0:
                                        if curr_closing_trade_data is None:
                                            self.logger.warning(
                                                "交易记录 %s [%s] '%s' %s %s %.0f 当前持仓 %.0f 手，缺少与当前持仓对应的开仓交易记录，"
                                                "计算将以当前持仓的平均价格为准进行计算。如果需要完整计算结果，"
                                                "可以清楚当前策略历史 position_status_model记录，进行重新计算。",
                                                strategy_name, symbol,
                                                trade_data.tradeid, trade_data.direction, trade_data.offset,
                                                trade_data.volume, volume)
                                            offset_gl += close_vol * (
                                                    trade_data.price - pos_status_dict['avg_price']
                                            ) * (1 if pos_status_dict['direction'] == Direction.LONG.value else -1)
                                        else:
                                            self.logger.warning(
                                                "交易记录 %s [%s] %s %s %s %.0f 当前持仓 %.0f 手，当前持仓全部订单不足以处理当前平仓，"
                                                "这种情况发生，说明当前持仓数据与交易数据的累加数字不一致，请检查数据是否缺失",
                                                strategy_name, symbol,
                                                trade_data.tradeid, trade_data.direction, trade_data.offset,
                                                trade_data.volume, volume)
                                            offset_gl += close_vol * (
                                                    trade_data.price - curr_closing_trade_data.price
                                            ) * (1 if curr_closing_trade_data.direction == Direction.LONG.value else -1)

                            # 计算平均价格
                            tot_value = curr_closing_trade_data_vol_left * curr_closing_trade_data.price \
                                if curr_closing_trade_data is not None else 0
                            tot_value += sum([
                                _.price * _.volume for _ in holding_trade_data_list
                            ])
                            tot_vol = curr_closing_trade_data_vol_left + sum(
                                [_.volume for _ in holding_trade_data_list])
                            avg_price_new = (tot_value / tot_vol) if tot_vol != 0 else 0

                        # 平仓盈亏需要 × 乘数
                        offset_gl *= multiplier
                        offset_daily_gl += offset_gl
                        offset_acc_gl += offset_gl
                        # 计算持仓盈亏
                        latest_price = trade_data.price
                        volume = curr_closing_trade_data_vol_left + sum([_.volume for _ in holding_trade_data_list])
                        holding_gl = curr_closing_trade_data_vol_left * (latest_price - avg_price_new) * multiplier * (
                            1 if pos_status_dict['direction'] == Direction.LONG.value else -1)
                        trade_date = trade_data.datetime.date() if trade_data.datetime.hour < 21 else \
                            next_trade_date_dic[trade_data.datetime.date()]
                        # 持仓方向
                        if trade_data.offset == Offset.OPEN:
                            direction = trade_data.direction
                        else:
                            direction = Direction.SHORT.value if trade_data.direction == Direction.LONG.value else Direction.LONG.value
                        # 更新持仓状态信息
                        pos_status_new_dict = dict(
                            tradeid=trade_data.tradeid,
                            strategy_name=strategy_name,
                            symbol=symbol,
                            exchange=trade_data.exchange,
                            trade_date=trade_date,
                            trade_dt=trade_data.datetime,
                            direction=direction,
                            avg_price=avg_price_new,
                            latest_price=latest_price,
                            volume=volume,
                            holding_gl=holding_gl,
                            offset_gl=offset_gl,
                            offset_daily_gl=offset_daily_gl,
                            offset_acc_gl=offset_acc_gl,
                            update_dt=datetime.now(),
                        )

                    # 新的状态信息加入的列表
                    pos_status_new_list.append(pos_status_new_dict)
                    # 更新最新的持仓状态
                    pos_status_dict = pos_status_new_dict

                # 退出 for _ in range(2): 循环
                break

        # 更新的持仓数据插入数据库
        if len(pos_status_new_list) > 0:
            PositionStatusModel.bulk_replace(pos_status_new_list)

    @staticmethod
    def refresh_position_daily() -> List[dict]:
        """刷新每日策略持仓收益统计表"""
        strategy_symbol_pos_status_dic: Dict[str, Dict[str, PositionStatusModel]] = \
            PositionStatusModel.query_latest_position_status()
        strategy_status_list: List[StrategyStatus] = StrategyStatus.query_all()
        symbol_tick_dic: Dict[str, LatestTickPriceModel] = LatestTickPriceModel.query_all_latest_price()
        position_daily_list = []
        # AccountStrategyMapping
        account_stg_mapping_key_pos_pair_list = []
        for strategy_status in strategy_status_list:
            strategy_name = strategy_status.strategy_name
            if strategy_name not in strategy_symbol_pos_status_dic:
                continue
            symbol_pos_status_dic: Dict[str, PositionStatusModel] = strategy_symbol_pos_status_dic[strategy_name]
            for symbol, pos_status in symbol_pos_status_dic.items():
                instrument_type = get_instrument_type(symbol).upper()
                if instrument_type not in SYMBOL_SIZE_DIC:
                    logging.warning("%s [%s] 计算仓位状态时，缺少 %s 乘数数据（使用默认值10）",
                                    strategy_name, symbol, instrument_type)
                    multiplier = 10
                else:
                    multiplier = SYMBOL_SIZE_DIC[instrument_type]

                if symbol in symbol_tick_dic:
                    tick = symbol_tick_dic[symbol]
                    trade_date = tick.datetime.date()
                    latest_price = tick.price
                elif pos_status.trade_date < date.today():
                    continue
                else:
                    logging.error("%s [%s] 计算仓位状态时，缺少最新tick数据，跳过当前计算，请补充tick数据后重新计算",
                                  strategy_name, symbol)
                    continue

                holding_gl = pos_status.volume * (latest_price - pos_status.avg_price) * multiplier * (
                    1 if pos_status.direction == Direction.LONG.value else -1)
                offset_gl = 0 if pos_status.trade_date != trade_date else pos_status.offset_gl
                offset_daily_gl = 0 if pos_status.trade_date != trade_date else pos_status.offset_daily_gl
                position_daily_dic = dict(
                    strategy_name=pos_status.strategy_name,
                    symbol=pos_status.symbol,
                    exchange=pos_status.exchange,
                    trade_date=trade_date,
                    trade_dt=pos_status.trade_dt,
                    direction=pos_status.direction,
                    avg_price=pos_status.avg_price,
                    latest_price=latest_price,
                    volume=pos_status.volume,
                    holding_gl=holding_gl,
                    offset_gl=offset_gl,
                    offset_daily_gl=offset_daily_gl,
                    offset_acc_gl=pos_status.offset_acc_gl,
                    update_dt=datetime.now(),
                )
                position_daily_list.append(position_daily_dic)
                position = pos_status.volume if pos_status.direction == Direction.LONG.value else -pos_status.volume
                account_stg_mapping_key_pos_pair = (
                    dict(
                        user_name=pos_status.user_name,
                        broker_id=pos_status.broker_id,
                        short_name=pos_status.strategy_name,
                    ),
                    position
                )
                account_stg_mapping_key_pos_pair_list.append(account_stg_mapping_key_pos_pair)

        # 更新的持仓数据插入数据库
        if len(position_daily_list) > 0:
            PositionDailyModel.bulk_replace(position_daily_list)

        if len(account_stg_mapping_key_pos_pair_list) > 0:
            AccountStrategyMapping.bulk_update_position(account_stg_mapping_key_pos_pair_list)

        return position_daily_list

    @staticmethod
    def output_daily_report(name_cn=None) -> dict:
        """输出持仓记录、交易记录"""
        output_file_dic = {}
        output_folder = os.path.join("output", 'daily_reports')
        os.makedirs(output_folder, exist_ok=True)
        strategy_symbol_pos_daily_dic: Dict[str, Dict[str, PositionDailyModel]] = \
            PositionDailyModel.query_latest_position_daily()
        # 最新一个交易日
        trade_date = None
        # 持仓列表
        holding_list = []
        user_id, _ = get_account()
        for strategy_name, symbol_pos_daily_dic in strategy_symbol_pos_daily_dic.items():
            for symbol, pos_daily in symbol_pos_daily_dic.items():
                if pos_daily.volume == 0 and pos_daily.offset_daily_gl == 0:
                    # 当日没有持仓且没有平仓盈亏的记录不显示
                    continue
                if trade_date is None:
                    trade_date = pos_daily.trade_date
                else:
                    trade_date = max(trade_date, pos_daily.trade_date)

                holding_list.append([
                    symbol, strategy_name, pos_daily.direction, pos_daily.volume,
                    pos_daily.avg_price,
                    pos_daily.holding_gl, pos_daily.offset_daily_gl, pos_daily.offset_acc_gl,
                    pos_daily.latest_price, pos_daily.trade_date, pos_daily.trade_dt,
                ])

        if len(holding_list) > 0:
            df = pd.DataFrame(
                [_ for _ in holding_list if trade_date == _[-2]],
                columns=['合约', '策略名称', '持仓方向', '持仓手数', '持仓均价',
                         '持仓盈亏', '当日平仓盈亏', '累计平仓盈亏', '最新价格', '交易日', '最近成交时间']
            ).set_index(['合约', '策略名称']).sort_index()
            # file_path = os.path.join(output_folder, f"各策略持仓状态_{date_2_str(trade_date)}.csv")
            # df.to_csv(file_path, encoding='GBK')
            file_name = f"{date_2_str(trade_date)}_{user_id}_持仓状态.xlsx" if name_cn is None or name_cn == '' else \
                f"{date_2_str(trade_date)}_{user_id}_{name_cn}_持仓状态.xlsx"
            file_path = os.path.join(output_folder, file_name)
            df.to_excel(file_path)
            StrategyPositionMonitor.logger.info("当前持仓：\n%s", df)
            output_file_dic[file_name] = file_path

        # 前一个交易日
        trade_date_list = TradeDateModel.query_latest_n_trade_date_list(2)
        # 通过记录获取交易日数据，选择上一交易日
        if len(trade_date_list) > 0:
            if len(trade_date_list) == 1:
                trade_date_last = trade_date_list[-1] - timedelta(days=1)
            else:
                trade_date_last = trade_date_list[-1]

            update_dt = str_2_datetime(date_2_str(trade_date_last) + " 15:00:00")
            strategy_symbol_trade_data_list_dic: Dict[str, Dict[str, List[TradeDataModel]]] = \
                TradeDataModel.query_trade_data_since(update_dt=update_dt)
            trade_list = []
            for strategy_name, symbol_trade_data_list_dic in strategy_symbol_trade_data_list_dic.items():
                for symbol, trade_data_list in symbol_trade_data_list_dic.items():
                    for trade_data in trade_data_list:
                        trade_list.append([
                            trade_data.symbol, trade_data.strategy_name, trade_data.direction, trade_data.offset,
                            trade_data.volume, trade_data.price, datetime_2_str(trade_data.datetime)
                        ])

            if len(trade_list) > 0:
                df = pd.DataFrame(
                    trade_list,
                    columns=['合约', '策略名称', '方向', '操作', '手数', '价格', '时间']
                ).set_index(['合约', '策略名称']).sort_index()
                # df.to_csv(os.path.join(output_folder, f"各策略交易明细_{date_2_str(trade_date)}.csv"), encoding='GBK')
                file_name = f"{date_2_str(trade_date)}_{user_id}_交易明细.xlsx" if name_cn is None or name_cn == '' else \
                    f"{date_2_str(trade_date)}_{user_id}_{name_cn}_交易明细.xlsx"
                file_path = os.path.join(output_folder, file_name)
                df.to_excel(file_path)
                StrategyPositionMonitor.logger.info("最近一个交易日交易数据：\n%s", df)
                output_file_dic[file_name] = file_path

        return output_file_dic

    @staticmethod
    def output_monthly_report(user_name=None, broker_id=None, description=None,
                              year=None, month=None, current_month=True):
        """输出月度持仓记录、交易记录"""
        today = date.today()
        if year is None:
            year = today.year if current_month or today.month != 1 else today.year - 1

        if month is None:
            if current_month:
                month = today.month
            else:
                month = today.month - 1 if today.month != 1 else 12

        date_since = date(year, month, 1) - timedelta(days=1)
        _, end_day = calendar.monthrange(year, month)
        date_until = date(year, month, end_day)
        if user_name:
            set_account(user_name, broker_id)
        else:
            user_name, broker_id = get_account()

        df_output, sum_df = StrategyPositionMonitor.output_report_between(
            date_since, date_until,
            file_name=f"{year}-{month:02d} 月度交易汇总 {user_name} {description if description else ''}.xlsx",
        )

        return df_output, sum_df  # 盈亏统计汇总, 按策略类统计

    @staticmethod
    def output_report_between(date_since, date_until, file_name=None, user_name=None, broker_id=None, description=None, ):
        """输出指定日期范围的持仓记录、交易记录"""
        if user_name:
            set_account(user_name, broker_id)
        else:
            user_name, broker_id = get_account()

        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)
        # 按截止日期进行查询各个策略及合约在当前时间结点下的盈亏统计
        since_df = pd.DataFrame([
            {
                'strategy_class_name': _.strategy_class_name,
                'strategy_name': _.strategy_name, 'symbol': _.symbol, date_since: _.offset_acc_gl
            } for _ in
            PositionStatusModel.query_position_status_list_until(date_since)
        ]).rename(columns={'strategy_class_name': '策略类名', 'strategy_name': '策略简称', 'symbol': '合约'})
        until_df = pd.DataFrame([
            {
                'strategy_class_name': _.strategy_class_name,
                'strategy_name': _.strategy_name, 'symbol': _.symbol, date_until: _.offset_acc_gl
            } for _ in
            PositionStatusModel.query_position_status_list_until(date_until)
        ]).rename(columns={'strategy_class_name': '策略类名', 'strategy_name': '策略简称', 'symbol': '合约'})
        if since_df.shape[0] > 0:
            df = pd.merge(
                since_df.set_index(['策略简称', '合约']).rename(columns={'策略类名': '策略类名_s'}),
                until_df.set_index(['策略简称', '合约']).rename(columns={'策略类名': '策略类名_u'}),
                left_index=True, right_index=True, how='outer')
            df['策略类名'] = df[['策略类名_s', '策略类名_u']].apply(
                lambda row: row['策略类名_u'] if pd.isna(row['策略类名_s']) else row['策略类名_s'], axis=1)
        elif until_df.shape[0] > 0:
            until_df[date_since] = 0
            df = until_df.set_index(['策略简称', '合约'])
        else:
            logging.warning("没有数据可以统计")
            return

        count_df = pd.DataFrame([
            {'策略简称': key[0], '合约': key[1], "交易次数": value[0], "盈利次数": value[1], "亏损次数": value[2]}
            for key, value in PositionStatusModel.query_strategy_symbol_count_dic(date_since, date_until).items()
        ]).set_index(['策略简称', '合约'])
        df = df.merge(count_df, left_index=True, right_index=True).fillna(0)
        df['区间盈亏'] = df[date_until] - df[date_since]
        # df['策略类名'] = [_[0] for _ in df.index]
        df['策略简称'] = [_[0] for _ in df.index]
        df['合约'] = [_[1] for _ in df.index]
        df_output = df.set_index(['合约', '策略简称']).sort_index()[['区间盈亏', '交易次数', '盈利次数', '亏损次数']]
        if file_name is None:
            user_name, broker_id = get_account()
            file_name_no_ext = f"{date_2_str(date_since)} {date_2_str(date_until)} " \
                               f"{user_name} {description if description else ''} 盈亏统计汇总"
            file_name = f"{file_name_no_ext}.xlsx"
        else:
            file_name_no_ext, ext = os.path.splitext(file_name)
            if ext == "":
                file_name = f"{file_name_no_ext}.xlsx"

        file_path = os.path.join('output', file_name)
        df_output.to_excel(file_path)

        df['品种'] = df['合约'].apply(get_instrument_type)
        sum_df = df[['策略类名', '品种', '区间盈亏']].groupby(
            by=['策略类名', '品种']).sum().reset_index().pivot('策略类名', '品种')

        sum_df.loc['汇总'] = sum_df.sum(0)  # 每列求和汇总
        sum_df[('区间盈亏', '汇总')] = sum_df.sum(1)  # 每行求和汇总

        sum_file_name = f"{file_name_no_ext}_按策略类统计.xlsx"
        file_path = os.path.join('output', sum_file_name)
        sum_df.to_excel(file_path)

        return df_output, sum_df  # 盈亏统计汇总, 按策略类统计

    def refresh_position_and_report(self, name_cn=None) -> dict:
        user_name, broker_id = get_account()
        self.logger.info(f"{'*' * 20} {user_name}[{broker_id}] 开始更新持仓信息 {'*' * 20}")
        self.refresh_positions()
        StrategyPositionMonitor.refresh_position_daily()
        return StrategyPositionMonitor.output_daily_report(name_cn)

    def run(self) -> None:
        while self.is_running:
            target_dt, seconds = self.get_sleep_seconds()
            self.logger.debug("wake up at %s", datetime_2_str(target_dt))
            sleep(seconds)
            self.refresh_position_and_report()


strategy_position_monitor = StrategyPositionMonitor()


def start_strategy_position_monitor():
    """启动 持仓监控器。监控器作为全局使用，因此只能有一个实例，且只能start一次"""
    with strategy_position_monitor.lock:
        if not strategy_position_monitor.is_alive():
            strategy_position_monitor.start()


def _test_position_status_monitor():
    user_name = "071001"
    broker_id = "9999"
    # user_name = "19510002"
    # broker_id = "5118"
    from vnpy_extra.db.orm import set_account
    set_account(user_name, broker_id)
    monitor = StrategyPositionMonitor()
    # monitor.logger.info("target=%s, seconds=%.0f", *monitor.get_sleep_seconds(5))
    # monitor.logger.info("target=%s, seconds=%.0f", *monitor.get_sleep_seconds(10))
    # monitor.logger.info("target=%s, seconds=%.0f", *monitor.get_sleep_seconds(60))
    # StrategyPositionMonitor.refresh_position_daily()
    monitor.refresh_position_and_report()


class AccountStrategyStatusMonitor(Thread):
    """TODO: 改成单例模式"""

    def __init__(self, name, get_status_func, set_status_func, symbols, strategy_settings: dict):
        super().__init__(name=name)
        self.daemon = True
        self.get_status_func = get_status_func
        self.set_status_func = set_status_func
        self.symbols = symbols
        self.strategy_settings = strategy_settings
        self.lock = Lock()
        self.logger = logging.getLogger(name)
        self.run_task = StrategyStatus.is_table_exists()

    def run(self) -> None:
        if not self.run_task:
            self.logger.warning("%s thread is not running because run_task == false")
        # 首次启动初始化状态
        status_int_curr = self.get_status_func().value
        try:
            StrategyStatus.register_strategy(strategy_name=self.name, status=status_int_curr, symbols=self.symbols,
                                             strategy_settings=self.strategy_settings)
        except DatabaseError:
            self.logger.exception("register_strategy error")
            return
        # 记录最新状态并开始循环
        status_int_last = status_int_curr
        sleep_seconds = 30
        while self.run_task:
            sleep(sleep_seconds)
            try:
                with self.lock:
                    # 获取当前策略最新状态，检查是否与上一个状态存在变化，否则更新
                    status_int_curr = self.get_status_func().value
                    # 检查数据库状态与上一状态是否一致，否则更新当前策略状态
                    status_int_db = StrategyStatus.query_status(self.name)

                try:
                    status = AccountStrategyStatusEnum(status_int_db)
                    if sleep_seconds != 2:
                        sleep_seconds = 2
                except ValueError:
                    self.logger.warning("%s 状态 %s 无效", self.name, str(status_int_db))
                    sleep_seconds = 300
                    continue
                if status_int_curr != status_int_last:
                    # 检查是否与上一个状态存在变化，否则更新
                    StrategyStatus.set_status(self.name, status=status_int_curr)
                    status_int_last = status_int_curr
                elif status_int_db != status_int_curr:
                    # 检查数据库状态与上一状态是否一致，否则更新当前策略状态
                    self.set_status_func(status)
                    status_int_last = status_int_db
            except:
                self.logger.exception("%s Monitor Error", self.name)


def _test_strategy_status_monitor():
    class Stg:
        def __init__(self, name):
            self.name = name
            self.status: AccountStrategyStatusEnum = AccountStrategyStatusEnum.Created
            self.lock: [Lock] = None

        def set_status(self, status: AccountStrategyStatusEnum):
            if self.lock is not None:
                self.lock.acquire()
            try:
                self.status = status
            finally:
                if self.lock is not None:
                    self.lock.release()

        def get_status(self) -> AccountStrategyStatusEnum:
            return self.status

    stg = Stg('test_monitor')
    monitor = AccountStrategyStatusMonitor(stg.name, stg.get_status, stg.set_status, symbols='rb2101.SHFE',
                                           strategy_settings={})
    stg.lock = monitor.lock
    monitor.start()
    sleep(2)
    # 初始化状态同步
    assert StrategyStatus.query_status(stg.name) == stg.status.value == AccountStrategyStatusEnum.Stopped.Created
    stg.status = AccountStrategyStatusEnum.Stopped
    sleep(2)
    # 修改策略状态，自动同步数据库
    assert StrategyStatus.query_status(stg.name) == stg.status.value == AccountStrategyStatusEnum.Stopped.value
    StrategyStatus.set_status(stg.name, AccountStrategyStatusEnum.Running)
    sleep(2)
    # 修改数据库，自动同步当前策略状态
    assert StrategyStatus.query_status(stg.name) == stg.status.value == AccountStrategyStatusEnum.Running
    StrategyStatus._meta.database.close()
    monitor.run_task = False
    monitor.join()


def test_monthly_report():
    user_name = "11859087"
    broker_id = "95533"
    from vnpy_extra.db.orm import set_account
    set_account(user_name, broker_id)
    StrategyPositionMonitor.output_monthly_report()


def test_report_between():
    user_name = "11859087"
    broker_id = "95533"
    from vnpy_extra.db.orm import set_account
    set_account(user_name, broker_id)
    date_since = str_2_date('2021-06-14')
    date_until = str_2_date('2021-06-21')
    StrategyPositionMonitor.output_report_between(date_since=date_since, date_until=date_until)


if __name__ == "__main__":
    # _test_strategy_status_monitor()
    # _test_position_status_monitor()
    # test_monthly_report()
    test_report_between()
