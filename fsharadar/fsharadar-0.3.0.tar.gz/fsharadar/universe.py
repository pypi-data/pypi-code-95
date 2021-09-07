import numpy as np
import pandas as pd

from zipline.utils.math_utils import nanmedian

from zipline.pipeline.factors import (
    AverageDollarVolume,
    CustomFactor,
    Latest,
    SimpleMovingAverage,
)

from zipline.pipeline.filters import (
    StaticSids,
    AllPresent,
)

from zipline.assets import ASSET_DB_VERSION
from zipline.pipeline.data import USEquityPricing

from fsharadar import sep
from fsharadar import daily
from fsharadar.db_schema import FSHARADAR_DB_VERSION
from fsharadar.db_access import DBReader

class AverageMarketCap(SimpleMovingAverage):
    inputs = [daily.Fundamentals.marketcap]

class MedianDollarVolume(CustomFactor):
    """
    Median Daily Dollar Volume
    **Default Inputs:** [EquityPricing.close, EquityPricing.volume]
    **Default Window Length:** None
    """
    inputs = [USEquityPricing.close, USEquityPricing.volume]

    def compute(self, today, assets, out, close, volume):
        out[:] = nanmedian(close * volume, axis=0)


def TradableStocksUS():
    
    # Domestic Common Stocks
    sep_bundle_data = sep.load()
    asset_finder = sep_bundle_data.asset_finder
    db_url = asset_finder.engine.url.database.replace('assets-{}.sqlite'.format(ASSET_DB_VERSION),
                                                      'fsharadar-{}.sqlite'.format(FSHARADAR_DB_VERSION))
    
    db_reader = DBReader(db_url)
    tickers_df = db_reader.get_tickers()
    dcs_sids = tickers_df[tickers_df.category == "Domestic Common Stock"].sid.values
    dcs_universe = StaticSids(dcs_sids)

    # The stock must not have more than 20 days of missing close price in the -- last 200
    # ...
    
    # and must not have any missing close price in the last 20 days
    # prices20 = AllPresent(inputs=[USEquityPricing.close], window_length=20, mask=dcs_universe)
    
    # marketcap > 350 M
    tradable_stocks = AverageMarketCap(window_length=20, mask=dcs_universe) >= 350.0
    
    # dollar volume > 2.5 M
    tradable_stocks = MedianDollarVolume(window_length=200, mask=tradable_stocks) >= 2.5e6
    
    # price > $5. 
    tradable_stocks = Latest([USEquityPricing.close], mask=tradable_stocks) > 5.0
    
    return tradable_stocks
