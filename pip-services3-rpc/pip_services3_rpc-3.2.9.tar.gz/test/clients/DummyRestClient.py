# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.data import DataPage, PagingParams, FilterParams

from pip_services3_rpc.clients import RestClient
from .IDummyClient import IDummyClient
from .. import Dummy


class DummyRestClient(RestClient, IDummyClient):

    def __init__(self):
        super(DummyRestClient, self).__init__()

    def get_page_by_filter(self, correlation_id, filters: FilterParams, paging: PagingParams) -> DataPage:
        params = {}
        self._add_filter_params(params, filters)
        self._add_paging_params(params, paging)

        timing = self._instrument(correlation_id, 'dummy.get_page_by_filter')
        try:
            result = self._call(
                'GET',
                '/dummies',
                correlation_id,
                params
            )

            page = DataPage(
                data=[Dummy(**item) for item in result['data']],
                total=result['total']
            )
            return page
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def get_one_by_id(self, correlation_id, dummy_id):
        timing = self._instrument(correlation_id, 'dummy.get_one_by_id')
        try:
            response = self._call(
                'GET',
                f'/dummies/{dummy_id}',
                correlation_id,
            )
            if response:
                return Dummy(**response)
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def create(self, correlation_id, entity):
        timing = self._instrument(correlation_id, 'dummy.create')
        try:
            response = self._call(
                'POST',
                '/dummies',
                correlation_id,
                None,
                {
                    'body': entity
                }
            )
            if response:
                return Dummy(**response)
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def update(self, correlation_id, entity):
        timing = self._instrument(correlation_id, 'dummy.update')
        try:
            response = self._call(
                'PUT',
                '/dummies',
                correlation_id,
                None,
                {
                    'body': entity
                }
            )
            if response:
                return Dummy(**response)
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def delete_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        timing = self._instrument(correlation_id, 'dummy.delete_by_id')
        try:
            response = self._call(
                'DELETE',
                f'/dummies/{dummy_id}',
                correlation_id,
                None
            )
            if response:
                return Dummy(**response)
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def check_correlation_id(self, correlation_id: Optional[str]) -> str:
        timing = self._instrument(correlation_id, 'dummy.check_correlation_id')
        try:
            result = self._call(
                'get',
                f'/dummies/check/correlation_id',
                correlation_id,
                None
            )
            return None if not result else result.get('correlation_id')
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()
