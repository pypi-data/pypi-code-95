"""
@author  : MG
@Time    : 2020/12/25 9:38
@File    : data_available_check.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import logging
from datetime import timedelta, datetime

from ibats_utils.mess import datetime_2_str
from vnpy_extra.constants import INSTRUMENT_TRADE_TIME_PAIR_DIC
from vnpy_extra.db.orm import database
from vnpy_extra.utils.symbol import get_instrument_type

logger = logging.getLogger(__name__)


def data_available_check(symbol='rb2105'):
    """每日早晨检查昨夜夜盘行情是否导入到数据库"""
    sql_str = """SELECT `datetime`, `exchange` FROM dbbardata 
    where symbol=%s and `interval`='1m' order by `datetime` desc limit 1"""
    # 获取当前交易日以及上一个交易日
    sql_str_curr_last_trade_date = """SELECT trade_date FROM trade_date_model
    where trade_date<=curdate() order by trade_date desc limit 2
    """
    try:
        trade_date_latest = None
        for num, row in enumerate(database.execute_sql(sql_str_curr_last_trade_date).fetchall()):
            # 如果第一天记录不是当日，则说明当天不是交易日
            # 此条记录即为上一个交易日
            if num == 0:
                if row[0] == datetime.now().date():
                    trade_date_curr = row[0]
                    trade_date_latest = row[0]
                else:
                    trade_date_curr = None
                    trade_date_last = row[0]
                    break
            else:
                trade_date_last = row[0]

        row = database.execute_sql(sql_str, [symbol]).fetchone()
        if row is None:
            logger.warning("%-6s 没有数据", symbol)
            return False
        else:
            datetime_max, exchange = row

        instrument_type = get_instrument_type(symbol).upper()
        _, end_time = INSTRUMENT_TRADE_TIME_PAIR_DIC[instrument_type]
        now = datetime.now()
        if 15 <= now.hour:
            # 15点以后按15点收盘时间计算
            expected_dt = datetime(trade_date_latest.year, trade_date_latest.month, trade_date_latest.day, 15, 0)
        elif end_time.hour <= 3:
            # 存在跨夜夜盘行情时，需要将日期+1
            trade_date_next = trade_date_last + timedelta(days=1)
            expected_dt = datetime(trade_date_next.year, trade_date_next.month, trade_date_next.day,
                                   end_time.hour, end_time.minute)
        else:
            expected_dt = datetime(trade_date_last.year, trade_date_last.month, trade_date_last.day,
                                   end_time.hour, end_time.minute)

        # 尾盘结束时间允许有1分钟的偏差
        if expected_dt - timedelta(minutes=2) <= datetime_max <= expected_dt:
            logger.info("%6s.%-4s [OK] 预期截止日期 %s 数据截止时间 %s",
                        symbol, exchange, datetime_2_str(expected_dt), datetime_max)
            return True
        else:
            logger.info("%6s.%-4s [Not yet] 预期截止日期 %s 数据截止时间 %s",
                        symbol, exchange, datetime_2_str(expected_dt), datetime_max)
            return False
    finally:
        database.close()


def _check_symbol_list():
    import itertools
    instrument_type_list = ['rb', 'hc', ]
    contract_year_month_list = ['2110']
    symbol_list = [instrument_type + year_month for instrument_type, year_month in
                   itertools.product(instrument_type_list, contract_year_month_list)]
    instrument_type_list = ['i', 'j', 'jm', 'm', 'p', 'jd']
    contract_year_month_list = ['2109']
    symbol_list.extend([instrument_type + year_month for instrument_type, year_month in
                        itertools.product(instrument_type_list, contract_year_month_list)])
    instrument_type_list = ['ap']
    contract_year_month_list = ['110']
    symbol_list.extend([instrument_type + year_month for instrument_type, year_month in
                        itertools.product(instrument_type_list, contract_year_month_list)])
    for symbol in symbol_list:
        data_available_check(symbol)


if __name__ == "__main__":
    _check_symbol_list()
