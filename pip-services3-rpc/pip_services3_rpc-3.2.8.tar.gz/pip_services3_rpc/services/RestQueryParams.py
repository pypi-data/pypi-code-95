# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.RestQueryParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    REST query parameters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.data import IdGenerator, FilterParams, PagingParams


class RestQueryParams(dict):

    def __init__(self, correlation_id: Optional[str] = None, filte: FilterParams = None, paging: PagingParams = None):
        super().__init__()
        self.add_correlation_id(correlation_id)
        self.add_filter_params(filte)
        self.add_paging_params(paging)

    def add_correlation_id(self, correlation_id: Optional[str]=None):
        # Automatically generate short ids for now
        if correlation_id is None:
            correlation_id = IdGenerator.next_short()

        self['correlation_id'] = correlation_id

    def add_filter_params(self, filter):
        if filter is None: return

        for key, value in filter.items():
            self[key] = value

    def add_paging_params(self, paging: PagingParams):
        if paging is None: return

        if not (paging.total is None):
            self['total'] = paging.total
        if not (paging.skip is None):
            self['skip'] = paging.skip
        if not (paging.take is None):
            self['take'] = paging.take
