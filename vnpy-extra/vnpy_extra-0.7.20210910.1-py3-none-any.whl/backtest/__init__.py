"""
@author  : MG
@Time    : 2020/10/9 12:00
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import enum
import time
from datetime import datetime, timedelta
from functools import partial, lru_cache
from itertools import chain
from threading import Thread
from typing import List, Sequence, Callable, Optional, Tuple
from unittest import mock

from ibats_utils.mess import datetime_2_str
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.database import database_manager
from vnpy.trader.database.database_sql import SqlManager
from vnpy.trader.object import BarData

from vnpy_extra.utils.symbol import get_instrument_type

STR_FORMAT_DATETIME_NO_SECOND = '%Y-%m-%d %H:%M'


def check_datetime_trade_available(dt: datetime) -> bool:
    """判断可发送交易请求的时间段（中午11:30以后交易）"""
    hour = dt.hour
    minute = dt.minute
    is_available = 0 <= hour < 3 or 9 <= hour <= 10 or (11 == hour and minute < 30) or 13 <= hour < 15 or (21 <= hour)
    return is_available


def check_datetime_available(dt: datetime) -> bool:
    hour = dt.hour
    is_available = 0 <= hour < 3 or 9 <= hour < 15 or 21 <= hour
    return is_available


class CrossLimitMethod(enum.IntEnum):
    open_price = 0
    mid_price = 1
    worst_price = 2


class CleanupOrcaServerProcessIntermittent(Thread):

    def __init__(self, sleep_time=5, interval=1800):
        super().__init__()
        self.is_running = True
        self.interval = interval
        self.sleep_time = sleep_time
        self.sleep_count = interval // sleep_time

    def run(self) -> None:
        from plotly.io._orca import cleanup
        count = 0
        while self.is_running:
            time.sleep(self.sleep_time)
            count += 1
            if count % self.sleep_count == 0 or not self.is_running:
                cleanup()
                count = 0


DEFAULT_STATIC_ITEM_DIC = {
    "max_new_higher_duration": "新高周期",
    "daily_trade_count": "交易频度",
    "annual_return": "年化收益率%",
    "sortino_ratio": "索提诺比率",
    "info_ratio": "信息比",
    "return_drawdown_ratio": "卡玛比",
    "return_risk_ratio": "收益风险比",
    "return_most_drawdown_ratio": "毛收益回撤比",
    "return_loss_ratio": "收益损失比",
    "strategy_class_name": "strategy_class_name",
    "symbols": "symbols",
    "cross_limit_method": "cross_limit_method",
    "available": "available",
    "backtest_status": "backtest_status",
    "id_name": "id_name",
    "image_file_url": "图片地址",
}


class StopOpeningPos(enum.IntEnum):
    open_available = 0
    stop_opening_and_log = 1
    stop_opening_and_nolog = 2


class DuplicateNameOptions(enum.Enum):
    raise_error = "raise_error"
    no_change = "no_change"
    replace = "replace"


def do_nothing(*args, **kwargs):
    """空函数"""
    return


# 加载主力连续合约
@lru_cache(maxsize=6)
def mock_load_bar_data(
        _self: SqlManager,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime,
        write_log_func: Callable = None,
        symbol_is_main_tuples: Optional[Tuple[Tuple[str, bool], Tuple[str, bool]]] = None
) -> Sequence[BarData]:
    """
    :_self:
    :symbol: 合约
    :exchange:
    :interval:
    :start:
    :end:
    :write_log_func: 日至函数
    :secondary_symbol_list: 是否主力字典
    """
    from vnpy_extra.db.md_reversion_rights import get_symbol_marked_main_or_sec
    from vnpy_extra.db.orm import FutureAdjFactor
    # 整理参数
    if isinstance(start, datetime):
        start = start.replace(minute=0, second=0, microsecond=0)

    if isinstance(end, datetime):
        end = end.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    if write_log_func is None:
        write_log_func = do_nothing

    main_symbol = None
    data_len = 0
    load_continue_data = symbol.find('9999') == -1 and symbol.find('8888') == -1
    is_main_str = ''
    if load_continue_data:
        start_continue_data = start
        _is_main = None
        if symbol_is_main_tuples is not None:
            symbol_is_main_dic = {_[0]: _[1] for _ in symbol_is_main_tuples}
            if symbol in symbol_is_main_dic:
                _is_main = symbol_is_main_dic[symbol]

        if _is_main is None:
            try:
                # 2021-8-19 MG
                # 已经支持每日复权，此前只能按照周级别复权因此需要做跨周处理，此后不再需要
                _is_main = FutureAdjFactor.is_main(symbol, skip_current_week=False)
            except ValueError as exp:
                _is_main = None
                write_log_func(f'FutureAdjFactor 查询合约异常: {exp.args[0]},将对主力、次主力合约分别进行尝试获取', 'warning')

        data: List[BarData] = []
        latest_dt: Optional[datetime] = None
        for is_main in ([True, False] if _is_main is None else [_is_main]):
            main_symbol = get_symbol_marked_main_or_sec(symbol, is_main=is_main)
            s = (
                _self.class_bar.select().where(
                    (_self.class_bar.symbol == main_symbol)
                    & (_self.class_bar.exchange == exchange.value)
                    & (_self.class_bar.interval == interval.value)
                    & (_self.class_bar.datetime >= start_continue_data)
                    & (_self.class_bar.datetime <= end)
                ).order_by(_self.class_bar.datetime)
            )

            for db_bar in s:
                bar: BarData = db_bar.to_bar()
                # Portfolio 的情况下需要更加 vt_symbol 生成相应字典，因此需要对该属性进行调整
                bar.symbol = symbol
                bar.vt_symbol = f"{bar.symbol}.{bar.exchange.value}"
                data.append(bar)
                if latest_dt is None:
                    latest_dt = bar.datetime
                elif latest_dt < bar.datetime:
                    latest_dt = bar.datetime

            data_len = len(data)
            is_main_str = '主连合约' if _is_main else '次主连合约'
            if _is_main is None and data_len == 0:
                write_log_func(f"加载 {is_main_str}[{main_symbol}] {data_len} 条 将会再次尝试次主连合约"
                               f"[{datetime_2_str(start, STR_FORMAT_DATETIME_NO_SECOND)} ~ "
                               f"{datetime_2_str(end, STR_FORMAT_DATETIME_NO_SECOND)}]", 'warning')
            elif data_len > 0:
                # 仅当无法判断主力、次主力合约是才进行提示
                # write_log_func(f"加载{is_main_str}[{main_symbol}] {data_len}条 "
                #                f"[{datetime_2_str(start)} ~ {datetime_2_str(latest_dt)}]", "info")
                start = latest_dt + timedelta(minutes=1)
                break
            else:
                # write_log_func(f"加载{is_main_str}[{main_symbol}] {data_len}条 "
                #                f"[{datetime_2_str(start)} ~ {datetime_2_str(end)}]", 'warning')
                pass
    else:
        start_continue_data = None
        data = []
        data_len = 0

    s = (
        _self.class_bar.select().where(
            (_self.class_bar.symbol == symbol)
            & (_self.class_bar.exchange == exchange.value)
            & (_self.class_bar.interval == interval.value)
            & (_self.class_bar.datetime >= start)
            & (_self.class_bar.datetime <= end)
        ).order_by(_self.class_bar.datetime)
    )

    data_sub: List[BarData] = [db_bar.to_bar() for db_bar in s]
    data.extend(data_sub)
    if load_continue_data:
        data_sub_len = len(data_sub)
        write_log_func(f"加载{is_main_str}/当期合约分别：\n"
                       f"[{main_symbol:^11}] {data_len:6,d}条，[{symbol:^6}] {data_sub_len:6,d}条，"
                       f"累计 {data_len + data_sub_len:6,d} 条\n"
                       f"[{datetime_2_str(start_continue_data, STR_FORMAT_DATETIME_NO_SECOND)} ~"
                       f" {datetime_2_str(start, STR_FORMAT_DATETIME_NO_SECOND)} ~"
                       f" {datetime_2_str(end, STR_FORMAT_DATETIME_NO_SECOND)}]。"
                       )

    return data


def generate_mock_load_bar_data(
        write_log_func: Callable = None,
        symbol_is_main_tuples: Optional[Tuple[Tuple[str, bool], Tuple[str, bool]]] = None):
    side_effect = mock.Mock(side_effect=partial(
        mock_load_bar_data, database_manager, write_log_func=write_log_func,
        symbol_is_main_tuples=symbol_is_main_tuples))
    return mock.patch.object(SqlManager, 'load_bar_data', side_effect)


VT_SYMBOL_LIST_CFFEX = [
    # 金融期货
    "IF9999.CFFEX",  # 沪深300
    "IC9999.CFFEX",  # 中证500指数
    "IH9999.CFFEX",  # 上证50指数
]
VT_SYMBOL_LIST_BLACK = [
    # 黑色\煤炭
    "RB9999.SHFE",  # 螺纹钢
    "HC9999.SHFE",  # 热卷
    "I9999.DCE",  # 铁矿石
    "J9999.DCE",  # 焦炭
    "JM9999.DCE",  # 焦煤
    "SF9999.CZCE",  # 硅铁
    "SM9999.CZCE",  # 锰硅
    "ZC9999.CZCE",  # 郑煤
]
VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL = [
    # 贵金属/有色
    "AU9999.SHFE",  # 金
    "AG9999.SHFE",  # 银
    "CU9999.SHFE",  # 阴极铜
    "AL9999.SHFE",  # 铝
    "PB9999.SHFE",  # 铅
    "ZN9999.SHFE",  # 锌
    "NI9999.SHFE",  # 镍
    "SN9999.SHFE",  # 锡
]
VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL_NOT_FOR_TRADE = [
    "BC9999.INE",  # 国际铜 历史行情太短
    "SS9999.SHFE",  # 不锈钢 2019-09 上市，满两年后再说
]
VT_SYMBOL_LIST_CHEMICAL = [
    # 化工品
    "RU9999.SHFE",  # 天然橡胶
    "BU9999.SHFE",  # 石油沥青
    "MA9999.CZCE",  # 甲醇
    "TA9999.CZCE",  # PTA
    "EG9999.DCE",  # 甘醇
    "FU9999.SHFE",  # 燃油
    "L9999.DCE",  # 塑料
    "PP9999.DCE",  # PP 聚丙烯
    "EB9999.DCE",  # 苯乙烯
    "V9999.DCE",  # PVC
    "SP9999.SHFE",  # 纸浆
    "SC9999.INE",  # 原油
    "FG9999.CZCE",  # 平板玻璃
    "NR9999.INE",  # 20号胶  # 2019-08-12 上市
    "UR9999.CZCE",  # 尿素 2019-08-09 上市
]
VT_SYMBOL_LIST_CHEMICAL_NOT_FOR_TRADE = [
    # delete from dbbardata where symbol in ('FB9999', 'FB8888') and `interval`='1m' and `datetime`<'2019-12-01 00:00:00';
    "FB9999.DCE",  # 纤维板  # 2019-12-02 之前的数据无效（品种有变化，此前的行情数据没有参考意义） 时间太短，不具有参考意义。
    "PG9999.DCE",  # LPG液化石油气  # 历史数据太短 2020-03-30
    "WR9999.SHFE",  # 线材 成交量不活跃
]
VT_SYMBOL_LIST_AGRICULTURE = [
    # 农产品
    "JD9999.DCE",  # 鸡蛋
    "AP9999.CZCE",  # 苹果
    "CJ9999.CZCE",  # 干制红枣
    "A9999.DCE",  # 黄大豆1号
    # 删除此前历史数据
    # delete from dbbardata where symbol in ('B9999', 'B8888') and `interval`='1m' and `datetime`<'2018-01-01 00:00:00';
    # 删除主力合约对应历史数据
    # delete from dbbardata where symbol IN ('B9999_2110', 'B8888_2110') AND `DATETIME`<'2018-01-01';
    "B9999.DCE",  # 黄大豆2号  # 2018年之前的数据没有成交量，一条锯齿线，没有参考意义。
    "C9999.DCE",  # 玉米
    "CS9999.DCE",  # 淀粉
    "M9999.DCE",  # 豆粕
    "OI9999.CZCE",  # 菜籽油
    "Y9999.DCE",  # 大豆原油
    "RM9999.CZCE",  # 菜籽粕
    "P9999.DCE",  # 棕榈油
    "SR9999.CZCE",  # 白砂糖
    "CF9999.CZCE",  # 一号棉花
    "CY9999.CZCE",  # 棉纱
]
VT_SYMBOL_LIST_AGRICULTURE_NOT_FOR_TRADE = [
    "WH9999.CZCE",  # 强麦  # 交易不活跃
    "PM9999.CZCE",  # 普麦  # 交易不活跃
    "RI9999.CZCE",  # 早稻  # 历史行情不够活跃
    "JR9999.CZCE",  # 粳稻  # 历史行情不够活跃 2013-11-18
    "LR9999.CZCE",  # 晚稻  # 交易不活跃
    "RR9999.DCE",  # 粳米  # 历史数据太短 2019-08-16
    "RS9999.CZCE",  # 油菜籽  # 历史行情不够活跃 2013-09-16
    "PK9999.CZCE",  # 花生仁  # 2021-02-01
    "LH9999.DCE",  # 生猪  # 2021-01-08
]
VT_SYMBOL_LIST_ALL = []
for _ in [
    VT_SYMBOL_LIST_BLACK,
    VT_SYMBOL_LIST_CFFEX,
    VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL,
    VT_SYMBOL_LIST_CHEMICAL,
    VT_SYMBOL_LIST_AGRICULTURE,
]:
    VT_SYMBOL_LIST_ALL.extend(_)


class InstrumentClassificationEnum(enum.Enum):
    BLACK = set([
        get_instrument_type(_).upper() for _ in chain(VT_SYMBOL_LIST_BLACK)])
    CFFEX = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_CFFEX)])
    PRECIOUS_NONFERROUS_METAL = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL,
                                              VT_SYMBOL_LIST_PRECIOUS_NONFERROUS_METAL_NOT_FOR_TRADE)])
    CHEMICAL = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_CHEMICAL, VT_SYMBOL_LIST_CHEMICAL_NOT_FOR_TRADE)])
    AGRICULTURE = set([
        get_instrument_type(_) for _ in chain(VT_SYMBOL_LIST_AGRICULTURE, VT_SYMBOL_LIST_AGRICULTURE_NOT_FOR_TRADE)])
    All = set(VT_SYMBOL_LIST_ALL)


INSTRUMENT_TYPE_MAIN_CONTRACT_DIC = {get_instrument_type(_).upper(): _ for _ in VT_SYMBOL_LIST_ALL}
