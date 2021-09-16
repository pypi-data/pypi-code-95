"""
Functions passed to jinja templates
"""

import logging
from dateutil.parser import parse as parse_dt

from stag.utils import SortDate as _SortDate

from slugify import slugify

log = logging.getLogger(__name__)


def _is_date(val):
    return isinstance(val, date)


def strftime(val, format):
    if not val:
        return ""

    try:
        if isinstance(val, (int, float, str)):
            dt = parse_dt(val)
        else:
            dt = val
        return dt.strftime(format)
    except ValueError:
        return val


def isoformat(val):
    if isinstance(val, str):
        dt = parse_dt(val)
    else:
        dt = val
    return dt.isoformat()


def sorted_pages(pages, key=None, reverse=False):
    if key == "date":
        return sorted(pages, key=_SortDate, reverse=reverse)
    return sorted(pages, reverse=reverse)


def update_env(env):
    globals = {"sorted_pages": sorted_pages, "slugify": slugify}
    filters = {"slugify": slugify, "strftime": strftime, "isoformat": isoformat}

    env.globals.update(globals)
    env.filters.update(filters)
