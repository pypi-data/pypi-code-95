# Methods for extracting the asset metadata (e.g., sids and exchanges)
# from the Sharadar tickers file

import numpy as np
import pandas as pd
from six import iteritems


def get_ticker_sids(tickers_df):
    tickers_dropna = tickers_df.dropna(subset=['ticker'])
    ticker_sids = pd.DataFrame(index=tickers_dropna.ticker.unique())
    ticker_sids['sid'] = tickers_dropna.groupby('ticker').apply(lambda x: x.permaticker.values[0])
    return ticker_sids

def get_ticker_exchanges(tickers_df):
    tickers_dropna = tickers_df.dropna(subset=['ticker'])
    ticker_exchanges = pd.DataFrame(index=tickers_dropna.ticker.unique())
    ticker_exchanges['exchange'] = tickers_dropna.groupby('ticker').apply(lambda x: x.exchange.values[0])
    return ticker_exchanges

def gen_asset_metadata(data, show_progress):

    data = data.groupby(
        by='symbol'
    ).agg(
        {'date': [np.min, np.max]}
    )
    data.reset_index(inplace=True)
    data['start_date'] = data.date.amin
    data['end_date'] = data.date.amax
    del data['date']
    data.columns = data.columns.get_level_values(0)

    # data['exchange'] = 'QUANDL'
    data['auto_close_date'] = data['end_date'].values + pd.Timedelta(days=1)
    return data

def get_asset_metadata(symbol_dates, tickers_df):
    
    # generate metadata
    asset_metadata = gen_asset_metadata(
        symbol_dates,
        show_progress=True
    )
    
    # add sids from tickers_file
    ticker_sids = get_ticker_sids(tickers_df)
    asset_metadata = asset_metadata.join(ticker_sids, on='symbol', how='left')
    
    # asset_metadata.dropna(inplace=True)
    asset_metadata['sid'] = asset_metadata.sid.astype(int)
    asset_metadata.set_index('sid', inplace=True)
        
    # add exchanges from tickers_file
    ticker_exchanges = get_ticker_exchanges(tickers_df)
    asset_metadata = asset_metadata.join(ticker_exchanges, on='symbol')

    return asset_metadata

def get_exchanges(asset_metadata):
    asset_metadata_exchanges = asset_metadata.exchange.unique()
    exchanges = pd.DataFrame(asset_metadata_exchanges, columns=['exchange'])
    exchanges['canonical_name'] = asset_metadata_exchanges
    exchanges['country_code'] = 'US'
    return exchanges

