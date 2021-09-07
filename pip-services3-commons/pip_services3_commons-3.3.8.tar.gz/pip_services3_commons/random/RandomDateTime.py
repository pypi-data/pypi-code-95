# -*- coding: utf-8 -*-
"""
    pip_services3_commons.random.RandomDateTime
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    RandomDateTime implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import datetime
from typing import Union

import pytz

from pip_services3_commons.random.RandomFloat import RandomFloat
from pip_services3_commons.random.RandomInteger import RandomInteger


class RandomDateTime:
    """
       Random generator for Date time values.

       Example:
       
       .. code-block:: python

           (month must be in 1..12)
           value1 = RandomDateTime.next_date(datetime.datetime(2010,1,1))       # Possible result: 2008-01-03
           value2 = RandomDateTime.next_datetime(datetime.datetime(2017,1,1))   # Possible result: 2007-03-11 11:20:32
           value3 = RandomDateTime.update_datetime(datetime.datetime(2010,1,2)) # Possible result: 2010-02-05 11:33:23
    """

    @staticmethod
    def next_date(min_year: datetime, max_year: datetime = None) -> datetime:
        """
        Generates a random Date in the range ['min_year', 'max_year'].
        This method generate dates without time (or time set to 00:00:00

        :param min_year: min range args
        :param max_year: (optional) maximum range args
        :return: a random Date and time args.
        """
        if max_year is None:
            max_year = min_year
            min_year = datetime.datetime(max_year.year - 10, 2, 1)

        diff = int((max_year.timestamp() * 1000) - (min_year.timestamp() * 1000))
        if diff <= 0:
            return min_year

        _time = ((min_year.timestamp() * 1000) + RandomInteger.next_integer(0, diff)) / 1000
        date = datetime.datetime.fromtimestamp(_time, pytz.utc)
        return datetime.datetime(date.year, date.month, date.day)

    @staticmethod
    def next_datetime(min_year: datetime, max_year: datetime = None) -> datetime:
        """
        Generates a random Date and time in the range ['minYear', 'maxYear'].
        This method generate dates without time (or time set to 00:00:00)

        :param min_year: min range args
        :param max_year: (optional) maximum range args
        :return: a random Date and time args.
        """
        if max_year is None:
            max_year = min_year
            min_year = datetime.datetime(2000, 1, 1)

        diff = int((max_year.timestamp() * 1000) - (min_year.timestamp() * 1000))
        if diff <= 0:
            return min_year

        _time = ((max_year.timestamp() * 1000) + RandomInteger.next_integer(0, diff)) / 1000
        return datetime.datetime.fromtimestamp(_time, pytz.utc)

    @staticmethod
    def update_datetime(value: datetime, range: Union[int, float] = None) -> datetime:
        """
        Updates (drifts) a Date args within specified range defined

        :param value: a Date args to drift.
        :param range: (optional) a range in milliseconds. Default: 10 days
        :return: an updated DateTime args.
        """
        if range == 0 or range is None:
            range = 10
        else:
            range = range / 24 / 3600000

        if range < 0:
            return value

        days = RandomFloat.next_float(-range, range)
        _time = value + datetime.timedelta(days)
        _time.replace(tzinfo=pytz.utc)
        return _time
