# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.PagingParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Data paging parameters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Dict, Any

from .AnyValueMap import AnyValueMap
from ..convert.BooleanConverter import BooleanConverter
from ..convert.IntegerConverter import IntegerConverter


class PagingParams:
    """
    Data transfer object to pass paging parameters for queries.

    The page is defined by two parameters:
    - the :func:`skip` parameter defines number of items to skip.
    - the :func:`take` parameter sets how many items to return in a page.
    - additionally, the optional :func:`total` parameter tells to return total number of items in the query.

     Remember: not all implementations support the :func:`total` parameter
     because its generation may lead to severe performance implications.

     Example:

     .. code-block:: python
     
         filter = FilterParams.fromTuples("type", "Type1")
         paging = PagingParams(0, 100)

         myDataClient.get_data_by_filter(filter, paging)
    """

    def __init__(self, skip: int = None, take: int = None, total: bool = False):
        """
        Creates a new instance and sets its values.

        :param skip: the number of items to skip.

        :param take: the number of items to return.

        :param total: true to return the total number of items.
        """
        # The number of items to skip.
        self.skip: int = IntegerConverter.to_nullable_integer(skip)
        # The number of items to return.
        self.take: int = IntegerConverter.to_nullable_integer(take)
        # The flag to return the total number of items.
        self.total: bool = BooleanConverter.to_boolean_with_default(total, False)

        if self.take == 0:
            self.take = None

    def get_skip(self, min_skip: int) -> int:
        """
        Gets the number of items to skip.

        :param min_skip: the minimum number of items to skip.

        :return: the number of items to skip.
        """
        if self.skip is None:
            return min_skip
        if self.skip < min_skip:
            return min_skip
        return self.skip

    def get_take(self, max_take: int) -> int:
        """
        Gets the number of items to return in a page.

        :param max_take: the maximum number of items to return.

        :return: the number of items to return.
        """
        if self.take is None:
            return max_take
        if self.take < 0:
            return 0
        if self.take > max_take:
            return max_take
        return self.take

    def has_total(self):
        return self.total

    def to_json(self) -> Dict[str, Any]:
        return {
            'skip': self.skip,
            'take': self.take,
            'total': self.total
        }

    @staticmethod
    def from_json(value: Any) -> 'PagingParams':
        if not isinstance(value, dict):
            return value

        skip = value['skip'] if 'skip' in value else None
        take = value['take'] if 'take' in value else None
        total = value['total'] if 'total' in value else None
        return PagingParams(skip, take, total)

    @staticmethod
    def from_value(value: Any) -> 'PagingParams':
        """
        Converts specified args into PagingParams.

        :param value: args to be converted

        :return: a newly created PagingParams.
        """
        if isinstance(value, PagingParams):
            return value
        if isinstance(value, AnyValueMap):
            return PagingParams.from_map(value)

        map = AnyValueMap.from_value(value)
        return PagingParams.from_map(map)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'PagingParams':
        """
        Creates a new PagingParams from a list of key-args pairs called tuples.

        :param tuples: a list of values where odd elements are keys and the following even elements are values

        :return: a newly created PagingParams.
        """
        map = AnyValueMap.from_tuples_array(tuples)
        return PagingParams.from_map(map)

    @staticmethod
    def from_map(map: Any) -> 'PagingParams':
        """
        Creates a new PagingParams and sets it parameters from the specified map

        :param map: a AnyValueMap or StringValueMap to initialize this PagingParams

        :return: a newly created PagingParams.
        """
        skip = map.get_as_nullable_integer("skip")
        take = map.get_as_nullable_integer("take")
        total = map.get_as_nullable_boolean("total")
        return PagingParams(skip, take, total)
