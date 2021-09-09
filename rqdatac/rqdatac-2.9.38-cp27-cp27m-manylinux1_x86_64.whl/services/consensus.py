# -*- coding: utf-8 -*-
from collections import defaultdict
import pandas as pd
import numpy as np

from rqdatac.validators import (
    ensure_list_of_string,
    ensure_order_book_ids,
    check_items_in_container,
    ensure_date_range
)

from rqdatac.client import get_client
from rqdatac.decorators import export_as_api


CONSENSUS_INDICATOR_FIELDS = [
    'net_profit_t', 'net_profit_t1', 'net_profit_t2',
    'revenue_t', 'revenue_t1', 'revenue_t2',
    'net_asset_t', 'net_asset_t1', 'net_asset_t2',
    'cash_from_operating_activities_t',
    'cash_from_operating_activities_t1',
    'cash_from_operating_activities_t2'
]


DTYPES = {k: '<f8' for k in CONSENSUS_INDICATOR_FIELDS}
DTYPES['fiscal_year'] = '<u8'

CONSENSUS_PRICE_FIELDS = [
    'half_year_target_price',
    'one_year_target_price',
    'quarter_recommendation',
    'half_year_recommendation',
    'one_year_recommendation',
]

CONSENSUS_PRICE_FIELDS_MAP = {
    'half_year_target_price': ('price_raw', 'price_prd', 'M06'),
    'one_year_target_price': ('price_raw', 'price_prd', 'Y01'),
    'quarter_recommendation': ('grd_coef', 'grd_prd', '1'),
    'half_year_recommendation': ('grd_coef', 'grd_prd', '2'),
    'one_year_recommendation': ('grd_coef', 'grd_prd', '3'),
}

PRICE_DTYPES = {
    'half_year_target_price': '<f8',
    'one_year_target_price': '<f8',
    'quarter_recommendation': '<f8',
    'half_year_recommendation': '<f8',
    'one_year_recommendation': '<f8',
}


@export_as_api
def get_consensus_indicator(order_book_ids, fiscal_year, fields=None, market='cn'):
    """
    获取一致预期数据

    :param order_book_ids: 股票名称
    :param fiscal_year: int/str, 查询年份
    :param fields: list,  一致预期字段
    :param market: (Default value = 'cn')
    :returns: pandas  MultiIndex DataFrame

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    fiscal_year = int(fiscal_year)
    if fields is None:
        fields = CONSENSUS_INDICATOR_FIELDS
    else:
        fields = ensure_list_of_string(fields, 'consensus_indicator')
        check_items_in_container(fields, CONSENSUS_INDICATOR_FIELDS, 'consensus_indicator')
    data = get_client().execute('get_consensus_indicator', order_book_ids, fiscal_year, fields, market='cn')
    if not data:
        return None
    df = pd.DataFrame(data)
    df.set_index(['order_book_id', 'date'], inplace=True)
    df.sort_index(inplace=True)
    dtypes = {f: DTYPES[f] for f in df.columns if f in DTYPES}
    df = df.astype(dtypes)
    return df


@export_as_api
def get_consensus_price(order_book_ids, start_date=None, end_date=None, fields=None, adjust_type='none', market='cn'):
    """
    获取一致预期股价预测数据

    :param order_book_ids: 股票名称
    :param start_date: 开始日期， date-like object, 默认三月前那天
    :param end_date: 结束日期， date-like object， 默认当天
    :param fields: list,  一致预期字段
    :param adjust_type: 可选参数,默认为‘none', 返回原始数据
            'pre' 返回前复权数据
            'post' 返回后复权数据
    :param market: (Default value = 'cn')
    :returns: pandas MultiIndex DataFrame

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)

    if fields is None:
        fields = CONSENSUS_PRICE_FIELDS
    else:
        fields = ensure_list_of_string(fields, 'consensus_price')
        check_items_in_container(fields, CONSENSUS_PRICE_FIELDS, 'consensus_price')

    start_date, end_date = ensure_date_range(start_date, end_date)

    data = get_client().execute('get_consensus_price', order_book_ids, start_date, end_date, market='cn')
    if not data:
        return None

    records = defaultdict(dict)
    for r in data:
        key = (r['order_book_id'], r['institute'], r['date'])
        if key not in records:
            records[key].update(r)
        for field in fields:
            name, f, value = CONSENSUS_PRICE_FIELDS_MAP[field]
            if r[f] == value:
                records[key][field] = r[name]
    df = pd.DataFrame(list(records.values()))
    df.set_index(['order_book_id', 'date'], inplace=True)
    df.sort_index(inplace=True)
    df = df.reindex(columns=['institute'] + fields)
    df = df.astype({f: PRICE_DTYPES[f] for f in fields})

    if adjust_type != 'none':
        adjust_fields = list(set(CONSENSUS_PRICE_FIELDS[:2]) & set(fields))
        if not adjust_fields:
            return df

        from rqdatac.services.detail.adjust_price import get_ex_factor_for
        ex_factors = get_ex_factor_for(order_book_ids, market)
        pre = adjust_type == 'pre'

        def adjust(sub):
            factors = ex_factors.get(sub.name)
            if factors is None:
                return sub
            factor = np.take(factors.values, factors.index.searchsorted(sub.index.get_level_values(1), side='right') - 1)
            if pre:
                factor /= factors.iloc[-1]

            sub[adjust_fields] = (sub[adjust_fields].values.T * factor).T
            return sub

        df = df.groupby(level=0).apply(adjust)
        df[adjust_fields] = np.round(df[adjust_fields], 4)

    return df
