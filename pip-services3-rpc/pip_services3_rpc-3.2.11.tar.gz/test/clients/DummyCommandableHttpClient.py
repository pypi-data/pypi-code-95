# -*- coding: utf-8 -*-
"""
    test.rest.DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy commandable HTTP client
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.data import DataPage, FilterParams, PagingParams

from pip_services3_rpc.clients import CommandableHttpClient
from .IDummyClient import IDummyClient
from .. import Dummy


class DummyCommandableHttpClient(CommandableHttpClient, IDummyClient):

    def __init__(self):
        super(DummyCommandableHttpClient, self).__init__('dummy')

    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams) -> DataPage:
        result = self.call_command(
            'get_dummies',
            correlation_id,
            {
                'filter': filter,
                'paging': paging
            }
        )
        page = DataPage(
            data=[Dummy(**item) for item in result['data']],
            total=result['total']
        )
        return page

    def get_one_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        response = self.call_command(
            'get_dummy_by_id',
            correlation_id,
            {
                'dummy_id': dummy_id
            }
        )
        if response:
            return Dummy(**response)

    def create(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        response = self.call_command(
            'create_dummy',
            correlation_id,
            {
                'dummy': item
            }
        )
        if response:
            return Dummy(**response)

    def update(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        response = self.call_command(
            'update_dummy',
            correlation_id,
            {
                'dummy': item
            }
        )
        if response:
            return Dummy(**response)

    def delete_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        response = self.call_command(
            'delete_dummy',
            correlation_id,
            {
                'dummy_id': dummy_id
            }
        )
        if response:
            return Dummy(**response)

    def check_correlation_id(self, correlation_id: Optional[str]) -> str:
        result = self.call_command(
            'check_correlation_id',
            correlation_id,
            {}
        )
        return None if not result else result.get('correlation_id')
