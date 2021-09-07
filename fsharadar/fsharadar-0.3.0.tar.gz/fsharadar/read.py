# Methods for reading the Sharadar files and processing data
# before ingesting them into the Zipline bundle 

import os
import numpy as np
import pandas as pd
from six import iteritems
from tqdm import tqdm

from fsharadar.defs import bundle_missing_value
from fsharadar.utils import print_progress
from fsharadar.asset_metadata import get_ticker_sids

def parse_pricing_and_vol(data,
                          sessions,
                          symbol_map):
    for asset_id, symbol in iteritems(symbol_map):
        asset_data = data.xs(
            symbol,
            level=0 # 1 
        ).reindex(
            sessions.tz_localize(None)
        ).fillna(bundle_missing_value)  # 0.0
        yield asset_id, asset_data


def read_data_file(data_file, tickers_df, bundle_tags):

    # read sep file
    usecols = ['ticker', 'date'] + bundle_tags
    raw_data = pd.read_csv(data_file, parse_dates=['date'], usecols=usecols)
    raw_data.rename(columns={'ticker': 'symbol'}, inplace=True)

    # remove assets without sids
    all_tickers = tickers_df.ticker.unique()
    common_tickers = list(set(raw_data.symbol.unique()) & set(all_tickers))
    raw_data = raw_data.query('symbol in @common_tickers')

    return raw_data

def read_actions_file(actions_file, tickers_df):

    # read actions file
    actions_df = pd.read_csv(actions_file, parse_dates=['date'])
    actions_df.rename(columns={'ticker': 'symbol'}, inplace=True)

    # remove assets without sids
    all_tickers = tickers_df.ticker.unique()
    common_tickers = list(set(actions_df.symbol.unique()) & set(all_tickers))
    actions_df = actions_df.query('symbol in @common_tickers')

    return actions_df

def create_date_range_df(calendar):
    
    start_session = calendar.first_session
    end_session = calendar.last_session

    date_range = pd.date_range(start=start_session, end=end_session)
    
    date_range_df = pd.DataFrame(index=date_range.tz_localize(None))
    date_range_df = date_range_df.sort_index(ascending=False)
    
    return date_range_df

def calc_dividend_ratios(unadj_xs):
    
    unadj_xs = unadj_xs.sort_index(ascending=False)
    
    closes = unadj_xs['close']
    dividends = unadj_xs['dividends'].shift(1)
    dividends[0] = 0.0
    
    dividend_ratios = (1. - dividends/closes)
    
    return dividend_ratios

def unadjust_splits(sep_df, actions_df, calendar, show_progress=False, t1=None):

    if show_progress: t1 = print_progress('Creating multi-index dataframes and sorting index ...', t1)
    
    # some splits in actions_df are located in non-business days
    sessions_df = create_date_range_df(calendar) # create_sessions_df()

    actions_mi =  actions_df.set_index(['symbol', 'date'])
    actions_mi.sort_index(level=0, inplace=True)
    action_tickers = actions_mi.index.get_level_values(0).unique()

    sep_mi =  sep_df.set_index(['symbol', 'date'])
    sep_mi.sort_index(level=0, inplace=True)
    tickers = sep_mi.index.get_level_values(0).unique()

    if show_progress: t1 = print_progress('Unadjusting splits ...', t1)
    
    dfs = []
    dfs_keys = []

    for ticker in tqdm(tickers):
    
        sep_xs = sep_mi.xs(ticker)
        sep_xs = sep_xs.sort_index(ascending=False)
        # sep_xs.index = sep_xs.index.tz_localize('UTC')
    
        if ticker not in action_tickers:
            dfs_keys.append(ticker)
            sep_xs['dividends'] = 0
            dfs.append(sep_xs)
            continue

        # select splits
        actions_xs = actions_mi.xs(ticker)
        actions_xs = actions_xs.sort_index(ascending=False)
        # actions_xs.index = actions_xs.index.tz_localize('UTC')
        splits = actions_xs[actions_xs.action == 'split'].value  
        
        # calculate split factor
        session_splits = sessions_df.join(splits, how='left')
        session_splits = session_splits.sort_index(ascending=False)
        session_splits = session_splits.rename(columns={'value': 'split_ratio'})
        
        session_splits['split_ratio'] = session_splits['split_ratio'].shift(1)
        session_splits['split_ratio'] = session_splits['split_ratio'].replace(np.nan, 1.0)
        session_splits['split_factor'] = session_splits['split_ratio'].cumprod()

        # add splits to the sep frame
        sep_xs = sep_xs.join(session_splits, how='left')
        sep_xs = sep_xs.sort_index(ascending=False)

        # add dividends from actions 
        dactions = ['dividend', 'spinoffdividend']
        dividends = actions_xs.query('action in @dactions').value
        dividends = dividends.groupby(dividends.index).sum()
        sep_xs = sep_xs.join(dividends, how='left')
        sep_xs['value'] = sep_xs['value'].fillna(0)
        sep_xs.rename(columns={'value': 'dividends'}, inplace=True)

        # apply split factor to prices
        for field in ['close', 'open', 'high', 'low', 'dividends']:
            sep_xs[field] = sep_xs['split_factor']*sep_xs[field]

        # apply split factor to volumes
        sep_xs['volume'] = sep_xs['volume']/sep_xs['split_factor']
    
        sep_xs.drop(['split_ratio', 'split_factor'], axis=1, inplace=True)
        
        # remove tickers with negative dividend ratios
        dividend_ratios = calc_dividend_ratios(sep_xs)
    
        neg_dividend_ratios = (dividend_ratios < 0).sum()
        if neg_dividend_ratios > 0:
            continue
        
        dfs_keys.append(ticker)
        dfs.append(sep_xs)

    if show_progress: t1 = print_progress('Concatenating unadjusted data ...', t1)

    unadj_df = pd.concat(dfs, keys=dfs_keys)
    unadj_df = unadj_df.reset_index()
    unadj_df.rename(columns={'level_0': 'symbol'}, inplace=True)
    
    return unadj_df, t1

def get_dividends(unadj_data, tickers_df):
    
    dividends = unadj_data[[
        'symbol',
        'date',
        'dividends',
    ]].loc[unadj_data.dividends != 0]

    # add sids from tickers_file
    ticker_sids = get_ticker_sids(tickers_df)
    dividends = dividends.join(ticker_sids, on='symbol', how='left')[['sid', 'date', 'dividends']]
    dividends = dividends.reset_index(drop=True)
    
    dividends['record_date'] = dividends['declared_date'] = dividends['pay_date'] = pd.NaT
    
    dividends.rename(
        columns={
            'dividends': 'amount',
            'date': 'ex_date',
        },
        inplace=True,
    )
    
    return dividends

def get_splits(actions_df, tickers_df):
    
    splits = actions_df[actions_df.action == 'split'][['date', 'symbol', 'value']]    
    splits.rename(columns={'value': 'split_ratio'}, inplace=True)
    splits = splits.reset_index(drop=True)
    
    # add sids
    ticker_sids = get_ticker_sids(tickers_df)
    splits = splits.join(ticker_sids, on='symbol', how='left')[['sid', 'date', 'split_ratio']]
    
    splits['split_ratio'] = 1.0 / splits.split_ratio
    
    splits.rename(
        columns={
            'split_ratio': 'ratio',
            'date': 'effective_date',
        },
        inplace=True,
    )
    
    return splits

def read_files(tickers_file, data_file, actions_file):
    
    # read the tickers file (with sids)
    tickers_df = pd.read_csv(tickers_file)

    # read the data file (with ohlcv prices)
    data_df = read_data_file(data_file, tickers_df)

    if actions_file is None:
        return tickers_df, data_df, actions_file

    # read the actions file (with splits) and unadjust splits
    actions_df = read_actions_file(actions_file, tickers_df)
    unadj_data = unadjust_splits(data_df, actions_df)

    return tickers_df, unadj_data, actions_df


    
