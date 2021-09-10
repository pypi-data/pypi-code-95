"""
@author  : MG
@Time    : 2021/1/20 9:31
@File    : track_performance.py
@contact : mmmaaaggg@163.com
@desc    : 用于对有效策略每日持续更新绩效表现
"""
import json
import logging
import os
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from typing import List, Dict, Tuple, Iterator, Optional

import numpy as np
import pandas as pd
from ibats_utils.mess import load_class, get_first
from ibats_utils.transfer import str_2_date
from tqdm import tqdm
from vnpy.trader.constant import Interval

from vnpy_extra.backtest import CrossLimitMethod
from vnpy_extra.backtest.commons import bulk_backtest_with_backtest_params_iter, set_default_root_folder_name, \
    run_backtest
from vnpy_extra.backtest.cta_strategy.engine import BacktestingEngine as CtaBacktestingEngine
from vnpy_extra.backtest.portfolio_strategy.engine import BacktestingEngine as PortfolioBacktestingEngine
from vnpy_extra.config import set_log_level
from vnpy_extra.constants import BASE_POSITION, STOP_OPENING_POS_PARAM
from vnpy_extra.db.orm import StrategyBacktestStats, StrategyBacktestStatsArchive, StrategyInfo, SymbolsInfo

logger = logging.getLogger(__name__)


def get_backtest_params_iter_from_stats_list(
        stats_list: List[StrategyBacktestStats], start: Optional[str] = None, end: Optional[str] = None
) -> Tuple[List[str], Iterator[Tuple[dict, list, StrategyBacktestStats]]]:
    """
    整理 StrategyBacktestStats 列表，重新设置回测日期区间，返回参数名称及 回测引擎及参数迭代器
    """
    param_name_list = None
    engine_kwargs_list, param_values_list = [], []
    for stats in stats_list:
        if stats.strategy_settings is None:
            stats.strategy_settings = {}

        if param_name_list is None:
            param_name_list = list(stats.strategy_settings.keys())

        engine_kwargs = stats.engine_kwargs
        # 2021-07-05 发现部分情况下 engine_kwargs 中 symbol 与 stats.symbols_info.symbols 不一致，以后者为准
        if 'vt_symbol' in engine_kwargs:
            vt_symbol_key = 'vt_symbol'
            is_mutiple = False
        else:
            vt_symbol_key = 'vt_symbols'
            is_mutiple = True

        symbols_info: SymbolsInfo = stats.symbols_info
        if engine_kwargs[vt_symbol_key] != symbols_info.symbols:
            logger.warning(
                f"{stats} engine_kwargs['{vt_symbol_key}']={engine_kwargs[vt_symbol_key]} "
                f"与 stats.symbols_info.symbols={symbols_info.symbols} 不一致，以后者为准")
            engine_kwargs[vt_symbol_key] = symbols_info.symbols

        if is_mutiple:
            # 将 B2109.DCE_B2110.DCE 转换为 ["B2109.DCE","B2110.DCE"] 的形式
            engine_kwargs[vt_symbol_key] = engine_kwargs[vt_symbol_key].split("_")

        # 整理回测日期区间
        engine_kwargs['end'] = end = date.today() if end is None else str_2_date(end)
        engine_kwargs['start'] = (end - timedelta(days=365 * 5)) if start is None else str_2_date(start)
        engine_kwargs['cross_limit_method'] = CrossLimitMethod(stats.cross_limit_method)
        if 'interval' in engine_kwargs:
            interval = engine_kwargs['interval']
            engine_kwargs['interval'] = Interval(interval) if interval is not None else Interval.MINUTE
        engine_kwargs_list.append(engine_kwargs)

        # 整理策略参数
        param_values = []
        for param_name in param_name_list:
            strategy_settings = stats.strategy_settings
            if param_name == BASE_POSITION:
                param_values.append(1)
            elif param_name == STOP_OPENING_POS_PARAM:
                param_values.append(0)
            else:
                param_values.append(strategy_settings.get(param_name, None))

        param_values_list.append(param_values)

    return param_name_list, zip(engine_kwargs_list, param_values_list, stats_list)


def backtest_all_strategies(
        symbols_list=None, strategy_class_name_list=None, root_folder_name=None, author_list=None,
        user_name_broker_id_pair_list: Optional[List[Tuple[str, str]]] = None, pool_size=3,
        output_path_has_strategy_class_name=False, start: Optional[str] = None, end: Optional[str] = None,
        generate_setting_json_file=False, file_name_include_symbol=False,
        ignore_backtest_in_n_days=0.5,
):
    """
    每日策略自动回测。所有参数均为可选输入项 None
    :param symbols_list: 合约列表
    :param strategy_class_name_list: 类名称列表
    :param root_folder_name: 根目录
    :param author_list: 作者列表
    :param user_name_broker_id_pair_list:
    :param pool_size: 是否使用进程池，<=1代表单进程
    :param output_path_has_strategy_class_name:是否输出目录中带策略类名称
    :param start: 起始日期
    :param end: 截止日期
    :param generate_setting_json_file 生成 setting json 文件
    :param file_name_include_symbol 生成文件的文件名带 symbol 用以进行区分，默认False，过长文件名可能导致系统不支持长文件名错误。
    :param ignore_backtest_in_n_days 忽略一天之内的回测（避免重复回测）。
    :return:
    """
    set_default_root_folder_name(root_folder_name)
    stats_list_dic, stats_count = StrategyBacktestStats.get_available_status_group_by_strategy(
        symbols_list=symbols_list, strategy_class_name_list=strategy_class_name_list,
        user_name_broker_id_pair_list=user_name_broker_id_pair_list,
        ignore_backtest_in_n_days=ignore_backtest_in_n_days,
    )
    StrategyBacktestStatsArchive.archive(stats_list_dic)
    if stats_count <= 1:
        pool_size = 0

    if pool_size <= 1:
        pool = None
    else:
        pool = ThreadPoolExecutor(max_workers=pool_size, thread_name_prefix="backtest_")

    count = len(stats_list_dic)
    logger.info(f"总计 {count} 个[策略类/品种]组合， {stats_count:,d} 个策略将被回测")
    for num, ((module_name, strategy_class_name, symbols), stats_list) in enumerate(stats_list_dic.items(), start=1):
        try:
            strategy_cls = load_class(module_name, strategy_class_name)
        except ModuleNotFoundError:
            logger.warning(f"{module_name}.{strategy_class_name} 不存在，模块名称错误，忽略")
            continue
        except AttributeError:
            logger.warning(f"{module_name}.{strategy_class_name} 不存在，类名称错误，忽略")
            continue
        if author_list is not None and getattr(strategy_cls, 'author', None) not in author_list:
            continue

        multi_symbols = len(symbols.split('_')) > 1
        if multi_symbols:
            from vnpy_extra.backtest.portfolio_strategy.run import default_engine_param_key_func
        else:
            from vnpy_extra.backtest.cta_strategy.run import default_engine_param_key_func

        param_name_list, backtest_params_iter = get_backtest_params_iter_from_stats_list(stats_list, start, end)
        bulk_backtest_kwargs = dict(
            strategy_cls=strategy_cls,
            multi_symbols=multi_symbols,
            param_name_list=param_name_list,
            backtest_params_iter=backtest_params_iter,
            engine_param_key_func=default_engine_param_key_func,
            output_available_only=False,
            open_browser_4_charts=False,
            save_stats=True,
            enable_collect_data=False,
            output_path_has_strategy_class_name=output_path_has_strategy_class_name,
            output_separate_by_backtest_status=True,
            generate_setting_json_file=generate_setting_json_file,
            file_name_include_symbol=file_name_include_symbol,
        )
        if pool_size <= 1:
            try:
                logger.info(f"{num}/{count}) {strategy_class_name} on {symbols} {len(stats_list)} 个策略将被回测")
                bulk_backtest_with_backtest_params_iter(**bulk_backtest_kwargs)
            except:
                logging.exception("%s 追踪回测异常", strategy_cls.__name__)

        else:
            future = pool.submit(bulk_backtest_with_backtest_params_iter, **bulk_backtest_kwargs)

    if pool is not None:
        pool.shutdown(wait=True)


def backtest_by_warning_log(log_file_path, xls_dir, encoding='utf-8', output_path_has_strategy_class_name=True):
    """更加日至中 '没有找到对应的记录' 的警告日志对当前测试进行补充测试，并将测试结果补充到数据库，同时，调整相应状态"""
    folder_name_list = os.listdir(xls_dir)
    # 读 log 寻找 WARNING *** 没有找到对应的记录 的记录，并将 策略类名称，合约名称，id_name 记录下来
    pattern = re.compile(r'WARNING (\w+) \[([\w\.]+)\] <(\w+)> 没有找到对应的记录')
    stg_cls_vt_symbol_id_name_tuple_xls_name_dic: Dict[Tuple[str, str, str], str] = {}
    with open(log_file_path, 'r', encoding=encoding) as f:
        line_str = f.readline()
        while line_str != "":
            ret = pattern.search(line_str)
            if ret is not None:
                stg_cls_vt_symbol_id_name_tuple: Tuple[str, str, str] = ret.groups()
                cls_name, vt_symbol, id_name = stg_cls_vt_symbol_id_name_tuple
                xls_name_header = f'{cls_name}_{vt_symbol}'
                # 从 xlsx 目录中找到相应的文件
                xls_name = get_first(folder_name_list, lambda x: x.startswith(xls_name_header))
                if xls_name is None:
                    logger.warning("%s 没有找的对应的文件，对应 id_name=%s", xls_name_header, id_name)
                else:
                    stg_cls_vt_symbol_id_name_tuple_xls_name_dic[stg_cls_vt_symbol_id_name_tuple] = xls_name

            line_str = f.readline()

    # get_cls_module_dic
    cls_module_dic = StrategyInfo.get_cls_module_dic()
    # 建立engine dic
    xls_df_dict = {}
    # 针对每一条 stg_cls, vt_symbol, id_name tuple 进行循环
    backtest_params_iter = tqdm(
        enumerate(stg_cls_vt_symbol_id_name_tuple_xls_name_dic.items()),
        total=len(stg_cls_vt_symbol_id_name_tuple_xls_name_dic),
    )
    # 回测统计结果列表
    data_dic_list = []
    # engine 列表
    engine_dic = {}
    for num, ((strategy_class_name, vt_symbol, id_name), xls_name) in backtest_params_iter:
        # 打开 xlsx 文件 找到相应的 记录
        if xls_name not in xls_df_dict:
            xls_df_dict[xls_name] = df = pd.read_excel(os.path.join(xls_dir, xls_name), index_col='id_name')
        else:
            df = xls_df_dict[xls_name]
        if id_name not in df.index:
            logger.warning("%s %s %s 在 %s 中没有找到相应记录", strategy_class_name, vt_symbol, id_name, xls_name)
            continue
        record: pd.Series = df.loc[id_name, :]
        # 读取相应参数，并整理成dic 同时记录 backtest_status 加入回测列表
        multi_symbols = vt_symbol.find('_') >= 0
        strategy_kwargs = {}
        # 构建 strategy_kwargs
        for key, value in record.items():
            if key == '新高周期':
                break
            if isinstance(value, np.int64) or isinstance(value, np.int32):
                value = int(value)
            elif isinstance(value, np.float64) or isinstance(value, np.float32) or isinstance(value, np.float16):
                value = float(value)
            strategy_kwargs[key] = value

        backtest_status_from_xls = record['backtest_status']
        short_name = record['short_name']
        shown_name = record['shown_name']
        cross_limit_method = CrossLimitMethod(record['cross_limit_method'])
        if backtest_status_from_xls == 0:
            logger.warning("%s %s %s backtest_status == 0 无需回测", strategy_class_name, vt_symbol, id_name)
            continue

        # 建立相应 engine
        if multi_symbols not in engine_dic:
            engine_dic[
                multi_symbols] = engine = PortfolioBacktestingEngine() if multi_symbols else CtaBacktestingEngine()
        else:
            engine = engine_dic[multi_symbols]

        # 建立 engine_kwargs
        if multi_symbols:
            engine_kwargs = {
                "vt_symbols": vt_symbol.split('_'),
                "cross_limit_method": cross_limit_method,
            }
        else:
            engine_kwargs = {
                "vt_symbol": vt_symbol,
                "cross_limit_method": cross_limit_method,
            }

        # 逐条回测
        strategy_cls = StrategyInfo.get_strategy_class_by_name(strategy_class_name)
        statistics = run_backtest(
            strategy_cls,
            multi_symbols,
            engine_kwargs,
            strategy_kwargs,
            engine=engine,
            save_stats=True,
            output_path_has_strategy_class_name=output_path_has_strategy_class_name,
        )

        if statistics is None:
            continue
        backtest_status = statistics.setdefault('backtest_status', 0)
        # 如果回测状态 backtest_status == 0 且 backtest_status_from_xls > 0 则需要更新状态，否则直接跳过
        if not (backtest_status == 0 and backtest_status_from_xls > 0):
            continue

        statistics['backtest_status'] = backtest_status_from_xls
        if statistics.setdefault('short_name', short_name) is None:
            statistics['short_name'] = short_name

        if statistics.setdefault('shown_name', shown_name) is None:
            statistics['shown_name'] = shown_name

        data_dic_list.append(statistics)
        id_name_new = statistics['id_name']
        if id_name_new != id_name:
            logger.warning(f"{strategy_class_name} {vt_symbol} {id_name} -> {id_name_new} 状态将被修改 "
                           f"{backtest_status} -> {backtest_status_from_xls}")
        else:
            logger.warning(f"{strategy_class_name} {vt_symbol} {id_name} 状态将被修改 "
                           f"{backtest_status} -> {backtest_status_from_xls}")

    StrategyBacktestStats.update_backtest_status_bulk(data_dic_list)


def get_param_iter_from_settings_dic(settings_dic: dict, start: Optional[str] = None, end: Optional[str] = None):
    """生成回测参数列表"""
    class_name_settings_dic = defaultdict(list)
    for _, setting_dic in settings_dic.items():
        strategy_class_name = setting_dic["class_name"]
        class_name_settings_dic[strategy_class_name].append(setting_dic)

    for strategy_class_name, setting_dic_list in class_name_settings_dic.items():
        try:
            strategy_cls = StrategyInfo.get_strategy_class_by_name(strategy_class_name)
        except:
            logger.exception(f"{strategy_class_name} 没找到")
            continue

        param_name_list = None
        engine_kwargs_list, param_values_list, stats_list = [], [], []
        multi_symbols = False
        engine_param_key_func = None
        for setting_dic in setting_dic_list:
            strategy_kwargs = setting_dic["setting"]
            if param_name_list is None:
                param_name_list = [_ for _ in strategy_kwargs.keys() if _ != 'class_name']

            if "vt_symbol" in setting_dic:
                from vnpy_extra.backtest.cta_strategy.run import \
                    default_engine_param_key_func as cta_engine_param_key_func
                multi_symbols = False
                vt_symbol = setting_dic["vt_symbol"]
                engine_kwargs = {
                    "vt_symbol": vt_symbol,
                    "cross_limit_method": CrossLimitMethod.open_price,
                }
                engine_param_key_func = cta_engine_param_key_func
            else:
                from vnpy_extra.backtest.portfolio_strategy.run import \
                    default_engine_param_key_func as portfolio_engine_param_key_func
                multi_symbols = True
                vt_symbol = setting_dic["vt_symbols"]
                engine_kwargs = {
                    "vt_symbols": vt_symbol.split('_'),
                    "cross_limit_method": CrossLimitMethod.open_price,
                }
                engine_param_key_func = portfolio_engine_param_key_func

            if start:
                engine_kwargs['start'] = start
            if end:
                engine_kwargs['end'] = end or date.today()

            strategy_kwargs = setting_dic["setting"]
            engine_kwargs_list.append(engine_kwargs)
            param_values_list.append([strategy_kwargs.get(_, None) for _ in param_name_list])
            stats_list.append(None)

        if len(engine_kwargs_list) == 0:
            continue

        yield dict(
            strategy_cls=strategy_cls,
            multi_symbols=multi_symbols,
            param_name_list=param_name_list,
            backtest_params_iter=zip(engine_kwargs_list, param_values_list, stats_list),
            engine_param_key_func=engine_param_key_func,
        )


def backtest_by_json(json_file_path, pool_size=0,
                     output_path_has_strategy_class_name=False, start: Optional[str] = None, end: Optional[str] = None,
                     generate_setting_json_file=False, file_name_include_symbol=False, output_available_only=False):
    """
    更加 json 文件进行策略回测
    :param json_file_path:
    :param pool_size:
    :param output_path_has_strategy_class_name:是否输出目录中带策略类名称
    :param start: 起始日期
    :param end: 截止日期
    :param generate_setting_json_file 生成 setting json 文件
    :param file_name_include_symbol 生成文件的文件名带 symbol 用以进行区分，默认False，过长文件名可能导致系统不支持长文件名错误。
    :param output_available_only 仅当策略有效是才输出统计数据、图片、参数等文件
    :return:
    """
    with open(json_file_path) as fp:
        settings_dic = json.load(fp)
    count = len(settings_dic)
    if count <= 1:
        pool_size = 0

    if pool_size <= 1:
        pool = None
    else:
        pool = ThreadPoolExecutor(max_workers=pool_size, thread_name_prefix="backtest_")

    for bulk_backtest_kwargs in get_param_iter_from_settings_dic(settings_dic, start=start, end=end):
        bulk_backtest_kwargs.update(dict(
            save_stats=True,
            output_path_has_strategy_class_name=output_path_has_strategy_class_name,
            generate_setting_json_file=generate_setting_json_file,
            file_name_include_symbol=file_name_include_symbol,
            output_available_only=output_available_only,
            enable_collect_data=False,
            open_browser_4_charts=False,
            short_name_with_file_name_if_exist=False,
        ))
        if pool_size <= 1:
            try:
                bulk_backtest_with_backtest_params_iter(**bulk_backtest_kwargs)
            except:
                logging.exception("%s 追踪回测异常", bulk_backtest_kwargs["strategy_cls"].__name__)

        else:
            future = pool.submit(bulk_backtest_with_backtest_params_iter, **bulk_backtest_kwargs)

    if pool is not None:
        pool.shutdown(wait=True)


def _test_backtest_by_json():
    json_file_path = r"D:\github\vnpy_extra\vnpy_extra\backtest\cta_strategy\test_settings.json"
    backtest_by_json(json_file_path=json_file_path)


def run_backtest_all_strategies():
    backtest_all_strategies(
        # strategy_class_name_list=['DoubleMA4Test'],
        # symbols_list=['rb9999.shfe', 'hc9999.shfe'],
        author_list={'MG'},
        pool_size=0,
        # user_name_broker_id_pair_list=[('11859087', '95533')],
    )


def run_backtest_all_strategies_after_refresh(
        symbols_list=None, strategy_class_name_list=None, user_name_broker_id_pair_list=None,
        refresh_vt_symbol=True, author_list=None, pool_size=None, ignore_backtest_in_n_days=1,
        generate_setting_json_file=True, log_level='info',
):
    """追踪回测功能的集成封装方法，回测前线刷新一下策略列表更新到最新合约"""
    set_log_level(log_level)
    if not user_name_broker_id_pair_list:
        user_name_broker_id_pair_list = []
    # strategy_class_name_list = ['SF32_long_runner']
    # symbols_list = ['V9999.DCE', 'V2201.DCE']
    # user_name_broker_id_pair_list: List[Tuple[str, str]] = [
    #     (*AccountListEnum.JX_11859087.value[:2],),
    #     (*AccountListEnum.QH_MK_721018.value[:2],),
    #     (*AccountListEnum.QH_YA_201010217.value[:2],),
    # ]
    if refresh_vt_symbol and user_name_broker_id_pair_list:
        from vnpy_extra.db.export_strategy_setting import refresh_vt_symbol_2_curr_contract_by_account
        for user_name, broker_id in user_name_broker_id_pair_list:
            refresh_vt_symbol_2_curr_contract_by_account(user_name, broker_id)
    try:
        backtest_all_strategies(
            symbols_list=symbols_list,
            strategy_class_name_list=strategy_class_name_list,
            user_name_broker_id_pair_list=user_name_broker_id_pair_list,
            author_list=author_list,
            pool_size=pool_size,
            generate_setting_json_file=generate_setting_json_file,
            ignore_backtest_in_n_days=ignore_backtest_in_n_days,
        )
    except:
        logging.exception("追踪回测异常")


if __name__ == "__main__":
    run_backtest_all_strategies()
    # _test_backtest_by_json()
