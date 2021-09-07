# The fsharadar extension for resolving a few Python warnings
# within the zipline version.

import numpy as np
import pandas as pd
from logbook import Logger

from zipline.utils.numpy_utils import (
    datetime64ns_dtype,
    float64_dtype,
    int64_dtype,
    uint32_dtype,
    uint64_dtype,
)

log = Logger(__name__)

from zipline.data.adjustments import SQLiteAdjustmentWriter

class SharadarSQLiteAdjustmentWriter(SQLiteAdjustmentWriter):


    def __init__(self, conn_or_path, equity_daily_bar_reader, overwrite=False):
            SQLiteAdjustmentWriter.__init__(self, conn_or_path, equity_daily_bar_reader, overwrite)

    def calc_dividend_ratios(self, dividends):
        """
        Calculate the ratios to apply to equities when looking back at pricing
        history so that the price is smoothed over the ex_date, when the market
        adjusts to the change in equity value due to upcoming dividend.
        Returns
        -------
        DataFrame
            A frame in the same format as splits and mergers, with keys
            - sid, the id of the equity
            - effective_date, the date in seconds on which to apply the ratio.
            - ratio, the ratio to apply to backwards looking pricing data.
        """
        if dividends is None or dividends.empty:
            return pd.DataFrame(np.array(
                [],
                dtype=[
                    ('sid', uint64_dtype),
                    ('effective_date', uint32_dtype),
                    ('ratio', float64_dtype),
                ],
            ))

        pricing_reader = self._equity_daily_bar_reader
        input_sids = dividends.sid.values
        unique_sids, sids_ix = np.unique(input_sids, return_inverse=True)
        dates = pricing_reader.sessions.values

        close, = pricing_reader.load_raw_arrays(
            ['close'],
            pd.Timestamp(dates[0], tz='UTC'),
            pd.Timestamp(dates[-1], tz='UTC'),
            unique_sids,
        )
        date_ix = np.searchsorted(dates, dividends.ex_date.values)
        mask = date_ix > 0

        date_ix = date_ix[mask]
        sids_ix = sids_ix[mask]
        input_dates = dividends.ex_date.values[mask]

        # subtract one day to get the close on the day prior to the merger
        previous_close = close[date_ix - 1, sids_ix]
        input_sids = input_sids[mask]

        amount = dividends.amount.values[mask]
        ratio = 1.0 - amount / previous_close

        non_nan_ratio_mask = ~np.isnan(ratio)
        for ix in np.flatnonzero(~non_nan_ratio_mask):
            log.warn(
                "Couldn't compute ratio for dividend"
                " sid={sid}, ex_date={ex_date:%Y-%m-%d}, amount={amount:.3f}",
                sid=input_sids[ix],
                ex_date=pd.Timestamp(input_dates[ix]),
                amount=amount[ix],
            )

        # *** fsharadar ***
        # replacing nan with negative values for avoiding the Python warnings
        ratio = np.nan_to_num(ratio, nan=-1.0)
        
        positive_ratio_mask = ratio > 0
        
        for ix in np.flatnonzero(~positive_ratio_mask & non_nan_ratio_mask):
            log.warn(
                "Dividend ratio <= 0 for dividend"
                " sid={sid}, ex_date={ex_date:%Y-%m-%d}, amount={amount:.3f}",
                sid=input_sids[ix],
                ex_date=pd.Timestamp(input_dates[ix]),
                amount=amount[ix],
            )

        valid_ratio_mask = non_nan_ratio_mask & positive_ratio_mask
        return pd.DataFrame({
            'sid': input_sids[valid_ratio_mask],
            'effective_date': input_dates[valid_ratio_mask],
            'ratio': ratio[valid_ratio_mask],
        })


        
