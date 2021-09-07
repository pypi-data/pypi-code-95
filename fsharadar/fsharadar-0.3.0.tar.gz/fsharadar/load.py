# load() and associated methods implemented from
# the corresponding originals within zipline/data/bundles/core.py
# for connecting BundleData with sharadar-specific bundle and reader.


import os
import errno
import numpy as np
import pandas as pd
from toolz import complement
from contextlib2 import ExitStack

from trading_calendars import get_calendar

import zipline.utils.paths as pth

from zipline.data.bundles import (
    bundles,
    UnknownBundle,
    from_bundle_ingest_dirname,
)

from zipline.data.bundles.core import (
    BundleData,
    daily_equity_path,
    asset_db_path,
    adjustment_db_path,
)

from zipline.assets import AssetFinder
from zipline.data.adjustments import SQLiteAdjustmentReader

from fsharadar.bcolz_reader_float64 import SharadarDailyBcolzReader

def most_recent_data(bundle_name, timestamp, environ=None):

    if bundle_name not in bundles:
        raise UnknownBundle(bundle_name)

    try:
        candidates = os.listdir(
            pth.data_path([bundle_name], environ=environ),
        )
        return pth.data_path(
            [bundle_name,
             max(
                 filter(complement(pth.hidden), candidates),
                 key=from_bundle_ingest_dirname,
             )],
            environ=environ,
        )
    except (ValueError, OSError) as e:
        if getattr(e, 'errno', errno.ENOENT) != errno.ENOENT:
            raise
        raise ValueError(
            'no data for bundle {bundle!r} on or before {timestamp}\n'
            'maybe you need to run: $ zipline ingest -b {bundle}'.format(
                bundle=bundle_name,
                timestamp=timestamp,
            ),
        )

def load_bundle(bundle_name, bundle_tags, adjustment=False):
    
    # original arguments
    name = bundle_name
    environ=os.environ
    timestamp=None

    if timestamp is None:
        timestamp = pd.Timestamp.utcnow()
    timestr = most_recent_data(name, timestamp, environ=environ)

    if adjustment is True:
        adjustment_reader = SQLiteAdjustmentReader(
            adjustment_db_path(name, timestr, environ=environ),
        )
    else:
        adjustment_reader = None
    
    return BundleData(
        asset_finder=AssetFinder(
            asset_db_path(name, timestr, environ=environ),
        ),
        equity_minute_bar_reader=None,
        equity_daily_bar_reader=SharadarDailyBcolzReader(
            daily_equity_path(name, timestr, environ=environ),
            bundle_tags=bundle_tags,
        ),
        adjustment_reader=adjustment_reader,
    )

