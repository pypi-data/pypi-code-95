"""
@author  : MG
@Time    : 2020/10/9 12:01
@File    : run.py
@contact : mmmaaaggg@163.com
@desc    : 用于对策略进行回测
"""
from datetime import date
from enum import Enum
from multiprocessing import Lock
from typing import Type, Union, Optional, List, Callable, Tuple, Dict

from ibats_utils.mess import str_2_date
from vnpy.app.cta_strategy import CtaTemplate
from vnpy.trader.constant import Interval

from vnpy_extra.backtest import CrossLimitMethod, VT_SYMBOL_LIST_ALL, DuplicateNameOptions
from vnpy_extra.backtest.commons import run_backtest as run_backtest_pub, bulk_backtest as bulk_backtest_pub
from vnpy_extra.backtest.cta_strategy.template import AllowTradeDirectionEnum
from vnpy_extra.config import logging

logger = logging.getLogger(__name__)
HAS_PANDAS_EXCEPTION = False


def run_backtest(
        strategy_class: Type[CtaTemplate],
        engine_kwargs: dict,
        strategy_kwargs: Optional[dict] = None,
        root_folder_name=None,
        file_name_header="",
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
    :param generate_setting_json_file 生成 setting json 文件
    :param file_name_include_symbol 生成文件的文件名带 symbol 用以进行区分，默认False，过长文件名可能导致系统不支持长文件名错误。
    :param stg_info_duplicate_name_options 默认 DuplicateNameOptions.raise_error。策略重名应对措施。该参数仅在 save_stats == True 的情况下启用
    """
    return run_backtest_pub(
        strategy_class=strategy_class,
        multi_symbols=False,
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
        enable_collect_data=enable_collect_data,
        save_stats=save_stats,
        generate_setting_json_file=generate_setting_json_file,
        file_name_include_symbol=file_name_include_symbol,
        stg_info_duplicate_name_options=stg_info_duplicate_name_options,
    )


def _run_backtest():
    from strategies.double_ma_strategy import DoubleMATargetPosNoStopOrder4Test
    allow_trade_direction = AllowTradeDirectionEnum.LONG_ONLY.value
    strategy_kwargs = dict(
        stop_loss_rate=0.01,
        trailing_stop_rate=0.01,
        # allow_trade_direction=allow_trade_direction,
    )
    engine_kwargs = dict(
        vt_symbol="RB9999.SHFE",
        interval=Interval.MINUTE,
        start=date(2020, 1, 1),
        # rate=2.5e-4,
        # slippage=1,
        # size=10,
        # pricetick=1,
        # capital=100000,
        end=date(2022, 1, 1),
        cross_limit_method=CrossLimitMethod.open_price,
    )
    run_backtest(
        DoubleMATargetPosNoStopOrder4Test,
        strategy_kwargs=strategy_kwargs,
        engine_kwargs=engine_kwargs,
        open_browser_4_charts=False,
        output_trades=False,
        output_orders=False,
        print_statistics=True,
        save_stats=True,
        generate_setting_json_file=False,
        file_name_include_symbol=True,
    )


def default_engine_param_key_func(**kwargs) -> Optional[Tuple[str]]:
    """
    将 engine_kwargs 生成一个默认的 key
    处于常用案例考虑，当前key不考虑起止时间、interval。
    如果需要进行key处理，需要单独写相应的函数
    """
    keys = ["vt_symbol", "rate", "slippage", "size", "pricetick", "cross_limit_method"]
    rets = []
    for key in keys:
        if key not in kwargs:
            continue
        value = kwargs[key]
        if isinstance(value, list):
            rets.append('_'.join([str(_) for _ in value]))
        elif isinstance(value, Enum):
            rets.append(str(value.name))
        else:
            rets.append(str(value))

    ret = tuple(rets)
    return ret


def bulk_backtest(
        strategy_cls: Type[CtaTemplate],
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
    :param ignore_existed_backtest 默认为False.是否忽略以及存在的回测.即,如果当前回测在数据库中已经存在,则跳过该测试.
    :param output_path_has_strategy_class_name 默认为False.输出文件路径是否包含 策略类名称.
    :param output_separate_by_backtest_status 默认为False.输出文件路径是否包含按 backtest_status 分目录存放.
    :param generate_setting_json_file 生成 setting json 文件
    :param file_name_include_symbol 生成文件的文件名带 symbol 用以进行区分，默认False，过长文件名可能导致系统不支持长文件名错误。
    :param stg_info_duplicate_name_options 默认 DuplicateNameOptions.raise_error。策略重名应对措施。该参数仅在 save_stats == True 的情况下启用
    """
    return bulk_backtest_pub(
        strategy_cls=strategy_cls,
        multi_symbols=False,
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
        ignore_existed_backtest=ignore_existed_backtest,
        output_path_has_strategy_class_name=output_path_has_strategy_class_name,
        output_separate_by_backtest_status=output_separate_by_backtest_status,
        generate_setting_json_file=generate_setting_json_file,
        file_name_include_symbol=file_name_include_symbol,
        stg_info_duplicate_name_options=stg_info_duplicate_name_options,
    )


def _run_bulk_backtest_double_ma():
    from strategies.double_ma_strategy import DoubleMA4Test
    from vnpy_extra.config import set_log_level
    set_log_level('INFO')
    engine_param_dic_list_dic = {
        "RB9999.SHFE": [
            dict(
                vt_symbol="RB9999.SHFE",
                cross_limit_method=CrossLimitMethod.open_price,
            ),
            dict(
                vt_symbol="RB9999.SHFE",
                cross_limit_method=CrossLimitMethod.worst_price,
            ),
        ],
        "I9999.DCE": [
            dict(
                vt_symbol="I9999.DCE",
                cross_limit_method=CrossLimitMethod.open_price,
            ),
            dict(
                vt_symbol="I9999.DCE",
                cross_limit_method=CrossLimitMethod.worst_price,
            ),
        ],
        "HC9999.SHFE": [
            dict(
                vt_symbol="HC9999.SHFE",
                cross_limit_method=CrossLimitMethod.open_price,
            ),
            dict(
                vt_symbol="HC9999.SHFE",
                cross_limit_method=CrossLimitMethod.worst_price,
            ),
        ],
    }
    for vt_symbol, engine_param_dic_list in engine_param_dic_list_dic.items():
        result_df = bulk_backtest(
            DoubleMA4Test,
            engine_param_dic_list=engine_param_dic_list,
            strategy_param_dic_list=dict(
                fast_window=[20, 30],
            ),
            multi_process=0,
            root_folder_name=f'bulk_{vt_symbol}'
        )


def bulk_backtest_separated_by_symbol(
        strategy_cls: Type[CtaTemplate],
        vt_symbol_info_list: List[Union[
            Tuple[str, Union[float, int]],
            Tuple[str, Union[float, int], Union[float, int]]
        ]],
        cross_limit_methods: List[CrossLimitMethod],
        strategy_param_dic_list: List[Dict[str, List]],
        start: Optional[date] = None,
        end: Optional[date] = None,
        capital=None,
        **kwargs
):
    for _ in vt_symbol_info_list:
        engine_param_dic = {}
        if len(_) == 1:
            vt_symbol = _[0]
            engine_param_dic['vt_symbol'] = vt_symbol
        elif len(_) == 2:
            vt_symbol, slippage = _
            engine_param_dic['vt_symbol'] = vt_symbol
            engine_param_dic['slippage'] = slippage
        elif len(_) == 3:
            vt_symbol, slippage, rate = _
            engine_param_dic['vt_symbol'] = vt_symbol
            engine_param_dic['slippage'] = slippage
            engine_param_dic['rate'] = rate
        else:
            raise ValueError(f"vt_symbol_info = {_} 无效")

        if start is not None:
            engine_param_dic['start'] = str_2_date(start)
        if end is not None:
            engine_param_dic['end'] = str_2_date(end)
        if capital is not None:
            engine_param_dic['capital'] = capital

        engine_param_dic_list = []
        for cross_limit_method in cross_limit_methods:
            engine_param_dic['cross_limit_method'] = cross_limit_method
            engine_param_dic_list.append(engine_param_dic.copy())

        kwargs.setdefault('output_path_has_strategy_class_name', False)
        bulk_backtest(
            strategy_cls=strategy_cls,
            engine_param_dic_list=engine_param_dic_list,
            strategy_param_dic_list=strategy_param_dic_list,
            root_folder_name=strategy_cls.__name__,
            **kwargs
        )


def _run_bulk_backtest_separated_by_symbol(all_symbol_4_test_cases=False):
    from strategies.double_ma_strategy import DoubleMA4Test
    from vnpy_extra.config import set_log_level
    set_log_level('INFO')
    if not all_symbol_4_test_cases:
        vt_symbol_info_list = [
            ("RB9999.SHFE", 0),
            ("HC9999.SHFE", 0),
        ]
    else:
        vt_symbol_info_list = [(item, 0) for item in VT_SYMBOL_LIST_ALL]

    strategy_param_dic_list = [
        dict(
            fast_window=[5, 10, 20, 30],
            slow_window=[80, 100],
        )
    ]
    bulk_backtest_separated_by_symbol(
        DoubleMA4Test,
        vt_symbol_info_list=vt_symbol_info_list,
        cross_limit_methods=[CrossLimitMethod.open_price, CrossLimitMethod.worst_price],  #
        strategy_param_dic_list=strategy_param_dic_list,
        multi_process=0,
        output_available_only=False,
        start=date(2018, 1, 1),
        capital=1_000_000,
        save_stats=False,
        generate_setting_json_file=False,
        file_name_include_symbol=True,
    )


if __name__ == "__main__":
    _run_backtest()
    # _run_bulk_backtest_double_ma()
    # _run_bulk_backtest_separated_by_symbol()
