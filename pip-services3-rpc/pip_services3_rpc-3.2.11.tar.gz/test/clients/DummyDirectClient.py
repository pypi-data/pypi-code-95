# -*- coding: utf-8 -*-
"""
    test.rest.DummyDirectClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy direct client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.data import FilterParams, PagingParams, DataPage
from pip_services3_commons.refer import Descriptor

from pip_services3_rpc.clients import DirectClient
from .IDummyClient import IDummyClient
from .. import Dummy


class DummyDirectClient(DirectClient, IDummyClient):

    def __init__(self):
        super(DummyDirectClient, self).__init__()
        self._dependency_resolver.put('controller', Descriptor('pip-services-dummies', 'controller', '*', '*', '*'))

    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams) -> DataPage:
        timing = self._instrument(correlation_id, 'dummy.get_page_by_filter')
        try:
            return self._controller.get_page_by_filter(correlation_id, filter, paging)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()

    def get_one_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        timing = self._instrument(correlation_id, 'dummy.get_one_by_id')
        try:
            return self._controller.get_one_by_id(correlation_id, dummy_id)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()

    def create(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        timing = self._instrument(correlation_id, 'dummy.create')
        try:
            return self._controller.create(correlation_id, item)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()

    def update(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        timing = self._instrument(correlation_id, 'dummy.update')
        try:
            return self._controller.update(correlation_id, item)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()

    def delete_by_id(self, correlation_id: Optional[str], dummy_id: str) -> Dummy:
        timing = self._instrument(correlation_id, 'dummy.delete_by_id')
        try:
            return self._controller.delete_by_id(correlation_id, dummy_id)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()

    def check_correlation_id(self, correlation_id: Optional[str]) -> str:
        timing = self._instrument(correlation_id, 'dummy.check_correlation_id')
        try:
            return self._controller.check_correlation_id(correlation_id)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()
