# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.SortParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Sort params implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.data import SortField


class SortParams(list):
    """
    Defines a field name and order used to sort query results.

    Example:
    
    .. code-block:: python

         filter = FilterParams.fromTuples("type", "Type1")
         paging = PagingParams(0, 100)
         sorting = SortingParams(SortField("create_time", true))

         myDataClient.get_data_by_filter(filter, paging, sorting)
    """

    def __init__(self, *fields: SortField):
        """
        Creates a new instance and initializes it with specified sort fields.

        :param fields: a list of fields to sort by.
        """
        super(SortParams, self).__init__()
        for field in fields:
            self.append(field)
