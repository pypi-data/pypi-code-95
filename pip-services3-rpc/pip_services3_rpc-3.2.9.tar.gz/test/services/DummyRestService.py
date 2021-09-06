# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import bottle
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import FilterParams, PagingParams
from pip_services3_commons.refer import Descriptor
from pip_services3_commons.validate import ObjectSchema, FilterParamsSchema

from pip_services3_rpc.services import AboutOperations
from pip_services3_rpc.services import RestService
from .. import IDummyController, Dummy
from ..DummySchema import DummySchema


class DummyRestService(RestService):

    def __init__(self):
        super(DummyRestService, self).__init__()
        self._dependency_resolver.put('controller',
                                      Descriptor("pip-services-dummies", "controller", "default", "*", "*"))

        self._controller: IDummyController = None
        self._number_of_calls = 0
        self._swagger_content = None
        self._swagger_path = None

    def configure(self, config):
        super().configure(config)

        self._swagger_content = config.get_as_nullable_string("swagger.content")
        self._swagger_path = config.get_as_nullable_string('swagger.path')

    def set_references(self, references):
        super().set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def get_number_of_calls(self) -> int:
        return self._number_of_calls

    def _increment_number_of_calls(self):
        self._number_of_calls += 1

    def __get_page_by_filter(self):
        result = self._controller.get_page_by_filter(
            self._get_correlation_id(),
            FilterParams(bottle.request.query.dict),
            PagingParams(bottle.request.query.get('skip'),
                         bottle.request.query.get('take'),
                         bottle.request.query.get('total')),
        )

        return self.send_result(result)

    def __get_one_by_id(self, dummy_id):
        result = self._controller.get_one_by_id(
            self._get_correlation_id(),
            dummy_id,
        )
        return self.send_result(result)

    def __create(self):
        data = json.loads(bottle.request.json).get('body')
        entity = Dummy(**data)

        result = self._controller.create(
            self._get_correlation_id(),
            entity,
        )
        return self.send_created_result(result)

    def __update(self):
        data = json.loads(bottle.request.json).get('body')
        entity = Dummy(**data)

        result = self._controller.update(
            self._get_correlation_id(),
            entity,
        )

        return self.send_deleted_result(result)

    def __delete_by_id(self, dummy_id):
        result = self._controller.delete_by_id(
            self._get_correlation_id(),
            dummy_id,
        )
        return self.send_deleted_result(result)

    def __check_correlation_id(self):
        try:
            result = self._controller.check_correlation_id(self._get_correlation_id())
            return self.send_result({'correlation_id': result})
        except Exception as err:
            return self.send_error(err)

    def register(self):
        self.register_interceptor('/dummies', self._increment_number_of_calls)

        self.register_route('get', '/dummies', ObjectSchema(True)
                            .with_optional_property("skip", TypeCode.String)
                            .with_optional_property("take", TypeCode.String)
                            .with_optional_property("total", TypeCode.String)
                            .with_optional_property("body", FilterParamsSchema()), self.__get_page_by_filter)

        self.register_route('get', '/dummies/<dummy_id>', ObjectSchema(True)
                            .with_required_property("dummy_id", TypeCode.String),
                            self.__get_one_by_id)

        self.register_route('post', '/dummies', ObjectSchema(True)
                            .with_required_property("body", DummySchema()),
                            self.__create)

        self.register_route('put', '/dummies', ObjectSchema(True)
                            .with_required_property("body", DummySchema()),
                            self.__update)

        self.register_route('delete', '/dummies/<dummy_id>', ObjectSchema(True)
                            .with_required_property("dummy_id", TypeCode.String),
                            self.__delete_by_id)

        self.register_route("get", "/dummies/check/correlation_id",
                            ObjectSchema(True), self.__check_correlation_id)

        self.register_route('post', '/about', None, AboutOperations().get_about)

        if self._swagger_content:
            self._register_open_api_spec(self._swagger_content)

        if self._swagger_path:
            self._register_open_api_spec_from_file(self._swagger_path)
