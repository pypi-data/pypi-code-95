# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.FilterParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Free-form filter parameters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any

from .StringValueMap import StringValueMap


class FilterParams(StringValueMap):
    """
    Data transfer object used to pass filter parameters as simple key-args pairs.

    Example:

    .. code-block:: python
    
        filter = FilterParams.from_tuples("type", "Type1",
        "from_create_time", datetime.datetime(2000, 0, 1),
        "to_create_time", datetime.datetime.now(),
        "completed", True)
        paging = PagingParams(0, 100)

        myDataClient.get_data_by_filter(filter, paging)
    """

    def __init__(self, map: Any = None):
        super(FilterParams, self).__init__(map)
        # if map != None:
        #     for (key, args) in map.items():
        #         self[key] = args

    @staticmethod
    def from_value(value: Any) -> 'FilterParams':
        """
        Converts specified args into FilterParams.

        :param value: args to be converted

        :return: a newly created FilterParams.
        """
        return FilterParams(value)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'FilterParams':
        """
        Creates a new FilterParams from a list of key-args pairs called tuples.

        :param tuples: a list of values where odd elements are keys and the following even elements are values

        :return: a newly created FilterParams.
        """
        map = StringValueMap.from_tuples_array(tuples)
        return FilterParams(map)

    @staticmethod
    def from_string(line: str) -> 'FilterParams':
        """
        Parses semicolon-separated key-args pairs and returns them as a FilterParams.

        :param line: semicolon-separated key-args list to initialize FilterParams.

        :return: a newly created FilterParams.
        """
        map = StringValueMap.from_string(line)
        return FilterParams(map)
