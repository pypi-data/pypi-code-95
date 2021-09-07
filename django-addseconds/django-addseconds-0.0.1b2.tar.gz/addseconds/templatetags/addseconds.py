"""
add_seconds template filter module
"""

import datetime

from django import template
from django.utils.dateparse import (
    parse_date as _parse_date,
    parse_datetime as _parse_datetime,
    parse_time as _parse_time,
)


register = template.Library()


@register.filter
def parse_date(value):
    """
    Filter parsing date
    and returning a date value
    """
    if isinstance(value, str):
        return _parse_date(value)


@register.filter
def parse_time(value):
    """
    Filter parsing time
    and returning a time value
    """
    if isinstance(value, str):
        return _parse_time(value)


@register.filter
def parse_datetime(value):
    """
    Filter parsing datetime
    and returning a datetime value
    """
    if isinstance(value, str):
        return _parse_datetime(value)


@register.filter
def addseconds(value, arg):
    """
    Filter adding seconds to the datetime parameter.

    If the `value` parameter is not a datetime,
    tries to convert to it. Integer as a unixtime,
    string as a string timestamp.

    If the `arg` is a string, converts
    it to the numeric.
    """

    if not isinstance(value, datetime.datetime):
        if isinstance(value, datetime.date):
            value = datetime.datetime.combine(value, datetime.time(0))
        elif isinstance(value, (int, float)):
            value = datetime.datetime.fromtimestamp(value)
        elif isinstance(value, str):
            value = _parse_datetime(value)
    if not isinstance(value, datetime.datetime):
        return
    if isinstance(arg, str):
        try:
            arg = float(arg)
        except ValueError:
            return
    if not isinstance(arg, (int, float)):
        return

    return value + datetime.timedelta(0, arg)
