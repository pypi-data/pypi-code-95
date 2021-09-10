#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/8/19 9:57
@File    : import_strategy_data.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import json
import logging
from datetime import datetime
from typing import Dict

from ibats_utils.transfer import datetime_2_str
from vnpy.trader.constant import Direction, Offset

from vnpy_extra.db.orm import set_account, TradeDataModel, LatestTickPriceModel, PositionStatusModel


def id_generator():
    counter = 0
    while True:
        counter += 1
        trade_id = datetime_2_str(datetime.now(), f'%Y_%m_%d_%H_%M_%S_%f_{counter}')
        yield trade_id


logger = logging.getLogger(__name__)


def import_cta_strategy_data_json(user_name, broker_id, data_json_file_path, symbol_price_dic=None):
    """读取 cta_strategy_data.json 文件，将持仓信息同步到数据库，仓位不一致的情况将通过补充交易数据来同步"""
    set_account(user_name, broker_id)
    with open(data_json_file_path, 'r', encoding='utf-8') as fp:
        key_pos_dic = json.load(fp)

    key_count = len(key_pos_dic)
    if len(key_pos_dic) == 0:
        return
    if symbol_price_dic:
        try:
            LatestTickPriceModel.insert_price_by_dic(symbol_price_dic)
        except:
            logger.exception(f"{user_name}[{broker_id}] 插入最新价格异常，不影响后续程序运行")

    logger.info(f"{user_name}[{broker_id}] 存在 {key_count} 条记录待匹配，首先更新持仓状态")
    from vnpy_extra.report.monitor import StrategyPositionMonitor
    StrategyPositionMonitor().refresh_positions()
    StrategyPositionMonitor.refresh_position_daily()
    logger.info(f"{user_name}[{broker_id}] 获取账户持仓记录")
    strategy_symbol_pos_status_dic: Dict[
        str, Dict[str, PositionStatusModel]] = PositionStatusModel.query_latest_position_status()
    key_pos_status_dic: Dict[str, PositionStatusModel] = {}
    for strategy_name, symbol_pos_status_dic in strategy_symbol_pos_status_dic.items():
        if len(symbol_pos_status_dic) != 1:
            continue
        pos_status = symbol_pos_status_dic[list(symbol_pos_status_dic.keys())[0]]
        key_pos_status_dic[strategy_name] = pos_status

    # 创建 id 生成器对象
    id_fn = id_generator()

    def generate_trade_data(direction: Direction, offset: Offset, volume: int) -> TradeDataModel:
        nonlocal price
        if price == 0:
            if symbol_price_dic:
                price = symbol_price_dic.get(symbol, 0)

        if price == 0:
            obj = LatestTickPriceModel.query_latest_price(symbol)
            if obj:
                price = obj.price
            else:
                raise ValueError(f"{num}/{count}) {user_name}[{broker_id}] {key}[{symbol}] 没有找到价格")

        new_id = next(id_fn)
        _trade_data = TradeDataModel(
            user_name=user_name,
            broker_id=broker_id,
            strategy_name=key,
            tradeid=new_id,
            symbol=symbol,
            exchange=exchange,
            orderid=new_id,
            direction=direction.value,
            offset=offset.value,
            price=price,
            volume=volume,
            datetime=datetime_2_str(datetime.now())
        )
        logger.info(f"{num}/{count}) {user_name}[{broker_id}] {key}[{symbol}] {new_id}:"
                    f"{offset.value} {direction.value} {volume} {price}")
        return _trade_data

    # 汇总 key
    logger.info(f"{user_name}[{broker_id}] 对比文件与数据库持仓记录")
    count = len(key_pos_status_dic)
    empty_json_pos = dict(pos=0)
    trade_list = []
    for num, (key, pos_status) in enumerate(key_pos_status_dic.items(), start=1):
        # json 文件中显示的仓位
        json_pos = key_pos_dic.get(key, empty_json_pos)["pos"]
        # 数据库账户中显示的仓位
        account_pos = pos_status.volume if pos_status.direction == Direction.LONG.value else -pos_status.volume
        if account_pos == json_pos:
            continue

        close_long, open_long, close_short, open_short = 0, 0, 0, 0
        symbol, exchange = pos_status.symbol, pos_status.exchange
        logger.warning(
            f"{num}/{count}) {user_name}[{broker_id}] {key} db->json {account_pos} -> {json_pos}")

        if account_pos <= 0 <= json_pos:
            close_long = abs(account_pos)
            open_long = abs(json_pos)
        elif account_pos >= 0 >= json_pos:
            close_short = abs(account_pos)
            open_short = abs(json_pos)
        elif account_pos <= 0 and json_pos <= 0:
            diff = account_pos - json_pos
            if diff > 0:
                open_short = abs(diff)
            else:
                close_long = abs(diff)
        elif account_pos > -0 and json_pos >= 0:
            diff = account_pos - json_pos
            if diff > 0:
                close_long = abs(diff)
            else:
                open_short = abs(diff)
        else:
            raise ValueError(
                f"{num}/{count}) {user_name}[{broker_id}] {key}[{symbol}] "
                f" db->json {account_pos} -> {json_pos}")

        # 增加相应交易记录
        price = 0
        if close_long > 0:
            trade_data = generate_trade_data(Direction.LONG, Offset.CLOSE, close_long)
            trade_list.append(trade_data)

        if close_short > 0:
            trade_data = generate_trade_data(Direction.SHORT, Offset.CLOSE, close_short)
            trade_list.append(trade_data)

        if open_long > 0:
            trade_data = generate_trade_data(Direction.LONG, Offset.OPEN, open_long)
            trade_list.append(trade_data)

        if open_short > 0:
            trade_data = generate_trade_data(Direction.SHORT, Offset.OPEN, open_short)
            trade_list.append(trade_data)

    if len(trade_list) > 0:
        TradeDataModel.bulk_create(trade_list)
        logger.info(f"{user_name}[{broker_id}] 增加交易记录 {len(trade_list)} 条，开始更新持仓状态。")
        # 更新 report
        from vnpy_extra.report.monitor import StrategyPositionMonitor
        StrategyPositionMonitor().refresh_positions()
        StrategyPositionMonitor.refresh_position_daily()
    else:
        logger.info(f"{user_name}[{broker_id}] 完全匹配。")


def _run_import():
    user_name, broker_id = "071001", "9999"  # 建信期货（资本）
    data_json_file_path = r"d:\TraderTools\vnpy_work_root\simnow_071001\.vntrader\cta_strategy_data.json"
    symbol_price_dic = {
        "C2109": 2572,
    }
    import_cta_strategy_data_json(user_name, broker_id, data_json_file_path, symbol_price_dic)


if __name__ == "__main__":
    _run_import()
