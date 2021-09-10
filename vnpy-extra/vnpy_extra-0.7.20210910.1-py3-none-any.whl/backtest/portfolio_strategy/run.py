#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2020/10/28 8:42
@File    : run.py
@contact : mmmaaaggg@163.com
@desc    : 基于 portfolio 的投资策略回测
"""
from enum import Enum
from multiprocessing import Lock
from typing import Type, Union, Optional, List, Callable, Tuple, Dict

from vnpy.app.portfolio_strategy import StrategyTemplate

from vnpy_extra.backtest import CrossLimitMethod, DuplicateNameOptions
from vnpy_extra.backtest.commons import run_backtest as run_backtest_pub, bulk_backtest as bulk_backtest_pub
from vnpy_extra.config import logging
from vnpy_extra.db.orm import StrategyBacktestStats

logger = logging.getLogger(__name__)
HAS_PANDAS_EXCEPTION = False


def run_backtest(
        strategy_class: Type[StrategyTemplate],
        engine_kwargs: dict,
        strategy_kwargs: Optional[dict] = None,
        root_folder_name=None,
        file_name_header=None,
        engine=None,
        output_available_only=False,
        output_trades=False,
        output_orders=False,
        open_browser_4_charts=False,
        log_statistic_markdown=False,
        show_indexes=None,
        print_statistics=True,
        lock: Optional[Lock] = None,
        enable_collect_data=False,
        save_stats: Optional[bool] = None,
        strategy_stats_original: Optional[StrategyBacktestStats] = None,
        enable_join_collector=True,
        ignore_existed_backtest=False,
        output_path_has_strategy_class_name=True,
        output_separate_by_backtest_status=False,
        generate_setting_json_file=False,
        file_name_include_symbol=False,
        stg_info_duplicate_name_options=DuplicateNameOptions.raise_error,
) -> dict:
    """
    本地化运行策略回测程序
    :param strategy_class 策略类
    :param engine_kwargs 回测引擎参数，或者回测引擎参数列表
    :param strategy_kwargs 策略类 参数数组字典,key为参数名称, value 为数组
    :param file_name_header 自定义文件头名称，默认为None，所有["参数名+参数", ...]用下划线链接
    :param engine 回测引擎
    :param output_available_only 仅当策略有效是才输出统计数据、图片、参数等文件
    :param output_trades 输出交易数据到 csv 文件（不受 output_available_only 影响）
    :param output_orders 输出订单数据到 csv 文件（不受 output_available_only 影响）
    :param open_browser_4_charts
    :param root_folder_name 策略类 保存跟目录名称,None 时为当前系统日期
    :param log_statistic_markdown Markdown 格式记录统计数据
    :param show_indexes 展示指标
    :param print_statistics 输出统计结果
    :param lock 进程锁
    :param enable_collect_data 是否运行收集数据
    :param save_stats 保存统计数据，默认情况下只记录 CrossLimitMethod.open_price 的回测结果数据
    :param strategy_stats_original 此前回测的统计数据对象
    :param enable_join_collector 是否交易结束后关闭 collector
    :param ignore_existed_backtest 默认为False.是否忽略以及存在的回测.即,如果当前回测在数据库中已经存在,则跳过该测试.
    :param output_path_has_strategy_class_name 默认为False.输出文件路径是否包含 策略类名称.
    :param output_separate_by_backtest_status 默认为False.输出文件路径是否包含按 backtest_status 分目录存放.
    :param generate_setting_json_file 生成 setting json 文件
    :param file_name_include_symbol 生成文件的文件名带 symbol 用以进行区分，默认False，过长文件名可能导致系统不支持长文件名错误。
    :param stg_info_duplicate_name_options 默认 DuplicateNameOptions.raise_error。策略重名应对措施。该参数仅在 save_stats == True 的情况下启用
    """
    return run_backtest_pub(
        strategy_class=strategy_class,
        multi_symbols=True,
        engine_kwargs=engine_kwargs,
        strategy_kwargs=strategy_kwargs,
        root_folder_name=root_folder_name,
        file_name_header=file_name_header,
        engine=engine,
        output_available_only=output_available_only,
        output_trades=output_trades,
        output_orders=output_orders,
        open_browser_4_charts=open_browser_4_charts,
        log_statistic_markdown=log_statistic_markdown,
        show_indexes=show_indexes,
        print_statistics=print_statistics,
        lock=lock,
        save_stats=save_stats,
        strategy_stats_original=strategy_stats_original,
        enable_join_collector=enable_join_collector,
        enable_collect_data=enable_collect_data,
        ignore_existed_backtest=ignore_existed_backtest,
        output_path_has_strategy_class_name=output_path_has_strategy_class_name,
        output_separate_by_backtest_status=output_separate_by_backtest_status,
        generate_setting_json_file=generate_setting_json_file,
        file_name_include_symbol=file_name_include_symbol,
        stg_info_duplicate_name_options=stg_info_duplicate_name_options,
    )


def _run_backtest():
    from vnpy_extra.constants import GeneralPeriodEnum
    from vnpy.trader.constant import Interval
    from datetime import datetime
    from strategies.pair_trading_strategy import PairTradingTargetPosStrategy4Test

    engine_kwargs = dict(
        vt_symbols=["RB9999.SHFE", "HC9999.SHFE"],
        interval=Interval.MINUTE,
        start=datetime(2020, 1, 1),
        end=datetime(2022, 1, 1),
        rates={"RB9999.SHFE": 2.5e-04, "HC9999.SHFE": 2.5e-04},
        slippages={"RB9999.SHFE": 0, "HC9999.SHFE": 0},
        sizes={"RB9999.SHFE": 10, "HC9999.SHFE": 10},
        priceticks={"RB9999.SHFE": 1, "HC9999.SHFE": 1},
        capital=100000,
        cross_limit_method=CrossLimitMethod.open_price,
    )
    strategy_param_dic = {
        'period_enum': GeneralPeriodEnum.h1.name
    }
    run_backtest(PairTradingTargetPosStrategy4Test,
                 engine_kwargs=engine_kwargs,
                 strategy_kwargs=strategy_param_dic,
                 open_browser_4_charts=False,
                 output_available_only=False,
                 output_trades=False,
                 output_orders=False,
                 save_stats=True,
                 )


def _run_backtest_futures_2_options():
    from vnpy.trader.constant import Interval
    from datetime import datetime

    engine_kwargs = dict(
        vt_symbols=["MA9999.CZCE", "MA2101-C-1975.DCE", "MA2101-P-1975.DCE"],
        interval=Interval.MINUTE,
        start=datetime(2020, 1, 1),
        end=datetime(2021, 1, 1),
        cross_limit_method=CrossLimitMethod.open_price,
    )
    strategy_param_dic = {
        "period_enum": "h1",
        "win_size": 20,
        "reverse_bs": 0,
        "ma_price_type": "close",
        "same_direction": False,
        "cross_price_type": "close",
        "filter_n_available": 0
    }
    from strategies.futures_2_options import MacpMacmaPrAndFutures2Options
    run_backtest(MacpMacmaPrAndFutures2Options,
                 engine_kwargs=engine_kwargs,
                 strategy_kwargs=strategy_param_dic,
                 open_browser_4_charts=False,
                 output_available_only=False,
                 output_trades=False,
                 output_orders=False,
                 save_stats=False,
                 )


def default_engine_param_key_func(**kwargs) -> Optional[Tuple[str]]:
    """
    将 engine_kwargs 生成一个默认的 key
    处于常用案例考虑，当前key不考虑起止时间、interval。
    如果需要进行key处理，需要单独写相应的函数
    """
    keys = ["vt_symbols", "rates", "slippages", "sizes", "priceticks", "cross_limit_method"]
    vt_symbols = kwargs["vt_symbols"]
    rets = []
    for key in keys:
        if key not in kwargs:
            continue
        value = kwargs[key]
        if isinstance(value, list):
            rets.append('_'.join([str(_) for _ in value]))
        elif isinstance(value, dict):
            rets.append("_".join([str(value[_]) for _ in vt_symbols]))
        elif isinstance(value, Enum):
            rets.append(str(value.name))
        else:
            raise ValueError(f"{value} 不支持")

    ret = tuple(rets)
    return ret


def bulk_backtest(
        strategy_cls: Type[StrategyTemplate],
        engine_param_dic_list: Union[dict, List[dict]],
        strategy_param_dic_list: Union[Dict[str, list], List[Dict[str, list]]],
        available_backtest_params_check_func: Optional[Callable] = None,
        file_name_func: Optional[Callable] = None,
        statistic_item_dic: Optional[dict] = None,
        engine_param_key_func: Callable = default_engine_param_key_func,
        output_available_only: bool = True,
        open_browser_4_charts: bool = False,
        root_folder_name: Optional[str] = None,
        multi_process: int = 0,
        save_stats: Optional[bool] = None,
        enable_collect_data=False,
        ignore_existed_backtest=False,
        output_path_has_strategy_class_name=True,
        output_separate_by_backtest_status=False,
        generate_setting_json_file=False,
        file_name_include_symbol=False,
        stg_info_duplicate_name_options=DuplicateNameOptions.raise_error,
):
    """
    :param strategy_cls 策略类
    :param engine_param_dic_list 回测引擎参数，或者回测引擎参数列表
    :param strategy_param_dic_list 策略类 参数数组字典,key为参数名称, value 为数组
    :param available_backtest_params_check_func 如果希望忽略部分参数组合，可以自定义函数，对每一个组合进行筛选，False为忽略该参数
    :param file_name_func 自定义文件头名称，默认为None，所有["参数名+参数", ...]用下划线链接
    :param statistic_item_dic 策略类 统计项默认 DEFAULT_STATIC_ITEM_DIC
    :param engine_param_key_func engine param key
    :param output_available_only
    :param open_browser_4_charts
    :param root_folder_name 策略类 保存跟目录名称,None 时为当前系统日期
    :param multi_process 0 单进程, -1 为CPU数量,正数为对应的进程数
    :param save_stats 保存统计数据，默认情况下只记录 CrossLimitMethod.open_price 的回测结果数据
    :param enable_collect_data 是否运行收集数据
    :param ignore_existed_backtest 默认为False.是否忽略以及存在的回测.即,如果当前回测在数据库中已经存在,则跳过该测试.
    :param output_path_has_strategy_class_name 默认为False.输出文件路径是否包含 策略类名称.
    :param output_separate_by_backtest_status 默认为False.输出文件路径是否包含按 backtest_status 分目录存放.
    :param generate_setting_json_file 生成 setting json 文件
    :param file_name_include_symbol 生成文件的文件名带 symbol 用以进行区分，默认False，过长文件名可能导致系统不支持长文件名错误。
    :param stg_info_duplicate_name_options 默认 DuplicateNameOptions.raise_error。策略重名应对措施。该参数仅在 save_stats == True 的情况下启用
    """
    return bulk_backtest_pub(
        strategy_cls=strategy_cls,
        multi_symbols=True,
        engine_param_dic_list=engine_param_dic_list,
        strategy_param_dic_list=strategy_param_dic_list,
        available_backtest_params_check_func=available_backtest_params_check_func,
        file_name_func=file_name_func,
        statistic_item_dic=statistic_item_dic,
        engine_param_key_func=engine_param_key_func,
        output_available_only=output_available_only,
        open_browser_4_charts=open_browser_4_charts,
        root_folder_name=root_folder_name,
        multi_process=multi_process,
        save_stats=save_stats,
        enable_collect_data=enable_collect_data,
        ignore_existed_backtest=ignore_existed_backtest,
        output_path_has_strategy_class_name=output_path_has_strategy_class_name,
        output_separate_by_backtest_status=output_separate_by_backtest_status,
        generate_setting_json_file=generate_setting_json_file,
        file_name_include_symbol=file_name_include_symbol,
        stg_info_duplicate_name_options=stg_info_duplicate_name_options,
    )


def _run_bulktest():
    from datetime import datetime
    from strategies.pair_trading_strategy import PairTradingStrategy4Test

    engine_param_dic_list = [
        dict(
            vt_symbols=["RB9999.SHFE", "HC9999.SHFE"],
            start=datetime(2017, 1, 1),
            end=datetime(2022, 1, 1),
            rates={"RB9999.SHFE": 2.5e-04, "HC9999.SHFE": 2.5e-04},
            slippages={"RB9999.SHFE": 0, "HC9999.SHFE": 0},
        ),
        dict(
            vt_symbols=["RB9999.SHFE", "HC9999.SHFE"],
            start=datetime(2017, 1, 1),
            end=datetime(2022, 1, 1),
            rates={"RB9999.SHFE": 2.5e-04, "HC9999.SHFE": 2.5e-04},
            slippages={"RB9999.SHFE": 0, "HC9999.SHFE": 0},
            cross_limit_method=CrossLimitMethod.mid_price,
        ),
        dict(
            vt_symbols=["RB9999.SHFE", "HC9999.SHFE"],
            start=datetime(2017, 1, 1),
            end=datetime(2022, 1, 1),
            rates={"RB9999.SHFE": 2.5e-04, "HC9999.SHFE": 2.5e-04},
            slippages={"RB9999.SHFE": 0, "HC9999.SHFE": 0},
            cross_limit_method=CrossLimitMethod.worst_price,
        ),
    ]
    strategy_param_dic_list = [
        {"boll_dev": [1, 1.5, 2, 2.5, 3]}
    ]

    # def file_name_func(engine_kwargs, strategy_kwargs, **kwargs):
    #     if "cross_limit_method" in engine_kwargs:
    #         method_value = engine_kwargs["cross_limit_method"].value
    #     else:
    #         method_value = CrossLimitMethod.open_price.value
    #
    #     file_name_header = f'boll_dev{strategy_kwargs["boll_dev"]}_{method_value}'
    #     return file_name_header

    bulk_backtest(
        PairTradingStrategy4Test,
        engine_param_dic_list=engine_param_dic_list,
        strategy_param_dic_list=strategy_param_dic_list,
        # file_name_func=file_name_func,
        open_browser_4_charts=False,
        multi_process=2,
        root_folder_name='test',
        output_available_only=False,
        file_name_include_symbol=False,
    )


if __name__ == "__main__":
    # _run_backtest()
    _run_backtest_futures_2_options()
    # _run_bulktest()
