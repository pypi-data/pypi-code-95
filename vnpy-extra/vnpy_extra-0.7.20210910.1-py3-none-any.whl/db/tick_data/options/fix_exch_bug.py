"""
@author  : MG
@Time    : 2021/7/23 8:16
@File    : fix_exch_bug.py
@contact : mmmaaaggg@163.com
@desc    : 用于修正交易所错误。 由于此前脚本问题，导致部分品种交易所错误。
"""
import logging

from tqdm import tqdm

from vnpy_extra.constants import INSTRUMENT_EXCHANGE_DIC
from vnpy_extra.utils.symbol import PATTERN_INSTRUMENT_TYPE_OPTION, get_instrument_type


def fix_exchange():
    logger = logging.getLogger()
    sql_str = "SELECT distinct symbol  FROM dbbardata where `interval`='1m'"
    update_sql_str = "update dbbardata set exchange=%s where symbol=%s and exchange <> %s"
    from vnpy_extra.db.orm import database
    symbols = [symbol for (symbol,) in database.execute_sql(sql_str)]
    symbol_count = len(symbols)
    # drop_index_sql = """ALTER TABLE `dbbardata` DROP INDEX `dbbardata_symbol_exchange_interval_datetime`"""
    # logger.warning("删除索引 dbbardata_symbol_exchange_interval_datetime")
    # database.execute_sql(drop_index_sql)
    logger.info("任务开始 %d 个合约将被修改", symbol_count)
    is_goon = False
    for num, symbol in tqdm(enumerate(symbols, start=1), total=symbol_count):
        if symbol == 'SR1811-P-4900':
            is_goon = True
        if not is_goon:
            continue
        instrument_type = get_instrument_type(symbol, pattern=PATTERN_INSTRUMENT_TYPE_OPTION, error_log=False)
        if not instrument_type:
            instrument_type = get_instrument_type(symbol)

        try:
            exch = INSTRUMENT_EXCHANGE_DIC[instrument_type].value
        except KeyError:
            logger.exception(f"symbol={symbol}")
            continue
        logger.info(f"{num}/{symbol_count}) {symbol}.{exch}")
        database.execute_sql(update_sql_str, [exch, symbol, exch])

    # build_index_sql = "ALTER TABLE `dbbardata` ADD UNIQUE INDEX `dbbardata_symbol_exchange_interval_datetime` " \
    #                   "(`symbol` ASC, `datetime` DESC, `interval` ASC, `exchange` ASC) VISIBLE"
    # logger.warning("重建索引 dbbardata_symbol_exchange_interval_datetime")
    # database.execute_sql(build_index_sql)
    logger.info("任务完成")


if __name__ == "__main__":
    fix_exchange()
