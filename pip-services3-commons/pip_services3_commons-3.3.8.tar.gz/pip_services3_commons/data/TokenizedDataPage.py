# -*- coding: utf-8 -*-

from typing import List




class TokenizedDataPage:
    """
    Data transfer object that is used to pass results of paginated queries.
    It contains items of retrieved page and optional total number of items.

    Most often this object type is used to send responses to paginated queries.
    Pagination parameters are defined by
    :class:`TokenizedPagingParams <pip_services3_commons.data.TokenizedPagingParams.TokenizedPagingParams>` object.
    The `token` parameter in the TokenizedPagingParams there means where to start the searxh.
    The `takes` parameter sets number of items to return in the page.
    And the optional `total` parameter tells to return total number of items in the query.

    The data page returns a token that shall be passed to the next search as a starting point.

    Remember: not all implementations support the `total` parameter
    because its generation may lead to severe performance implications.

    See :class:`PagingParams <pip_services3_commons.data.PagingParams.PagingParams>`

     Example:

    .. code-block:: python

        page = my_data_client.get_data_by_filter(
            "123",
            FilterParams.from_tuples("completed", True),
            TokenizedPagingParams(None, 100, True)
        )
    """

    def __init__(self, data: List[Any], token: str = None, total: int = None):
        """
        Creates a new instance of data page and assigns its values.

        :param data: a list of items from the retrieved page.
        :param token: (optional) a token to define astarting point for the next search.
        :param total: (optional) a total number of objects in the result.
        """
        # The total amount of items in a request.
        self.total: int = total
        # The starting point for the next search.
        self.token: str = token
        # The items of the retrieved page.
        self.data: List[Any] = data
