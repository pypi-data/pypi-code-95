"""
@author  : MG
@Time    : 2020/9/27 13:11
@File    : md_reversion_rights.py
@contact : mmmaaaggg@163.com
@desc    : 用于将指定期货品种的各个合约行情数据通过复权因子合并成为主力连续合约数据，以及次主力联系合约数据
"""
import itertools
import os
import typing
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta
from enum import Enum

import pandas as pd
from tqdm import tqdm
from vnpy.trader.constant import Interval
from vnpy.trader.database import database_manager

from vnpy_extra.config import logging
from vnpy_extra.constants import INSTRUMENT_EXCHANGE_DIC
from vnpy_extra.db.orm import database
from vnpy_extra.utils.symbol import get_instrument_type

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Method(Enum):
    """
    方法枚举，value为对应的默认 adj_factor 因子值
    """
    division = 1
    diff = 0


def get_symbol_marked_main_or_sec(symbol, is_main):
    instrument_type = get_instrument_type(symbol)
    contract_no = symbol.upper().lstrip(instrument_type.upper()).split('.')[0]
    return f"{instrument_type.upper()}{'9999' if is_main else '8888'}_{contract_no}"


def generate_md_with_adj_factor(
        instrument_type: str,
        adj_factor_dir: str = None,
        table_name: str = None,
        intervals: typing.List[Interval] = None,
        method: typing.Optional[Method] = Method.division,
        incrementally=True,
        save_adj_md_with_latest_symbol_mark=True,
        remove_old_symbol_until_nth_latest=3,
):
    """
    将指定期货品种生产复权后价格。
    主力合约名称 f"{instrument_type.upper()}9999"
    次主力合约名称 f"{instrument_type.upper()}8888"
    仅针对 OHLC 四个价格进行复权处理
    :param instrument_type 品种
    :param adj_factor_dir 调整因子所在文件目录（adj_factor_dir、table_name 其一不为空即可）
    :param table_name 调整因子所在数据库表名（adj_factor_dir、table_name 其一不为空即可）
    :param intervals 可以为空，默认只处理分钟级数据
    :param method 因子调整方法，默认 Method.division
    :param incrementally 是否使用增量方法。默认为True
    :param save_adj_md_with_latest_symbol_mark 是否在保存主力、次主力合约的同时，另外保存一份带当前合约名称的行情数据。
        例如 RB9999_2150。
        该合约将被用于"主连行情进行决策，当期主力合约实现买卖"的功能模块中
    :param remove_old_symbol_until_nth_latest 删除旧的“带 symbol 标记”的主连行情数据，截止到第N个最新的主力合约
    """
    if intervals is None:
        intervals = [
            Interval.MINUTE,
            # Interval.HOUR,  # 暂不维护小时级数据
        ]

    # 加载因子数据
    if table_name is not None:
        adj_factor_df = pd.read_sql(
            f"select * from {table_name} where instrument_type=%s and method=%s",
            database,
            params=[instrument_type, 'division' if method is None else method.name],
            parse_dates=['trade_date']
        )
    else:
        if method is None:
            file_path = os.path.join(adj_factor_dir, f"adj_factor_{instrument_type}.csv")
        else:
            file_path = os.path.join(adj_factor_dir, f"adj_factor_{instrument_type}_{method.name}.csv")

        adj_factor_df = pd.read_csv(file_path, parse_dates=['trade_date'])

    # 处理因子数据
    adj_factor_df.sort_values(['trade_date'], inplace=True)
    adj_factor_df['trade_date_larger_than'] = adj_factor_df['trade_date'].shift(1)
    adj_factor_df.set_index(['trade_date_larger_than', 'trade_date'], inplace=True)
    n_final = adj_factor_df.shape[0]
    symbol_label_pairs = [
        (f"{instrument_type.upper()}9999", "instrument_id_main", "adj_factor_main"),
        (f"{instrument_type.upper()}8888", "instrument_id_secondary", "adj_factor_secondary")]
    if save_adj_md_with_latest_symbol_mark:
        latest_symbol_main = adj_factor_df.iloc[-1, :]['instrument_id_main']
        latest_symbol_sec = adj_factor_df.iloc[-1, :]['instrument_id_secondary']
        if not pd.isna(latest_symbol_main):
            symbol_label_pairs.append(
                (get_symbol_marked_main_or_sec(latest_symbol_main, True),
                 "instrument_id_main", "adj_factor_main")
            )
        if not pd.isna(latest_symbol_sec):
            symbol_label_pairs.append(
                (get_symbol_marked_main_or_sec(latest_symbol_sec, False),
                 "instrument_id_secondary", "adj_factor_secondary")
            )

    main_sec_symbols = [_[0] for _ in symbol_label_pairs]

    # 处理历史行情数据
    try:
        for interval in intervals:
            if remove_old_symbol_until_nth_latest > 0:
                removed_symbol_list = [
                    get_symbol_marked_main_or_sec(_, True, )
                    for _ in
                    adj_factor_df['instrument_id_main'].drop_duplicates().iloc[:-remove_old_symbol_until_nth_latest]
                    if not pd.isna(_)]
                removed_symbol_list.extend([
                    get_symbol_marked_main_or_sec(_, False, )
                    for _ in adj_factor_df['instrument_id_secondary'].drop_duplicates().iloc[
                             :-remove_old_symbol_until_nth_latest]
                    if not pd.isna(_)])

                if len(removed_symbol_list) > 0:
                    del_sql_str = f"delete from dbbardata " \
                                  f"where `symbol` in ({','.join(['%s' for _ in removed_symbol_list])}) " \
                                  f"and `interval` = %s"
                    removed_symbol_list.append(interval.value)
                    cursor = database.execute_sql(del_sql_str, params=removed_symbol_list)
                    rowcount = cursor.rowcount
                    if rowcount > 0:
                        logger.info("删除旧的带 symbol 历史主连、次主连行情数据 %s[%s] %d 条记录。 包括：%s",
                                    instrument_type, interval.value, rowcount, removed_symbol_list[:-1])

            if incrementally:
                # 增量处理
                # 首先查询主连合约，次主连合约最大日期
                # 如果日期小于最后一个因子调整值的日期，则说明，发生了合约切换。否则说没有发生合约切换。
                # 如果发生合约切换，需要将历史数据直接×调整因子（或 - 调整因子，取决于 method）。此后的数据正常进行因子调整后导入
                # 如果没有发生合约切换。在此数据后直接进行数据导入即可。
                sql_str = f"select `symbol`, max(`datetime`) from dbbardata " \
                          f"where `symbol` in ({','.join(['%s' for _ in main_sec_symbols])}) " \
                          f"and `interval` = %s group by `symbol`"
                params = [_ for _ in main_sec_symbols]
                params.append(interval.value)
                symbol_datetime_dic = dict(database.execute_sql(sql_str, params=params))
                for _ in main_sec_symbols:
                    symbol_datetime_dic.setdefault(_, None)

            else:
                sql_str = f"delete from dbbardata " \
                          f"where `symbol` in ({','.join(['%s' for _ in main_sec_symbols])}) " \
                          f"and `interval`=%s"
                params = [_ for _ in main_sec_symbols]
                params.append(interval.value)
                result = database.execute_sql(sql_str, params=params)
                logger.info("删除 %s '1m' 历史数据 %d 条", instrument_type, result.rowcount)
                symbol_datetime_dic = {_: None for _ in main_sec_symbols}

        sql_str_adj_his_md = """update dbbardata
            set open_price = open_price * %s, 
            high_price = high_price * %s,
            low_price = low_price * %s,
            close_price = close_price * %s
            where `symbol` = %s
            and `interval` = %s"""
        for n, ((trade_date_larger_than, trade_date), adj_factor_s) in enumerate(adj_factor_df.iterrows(), start=1):
            # 截止当日下午3点收盘，保守计算，延迟1个小时，到16点
            if pd.isna(trade_date_larger_than):
                start = None
            else:
                start = (pd.to_datetime(trade_date_larger_than) + pd.Timedelta('16H')).to_pydatetime()

            if n == n_final:
                if start is None:
                    start = pd.to_datetime('1990-01-01').to_pydatetime()
                    end = pd.to_datetime('2090-12-31').to_pydatetime()
                else:
                    end = start + timedelta(days=365)
            else:
                end = (pd.to_datetime(trade_date) + pd.Timedelta('16H')).to_pydatetime()
                if start is None:
                    start = end - timedelta(days=365)

            # 循环对 主力、次主力合约复权
            for interval, (symbol_new, id_label, adj_factor_label) in itertools.product(intervals, symbol_label_pairs):
                start_curr = start
                # 开始对所有合约进行历史行情复权调整
                instrument_id = adj_factor_s[id_label]
                if instrument_id is None or isinstance(instrument_id, float):
                    logger.error('%s %s 数据无效\n%s', instrument_type, id_label, adj_factor_s)
                    continue
                symbol, _ = instrument_id.split('.')
                adj_factor = adj_factor_s[adj_factor_label]
                # 判断历史行情的最新日期 是否小于 当前调整因子的截止日期
                if incrementally:
                    # 增量调整历史行情
                    if symbol_datetime_dic[symbol_new] is not None:
                        # 存在历史行情
                        if symbol_datetime_dic[symbol_new] < end:
                            # 历史行情小于当前主力合约的截止日期
                            if adj_factor != 1.0:
                                # 对历史行情数据进行因子调整
                                database.execute_sql(
                                    sql_str_adj_his_md,
                                    params=[adj_factor, adj_factor, adj_factor, adj_factor, symbol_new, interval.value]
                                )
                                logger.info("对 %s[%s] %s < %s 的历史数据进行因子调整 %.4f",
                                            symbol_new, interval, symbol_datetime_dic[symbol_new],
                                            end, adj_factor)

                            # 历史行情经过因子调整后，修改 start 时间，此后的数据，通过正常因子调整逻辑进行调整
                            start_curr = symbol_datetime_dic[symbol_new] + timedelta(minutes=1)
                            # 防止出现因子多次调整的情况，每一个合约每个周期只调整一次
                            symbol_datetime_dic[symbol_new] = None
                        else:
                            # 已存在行情数据，无需进一步处理
                            continue

                # 对新的行情进行因子调整
                instrument_type_upper = instrument_type.upper()
                if instrument_type_upper not in INSTRUMENT_EXCHANGE_DIC:
                    logger.error("%s 品种没有找到对应的交易所", instrument_type_upper)
                    continue
                exchange = INSTRUMENT_EXCHANGE_DIC[instrument_type_upper]
                bars = database_manager.load_bar_data(
                    symbol=symbol, exchange=exchange, interval=interval,
                    start=start_curr, end=end)
                bar_count = len(bars)
                if bar_count > 0:
                    for bar in bars:
                        bar.symbol = symbol_new
                        bar.open_price *= adj_factor
                        bar.high_price *= adj_factor
                        bar.low_price *= adj_factor
                        bar.close_price *= adj_factor

                    # 保存复权后的价格序列
                    database_manager.save_bar_data(bars)
                    logger.info("%s.%s %s 周期 [%s ~ %s] 包含 %d 条数据-> %s 完成",
                                symbol, exchange.name, interval.name, start_curr, end, bar_count, symbol_new)
                else:
                    logger.warning("%s.%s %s 周期 [%s ~ %s] 没有数据-> %s",
                                   symbol, exchange.name, interval.name, start_curr, end, symbol_new, )

        logger.info(f'{main_sec_symbols} 保存完成')

    finally:
        database.close()


def _test_generate_md_with_adj_factor():
    instrument_type = 'rb'
    adj_factor_dir = r'd:\github\data_integration_celery\output\2021-02-22'
    generate_md_with_adj_factor(
        instrument_type,
        # adj_factor_dir=adj_factor_dir,
        table_name='wind_future_adj_factor',
    )


def generate_adj_md(
        instrument_types, adj_factor_dir=None, table_name=None,
        method_filter: typing.Optional[Method] = None, until_instrument_type=None,
        pool_size=4,
        incrementally=True,
):
    """
    对指定类型进行复权数据生成
    :param instrument_types 类型列表，如果为None则为全部生成
    :param adj_factor_dir 复权因子目录
    :param table_name 数据库表名
    :param method_filter 方法筛选
    :param until_instrument_type 指定当前品种才开始运行（仅同调试使用），有时候运行中途出错，再次运行时，从报错的品种开始重新运行，而不是全部重新运行
    :param pool_size 线程池大小
    :param incrementally 是否增量调整
    """
    if instrument_types is None:
        if table_name is not None:
            sql_str = f"select distinct instrument_type from {table_name}"
            if method_filter is not None:
                sql_str += " where method = %s"
                df = pd.read_sql(sql_str, database, params=[method_filter.name])
            else:
                df = pd.read_sql(sql_str, database)

            instrument_types = list(df['instrument_type'])
        else:
            instrument_types = []
            files = os.listdir(adj_factor_dir)
            is_ok = until_instrument_type is None
            for file_name in files:
                name, ext = os.path.splitext(file_name)
                if ext != '.csv' or not name.startswith('adj_factor_'):
                    continue
                instrument_type, method = name.replace('adj_factor_', '').split('_')
                if not is_ok:
                    if instrument_type == until_instrument_type:
                        is_ok = True
                    else:
                        continue

                if method_filter is None:
                    instrument_types.append(instrument_type)
                else:
                    if method != method_filter.name:
                        continue
                    instrument_types.append((instrument_type, getattr(Method, method)))

    if pool_size <= 1:
        pool = None
    else:
        pool = ThreadPoolExecutor(max_workers=pool_size, thread_name_prefix="adj_md_")

    instrument_types_iter = tqdm(instrument_types, total=len(instrument_types))
    for instrument_type in instrument_types_iter:
        if isinstance(instrument_type, tuple):
            instrument_type, method = instrument_type
        else:
            method = method_filter

        instrument_types_iter.set_description(f"{instrument_type}[{method}]")
        params = dict(
            instrument_type=instrument_type,
            adj_factor_dir=adj_factor_dir,
            table_name=table_name,
            method=method,
            incrementally=incrementally
        )
        if pool_size <= 1:
            generate_md_with_adj_factor(**params)
        else:
            pool.submit(generate_md_with_adj_factor, **params)

    if pool is not None:
        pool.shutdown(wait=True)


def _run_generate_adj_md():
    instrument_types = None
    # instrument_types = ['v']  # test only
    # instrument_types = [
    #     'rb', 'hc', 'i', 'j', 'jm', 'ru', 'bu', 'ma', 'cu', 'fg', 'jd',
    #     'ap', 'cj', 'a', 'b', 'm', 'oi', 'y', 'rm', 'p', 'rs', 'sr', 'cf'
    # ]
    # adj_factor_dir = r'D:\github\data_integration_celery\tasks\wind\future_reorg\output\2021-01-13'
    # adj_factor_dir = r'd:\github\data_integration_celery\output\2021-01-13'
    table_name = 'wind_future_adj_factor'
    generate_adj_md(
        instrument_types,
        # adj_factor_dir=adj_factor_dir,
        table_name=table_name,
        method_filter=Method.division,
        # until_instrument_type='V',
        pool_size=0,
        # incrementally=False,
    )


def get_all_instrument_type_by_dir(adj_factor_dir):
    files = os.listdir(adj_factor_dir)
    instrument_type_set = set()
    for file_name in files:
        name, ext = os.path.splitext(file_name)
        if ext != '.csv' or not name.startswith('adj_factor_'):
            continue
        instrument_type, method = name.replace('adj_factor_', '').split('_')
        instrument_type_set.add(instrument_type)

    instrument_types = list(instrument_type_set)
    instrument_types.sort()
    return instrument_types


if __name__ == "__main__":
    # _test_generate_md_with_adj_factor()
    _run_generate_adj_md()
