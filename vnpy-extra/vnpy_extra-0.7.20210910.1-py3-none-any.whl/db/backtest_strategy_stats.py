#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/1/13 下午9:02
@File    : backtest_strategy_stats.py
@contact : mmmaaaggg@163.com
@desc    : 本模块用于维护及更新　回测策略统计表中的记录状态
"""
import logging

import pandas as pd

from vnpy_extra.db.orm import StrategyBacktestStats

logger = logging.getLogger(__name__)


def update_backtest_strategy_stats_by_xls(file_path):
    """根据xls文件更新相应记录状态"""
    df = pd.read_excel(file_path)
    is_available = True
    columns = ["strategy_class_name", "id_name", 'symbols', "cross_limit_method", "backtest_status"]
    # 数据检查
    for item in columns:
        if item not in df.columns:
            logger.error("%s not in df for file: %s", item, file_path)
            is_available = False

    if not is_available:
        return
    # 只取需要的列
    df = df[columns][df["backtest_status"] != 0]
    StrategyBacktestStats.update_backtest_status_bulk(df.to_dict(orient='record'))


def _test_update_backtest_strategy_stats_by_xls():
    file_path = r''
    update_backtest_strategy_stats_by_xls(file_path)


if __name__ == "__main__":
    _test_update_backtest_strategy_stats_by_xls()
