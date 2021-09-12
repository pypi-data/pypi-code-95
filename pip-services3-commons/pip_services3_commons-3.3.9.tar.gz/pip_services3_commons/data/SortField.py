# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.SortField
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Sort field implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""


class SortField:
    """
    Defines a field name and order used to sort query results.

    Example:

    .. code-block:: python
    
         filter = FilterParams.fromTuples("type", "Type1")
         paging = PagingParams(0, 100)
         sorting = SortingParams(SortField("create_time", true))

         myDataClient.get_data_by_filter(filter, paging, sorting)
    """

    def __init__(self, name: str, ascending: bool = True):
        """
        Creates a new instance and assigns its values.

        :param name: the name of the field to sort by.

        :param ascending: true to sort in ascending order, and false to sort in descending order.
        """
        self.name: str = name
        self.ascending: bool = ascending
