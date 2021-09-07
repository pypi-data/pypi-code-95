# Approximate Quantopian function `get_pricing`

from fsharadar import sep
from fsharadar.data_portal import get_data_portal_history_window

def get_pricing(assets, start_date, end_date, field='close'):

    bundle_data = sep.load()
    return get_data_portal_history_window(bundle_data, assets, start_date, end_date, field)

