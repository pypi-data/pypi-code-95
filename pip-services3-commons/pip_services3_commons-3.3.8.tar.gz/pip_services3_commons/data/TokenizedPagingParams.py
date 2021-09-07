# -*- coding: utf-8 -*-
from typing import Any

from pip_services3_commons.data import AnyValueMap


class TokenizedPagingParams:
    """
    Data transfer object to pass tokenized paging parameters for queries.
    It can be used for complex paging scenarios, like paging across multiple databases
    where the previous state is encoded in a token. The token is usually retrieved from
    the previous response. The initial request shall go with token == `None`
    
    The page is defined by two parameters:
    - the `token` token that defines a starting point for the search.
    - the `take` parameter sets how many items to return in a page.
    - additionally, the optional `total` parameter tells to return total number of items in the query.

    Remember: not all implementations support the `total` parameter
    because its generation may lead to severe performance implications.

    Example:

    .. code-block:: python

        filter = FilterParams.from_tuples("type", "Type1");
        paging = TokenizedPagingParams(None, 100);

        result = my_data_client.get_data_by_filter(filter, paging)
    """

    def __init__(self, token: str = None, take: int = None, total: bool = None):
        """
        Creates a new instance and sets its values.

        :param token: token that defines a starting point for the search.
        :param take: the number of items to return.
        :param total: true to return the total number of items.
        """
        self.token: str = token
        self.take: int = take
        self.total: bool = total

        # This is for correctly using PagingParams with gRPC. gRPC defaults to 0 when take is null,
        # so we have to set it back to null if we get 0 in the constructor.
        if self.take == 0:
            self.take = None

    def get_take(self, max_take: int) -> int:
        """
        Gets the number of items to return in a page.

        :param max_take: the maximum number of items to return.
        :return: the number of items to return.
        """
        if self.take is None: return max_take;
        if self.take < 0: return 0
        if self.take > max_take: return max_take
        return self.take

    @staticmethod
    def from_value(value: Any) -> 'TokenizedPagingParams':
        """
        Converts specified value into TokenizedPagingParams.

        :param value: value to be converted
        :return: a newly created PagingParams.
        """
        if isinstance(value, TokenizedPagingParams):
            return value

        map = AnyValueMap.from_value(value)
        return TokenizedPagingParams.from_map(map)

    @staticmethod
    def from_tuple(*tuples: Any) -> 'TokenizedPagingParams':
        """
        Creates a new TokenizedPagingParams from a list of key-value pairs called tuples.

        :param tuples: a list of values where odd elements are keys and the following even elements are values
        :return: a newly created TokenizedPagingParams.
        """
        map = AnyValueMap.from_tuples_array(tuples)
        return TokenizedPagingParams.from_map(map)

    @staticmethod
    def from_map(map: AnyValueMap) -> 'TokenizedPagingParams':
        """
        Creates a new TokenizedPagingParams and sets it parameters from the specified map

        :param map: a AnyValueMap or StringValueMap to initialize this TokenizedPagingParams
        :return: a newly created PagingParams.
        """
        token = map.get_as_nullable_string("token")
        take = map.get_as_nullable_integer("take")
        total = map.get_as_boolean_with_default("total", False)
        return TokenizedPagingParams(token, take, total)
