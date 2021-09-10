"""
@author  : MG
@Time    : 2020/12/9 13:05
@File    : collector.py
@contact : mmmaaaggg@163.com
@desc    : 用户收集策略运行过程中的下单、成交等数据
采用独立线程进行数据采集工作，以避免出现因插入数据造成策略延迟或阻塞，保证策略线程运行平稳
"""
__all__ = ('trade_data_collector', 'order_data_collector', 'latest_price_collector')

import logging
from datetime import date
from queue import Queue, Empty
from threading import Thread
from typing import List
import pandas as pd

from vnpy.trader.constant import OrderType, Status
from vnpy.trader.object import TradeData, OrderData, TickData

from vnpy_extra.db.orm import database, TradeDataModel, OrderDataModel, LatestTickPriceModel


class OrderDataCollector(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.queue = Queue()
        self.queue_timeout = 90
        self.is_running = True
        self.logger = logging.getLogger(self.__class__.__name__)

    def put_nowait(self, strategy_name, trade_data):
        self.queue.put_nowait((strategy_name, trade_data))

    def join_queue(self):
        self.queue.join()

    def run(self) -> None:
        data_list: List[(str, OrderData,)] = []
        order_id = 10000
        try:
            while self.is_running:
                try:
                    strategy_name, order_data = self.queue.get(timeout=self.queue_timeout)
                    if isinstance(order_data, dict):
                        order_data['strategy_name'] = strategy_name
                        if 'orderid' not in order_data:
                            order_id += 1
                            order_data['orderid'] = order_id
                        if 'order_type' not in order_data:
                            order_data['order_type'] = OrderType.LIMIT.value
                        if 'status' not in order_data:
                            order_data['status'] = Status.SUBMITTING.value

                        data_list.append(order_data)
                    else:
                        data_list.append(dict(
                            strategy_name=strategy_name,
                            orderid=order_data.orderid,
                            symbol=order_data.symbol,
                            exchange=order_data.exchange.value,
                            order_type=order_data.type.value,
                            direction=order_data.direction.value,
                            offset=order_data.offset.value,
                            price=order_data.price,
                            volume=order_data.volume,
                            status=order_data.status.value,
                            datetime=order_data.datetime,
                        ))
                    self.queue.task_done()
                except Empty:
                    if len(data_list) == 0:
                        continue
                    # 攒够一个list，开始集中插入
                    OrderDataModel.bulk_replace(data_list)
                    self.logger.info("插入订单数据 %d 条", len(data_list))
                    data_list = []

        except Exception as exp:
            self.logger.exception("插入订单数据异常")
            raise exp from exp
        finally:
            self.logger.info("订单数据收集线程关闭")


order_data_collector = OrderDataCollector()
order_data_collector.start()


class TradeDataCollector(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.queue = Queue()
        self.queue_timeout = 90
        self.is_running = True
        self.logger = logging.getLogger(self.__class__.__name__)

    def put_nowait(self, strategy_name, trade_data):
        self.queue.put_nowait((strategy_name, trade_data))

    def join_queue(self):
        self.queue.join()

    def run(self) -> None:
        self.logger.info("交易数据收集线程启动")
        data_list: List[(str, TradeData,)] = []
        try:
            while self.is_running:
                try:
                    strategy_name, trade_data = self.queue.get(timeout=self.queue_timeout)
                    today = date.today()
                    if trade_data.datetime is not None \
                            and trade_data.datetime.date() > today:
                        # 主要针对大商所等交易所，将夜盘9点钟以后的数据成交日期算作下一个交易日
                        # 在此对交易日期进行修正，改为当前日期
                        # 此逻辑对于跨日瞬间出现的成交单可能依然会存在问题。
                        # 但目前交易不涉及跨夜盘12点操作，因此暂不考虑
                        trade_data.datetime = trade_data.datetime.replace(today.year, today.month, today.day)

                    data_list.append(dict(
                        strategy_name=strategy_name,
                        symbol=trade_data.symbol,
                        exchange=trade_data.exchange.value,
                        orderid=trade_data.orderid,
                        tradeid=trade_data.tradeid.lstrip(),
                        direction=trade_data.direction.value,
                        offset=trade_data.offset.value,
                        price=trade_data.price,
                        volume=trade_data.volume,
                        datetime=trade_data.datetime,
                    ))
                    self.queue.task_done()
                except Empty:
                    if len(data_list) == 0:
                        continue
                    # 攒够一个list，开始集中插入
                    try:
                        TradeDataModel.bulk_replace(data_list)
                    except:
                        self.logger.exception("插入交易数据异常，稍后再次尝试")
                        pd.DataFrame(data_list).to_csv("TradeDataModel.csv")
                        continue

                    self.logger.info("插入交易数据 %d 条", len(data_list))
                    data_list = []

        except Exception as exp:
            self.logger.exception("插入交易数据异常")
            raise exp from exp
        finally:
            self.logger.info("交易数据收集线程关闭")


trade_data_collector = TradeDataCollector()
trade_data_collector.start()


class LatestPriceCollector(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.queue = Queue()
        self.is_running = True
        self.logger = logging.getLogger(self.__class__.__name__)

    def put_nowait(self, tick: TickData):
        self.queue.put_nowait(tick)

    def join_queue(self):
        self.queue.join()

    def run(self) -> None:
        symbol_tick_dic = {}
        is_updated = False
        while self.is_running:
            try:
                tick: TickData = self.queue.get(timeout=10)
                if 15 <= tick.datetime.hour < 21:
                    # 忽略收盘后的报价（收盘价会被结算价剃掉）
                    pass
                else:
                    symbol_tick_dic[tick.symbol] = tick
                    is_updated = True

                self.queue.task_done()
            except Empty:
                symbol_count = len(symbol_tick_dic)
                if symbol_count == 0 or not is_updated:
                    continue
                # 攒够一个list，开始集中插入
                try:
                    with database.atomic():
                        for num, (symbol, tick) in enumerate(symbol_tick_dic.items()):
                            # 每次批量插入100条，分成多次插入
                            LatestTickPriceModel.insert(
                                symbol=symbol, exchange=tick.exchange.value,
                                price=tick.last_price, volume=tick.volume, datetime=tick.datetime
                            ).on_conflict(
                                update=dict(
                                    price=tick.last_price, volume=tick.volume, datetime=tick.datetime
                                )
                            ).execute()
                            self.logger.debug("%d/%d) 更新 %s latest price %.2f",
                                              num, symbol_count, symbol, tick.last_price)
                            is_updated = False
                finally:
                    LatestTickPriceModel._meta.database.close()


latest_price_collector = LatestPriceCollector()
latest_price_collector.start()
