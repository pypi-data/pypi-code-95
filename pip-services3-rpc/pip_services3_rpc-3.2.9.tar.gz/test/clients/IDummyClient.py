# -*- coding: utf-8 -*-
"""
    test.IDummyClient
    ~~~~~~~~~~~~~~~~~
    
    Interface for dummy clients
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.data import DataPage, PagingParams, FilterParams

from test import Dummy


class IDummyClient:
    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError('Method from interface definition')

    def get_one_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def create(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def update(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def delete_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def check_correlation_id(self, correlation_id: Optional[str]) -> str:
        raise NotImplementedError('Method from interface definition')
