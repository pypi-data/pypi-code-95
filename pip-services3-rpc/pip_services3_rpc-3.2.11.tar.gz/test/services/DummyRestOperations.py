# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
import threading

from pip_services3_commons.data import FilterParams, PagingParams, IdGenerator
from pip_services3_commons.refer import Descriptor
from pip_services3_rpc.services import RestOperations, AboutOperations,\
                                        StatusOperations, HeartBeatOperations


class DummyRestOperations(RestOperations, ABC):

    _controller = None

    def __init__(self):
        super(DummyRestOperations, self).__init__()
        self._dependency_resolver.put('controller', Descriptor('pip-services-dummies', 'controller', 'default', '*', '*'))

    def set_references(self, references):
        super(DummyRestOperations, self).set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def get_page_by_filter(self):
        correlation_id = self._get_correlation_id()
        filters = self._get_filter_params()
        paging = self._get_paging_params()
        return self._send_result(self._controller.get_page_by_filter(correlation_id, filters, paging))

    def get_one_by_id(self, id):
        correlation_id = self._get_correlation_id()
        return self._send_result(self._controller.get_one_by_id(correlation_id, id))

    def create(self):
        correlation_id = self._get_correlation_id()
        entity = self._get_data()
        return self._send_created_result(self._controller.create(correlation_id, entity))

    def update(self, id):
        correlation_id = self._get_correlation_id()
        entity = self._get_data()
        return self._send_result(self._controller.update(correlation_id, entity))

    def delete_by_id(self, id):
        correlation_id = self._get_correlation_id()
        self._controller.delete_by_id(correlation_id, id)
        return self._send_deleted_result()

    def handled_error(self):
        raise UnsupportedError('NotSupported', 'Test handled error')

    def unhandled_error(self):
        raise TypeError('Test unhandled error')

    def send_bad_request(self, message):
        return self._send_bad_request(message)

 
