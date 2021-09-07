import pandas as pd
from trading_calendars import get_calendar
from zipline.data.data_portal import DataPortal

def get_data_portal(bundle_data):

    trading_calendar = get_calendar("NYSE")

    # Create a data portal
    data_portal = DataPortal(
        bundle_data.asset_finder,
        trading_calendar=trading_calendar,
        first_trading_day=bundle_data.equity_daily_bar_reader.first_trading_day,
        equity_daily_reader=bundle_data.equity_daily_bar_reader,
        adjustment_reader=bundle_data.adjustment_reader)

    return data_portal

def get_data_portal_history_window(bundle_data, assets, start_date, end_date, field='close'):

    data_portal = get_data_portal(bundle_data)

    # Set the given start and end dates to Timestamps.
    end_date = pd.Timestamp(end_date, tz='utc')
    start_date = pd.Timestamp(start_date, tz='utc')

    # Get the locations of the start and end dates
    trading_calendar = data_portal.trading_calendar
    sessions = trading_calendar.sessions_in_range(start_date, end_date)
    bar_count = len(sessions)
     
    # return the historical data for the given window
    return data_portal.get_history_window(
                            assets=assets,
                            end_dt=end_date,
                            bar_count=bar_count,
                            frequency='1d',
                            field=field,
                            data_frequency='daily')

