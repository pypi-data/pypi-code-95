# ingest_bundle() and associated methods implemented from
# the corresponding originals within zipline/data/bundles/core.py
# and zipline/data/bundles/quandl.py for ingesting
# data from the sharadar files and supporting the sharadar sids.

import os
import time
import numpy as np
import pandas as pd

from contextlib2 import ExitStack
from trading_calendars import get_calendar

import zipline.utils.paths as pth
from zipline.utils.cache import (
    dataframe_cache,
    working_dir,
    working_file,
)

from zipline.data.bundles import (
    bundles,
    UnknownBundle,
    to_bundle_ingest_dirname,
)
from zipline.data.bundles.core import (
    cache_path,
    daily_equity_relative,
    asset_db_relative,
    adjustment_db_relative,
)

from zipline.assets import AssetDBWriter, AssetFinder
# from zipline.data.adjustments import SQLiteAdjustmentWriter
from fsharadar.adjustments import SharadarSQLiteAdjustmentWriter

from fsharadar.read import (
    read_data_file,
    read_actions_file,
    parse_pricing_and_vol,
    unadjust_splits,
    get_splits,
    get_dividends,
)

from fsharadar.asset_metadata import (
    get_asset_metadata,
    get_exchanges,
)

from fsharadar.bcolz_writer_float64 import SharadarDailyBcolzWriter
from fsharadar.bcolz_reader_float64 import SharadarDailyBcolzReader

from fsharadar.db_access import (
    fsharadar_db_relative,
    write_db,
)

from fsharadar.utils import print_progress


def read_and_ingest(environ,
                    asset_db_writer,
                    minute_bar_writer,
                    daily_bar_writer,
                    adjustment_writer,
                    calendar,
                    start_session,
                    end_session,
                    cache,
                    show_progress,
                    output_dir,
                    tickers_file, 
                    data_file,
                    actions_file):

    t1 = None

    if show_progress: t1 = print_progress('Reading the tickers and data files ...', t1)

    # read the tickers file (with sids)
    tickers_df = pd.read_csv(tickers_file)

    # read the data file (with ohlcv prices)
    raw_data = read_data_file(data_file, tickers_df, list(daily_bar_writer.bundle_tags))

    # read the actions file (with splits) and unadjust splits
    if actions_file is not None:
        if show_progress: t1 = print_progress('Reading the actions file  ...', t1)
        actions_df = read_actions_file(actions_file, tickers_df)
        raw_data, t1 = unadjust_splits(raw_data, actions_df, calendar, show_progress, t1)

    # write metadata
    if show_progress: t1 = print_progress('Writing metadata ...', t1)
    
    asset_metadata = get_asset_metadata(raw_data[['symbol', 'date']], tickers_df)
    exchanges = get_exchanges(asset_metadata)
  
    asset_db_writer.write(asset_metadata, exchanges=exchanges)

    # write raw data
    if show_progress: t1 = print_progress('Creating multi-index dataframe and sorting index ...', t1)

    raw_data = raw_data.set_index(['symbol', 'date'])
    raw_data = raw_data.sort_index(level=0)

    if show_progress: t1 = print_progress('Writing daily data ...', t1)
    
    symbol_map = asset_metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)
    
    daily_bar_writer.write(
        parse_pricing_and_vol(
            raw_data,
            sessions,
            symbol_map
        ),
        assets=symbol_map.index.values, 
        show_progress=show_progress
    )

    raw_data = raw_data.reset_index()

    if actions_file is None:
        if show_progress: t1 = print_progress('Done.', t1)
        return

    if show_progress: t1 = print_progress('Writing split and dividend adjustments ...', t1)

    # write splits and dividends
    splits = get_splits(actions_df, tickers_df)
    dividends = get_dividends(raw_data, tickers_df)
    
    adjustment_writer.write(
        splits=splits,
        dividends=dividends
    )

    if show_progress: t1 = print_progress('Done.', t1)



def ingest_bundle(bundle_name,
                  bundle_tags,
                  tickers_table,
                  tickers_file,
                  data_file,
                  actions_file=None,
                  show_progress=False):

    # original argumenets
    name = bundle_name
    environ = os.environ
    timestamp = None
    assets_versions = ()

    # select bundle
    try:
        bundle = bundles[name]
    except KeyError:
        raise UnknownBundle(name)

    # define output directory based on bundle name and timestamp

    calendar = get_calendar(bundle.calendar_name)
    start_session = calendar.first_session
    end_session = calendar.last_session

    timestamp = pd.Timestamp.utcnow()
    timestamp = timestamp.tz_convert('utc').tz_localize(None)

    timestr = to_bundle_ingest_dirname(timestamp)
    cachepath = cache_path(name, environ=environ)

    output_dir = pth.data_path([name, timestr], environ=environ)

    pth.ensure_directory(output_dir)
    pth.ensure_directory(cachepath)

    # write tickers to the fsharadar db
    # output_dir = pth.data_path([name, timestr], environ=environ,)
    # write_db(tickers_file, table_name='SEP', output_dir=output_dir)

    # create writers and ingest data
    
    with dataframe_cache(cachepath, clean_on_failure=False) as cache, \
            ExitStack() as stack:
            
    # we use `cleanup_on_failure=False` so that we don't purge the
    # cache directory if the load fails in the middle
        
        wd = stack.enter_context(working_dir(
            pth.data_path([], environ=environ))
        )
        
        daily_bars_path = wd.ensure_dir(
            *daily_equity_relative(name, timestr)
        )
                
        daily_bar_writer = SharadarDailyBcolzWriter(
            daily_bars_path,
            calendar,
            start_session,
            end_session,
            bundle_tags, # new argument
        )
                
        # Do an empty write to ensure that the daily ctables exist
        # when we create the SQLiteAdjustmentWriter below. The
        # SQLiteAdjustmentWriter needs to open the daily ctables so
        # that it can compute the adjustment ratios for the dividends.

        daily_bar_writer.write(())
        
        minute_bar_writer = None 
        
        # DB Writer
            
        assets_db_path = wd.getpath(*asset_db_relative(name, timestr))
        asset_db_writer = AssetDBWriter(assets_db_path)

        adjustment_db_writer = stack.enter_context(
            SharadarSQLiteAdjustmentWriter(
                wd.getpath(*adjustment_db_relative(name, timestr)),
                SharadarDailyBcolzReader(daily_bars_path, bundle_tags=bundle_tags),
                overwrite=True,
            )
        )
         
        read_and_ingest(
                environ,
                asset_db_writer,
                minute_bar_writer,
                daily_bar_writer,
                adjustment_db_writer,
                calendar,
                start_session,
                end_session,
                cache,
                show_progress,
                pth.data_path([name, timestr], environ=environ,),
                tickers_file,
                data_file,
                actions_file,
        )
        
        # FSharadar DB (metadata)
         
        db_path = wd.getpath(*fsharadar_db_relative(name, timestr))
        write_db(tickers_file, tickers_table, db_path)



 
