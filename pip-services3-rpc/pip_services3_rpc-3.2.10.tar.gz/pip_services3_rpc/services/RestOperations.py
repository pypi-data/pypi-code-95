# -*- coding: utf-8 -*-

import json
from abc import ABC
from typing import Optional, Any, Callable

import bottle
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config.IConfigurable import IConfigurable
from pip_services3_commons.data.FilterParams import FilterParams
from pip_services3_commons.data.PagingParams import PagingParams
from pip_services3_commons.errors.BadRequestException import BadRequestException
from pip_services3_commons.errors.ConflictException import ConflictException
from pip_services3_commons.errors.NotFoundException import NotFoundException
from pip_services3_commons.errors.UnauthorizedException import UnauthorizedException
from pip_services3_commons.errors.UnknownException import UnknownException
from pip_services3_commons.refer import IReferences
from pip_services3_commons.refer.DependencyResolver import DependencyResolver
from pip_services3_commons.refer.IReferenceable import IReferenceable
from pip_services3_components.count.CompositeCounters import CompositeCounters
from pip_services3_components.log.CompositeLogger import CompositeLogger

from .HttpResponseSender import HttpResponseSender


class RestOperations(IConfigurable, IReferenceable, ABC):

    def __init__(self):
        super().__init__()
        self._logger: CompositeLogger = CompositeLogger()
        self._counters: CompositeCounters = CompositeCounters()
        self._dependency_resolver: DependencyResolver = DependencyResolver()

    def configure(self, config: ConfigParams):
        self._dependency_resolver.configure(config)

    def set_references(self, references: IReferences):
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)

    def get_param(self, param, default=None):
        return bottle.request.params.get(param, default)

    def _get_correlation_id(self) -> Optional[str]:
        """
        Returns correlationId from request

        :returns: Returns correlationId from request
        """
        correlation_id = bottle.request.query.get('correlation_id')
        if correlation_id is None or correlation_id == '':
            correlation_id = bottle.request.headers.get('correlation_id')

        return correlation_id

    def _get_filter_params(self) -> FilterParams:
        data = dict(bottle.request.query.decode())
        data.pop('correlation_id', None)
        data.pop('skip', None)
        data.pop('take', None)
        data.pop('total', None)
        return FilterParams(data)

    def _get_paging_params(self) -> PagingParams:
        params = dict(bottle.request.query.decode())
        skip = params.get('skip')
        take = params.get('take')
        total = params.get('total')
        return PagingParams(skip, take, total)

    def _get_data(self) -> Optional[str]:
        data = bottle.request.json
        if isinstance(data, str):
            return json.loads(bottle.request.json)
        elif bottle.request.json:
            return bottle.request.json
        else:
            return None

    def _send_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_result(result)

    def _send_empty_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_empty_result(result)

    def _send_created_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_created_result(result)

    def _send_deleted_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_deleted_result(result)

    def _send_error(self, error: Any = None) -> str:
        return HttpResponseSender.send_error(error)

    def _send_bad_request(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = BadRequestException(correlation_id, 'BAD_REQUEST', message)
        return self._send_error(error)

    def _send_unauthorized(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = UnauthorizedException(correlation_id, 'UNAUTHORIZED', message)
        return self._send_error(error)

    def _send_not_found(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = NotFoundException(correlation_id, 'NOT_FOUND', message)
        return self._send_error(error)

    def _send_conflict(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = ConflictException(correlation_id, 'CONFLICT', message)
        return self._send_error(error)

    def _send_session_expired(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = UnknownException(correlation_id, 'SESSION_EXPIRED', message)
        error.status = 440
        return self._send_error(error)

    def _send_internal_error(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = UnknownException(correlation_id, 'INTERNAL', message)
        return self._send_error(error)

    def _send_server_unavailable(self, message: str) -> str:
        correlation_id = self._get_correlation_id()
        error = ConflictException(correlation_id, 'SERVER_UNAVAILABLE', message)
        error.status = 503
        return self._send_error(error)

    def invoke(self, operation: str) -> Callable:
        for attr in dir(self):
            if attr in dir(self):
                return lambda param=None: getattr(self, operation)(param)
