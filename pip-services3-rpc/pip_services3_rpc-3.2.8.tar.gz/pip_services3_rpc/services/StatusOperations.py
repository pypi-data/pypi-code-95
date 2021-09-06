# -*- coding: utf-8 -*-

import datetime
import json
from typing import Callable

import bottle
import pytz
from pip_services3_commons.convert.StringConverter import StringConverter
from pip_services3_commons.refer.Descriptor import Descriptor
from pip_services3_commons.refer.IReferences import IReferences
from pip_services3_components.info.ContextInfo import ContextInfo

from .RestOperations import RestOperations


class StatusOperations(RestOperations):

    def __init__(self):
        super(StatusOperations, self).__init__()

        self.__start_time: datetime.datetime = datetime.datetime.now()
        self.__references2: IReferences = None
        self.__context_info: ContextInfo = None

        self._dependency_resolver.put(
            'context-info',
            Descriptor('pip-services', 'context-info', 'default', '*', '1.0')
        )

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """

        self.__references2 = references
        super(StatusOperations, self).set_references(references)

        self.__context_info = self._dependency_resolver.get_one_optional('context-info')

    def get_status_operation(self) -> Callable:
        return self.__status

    def __status(self) -> str:
        """
        Handles status requests
        """
        _id = self.__context_info.context_id if not (self.__context_info is None) else ''
        name = self.__context_info.name if not (self.__context_info is None) else 'unknown'
        description = self.__context_info.description if not (self.__context_info is None) else ''
        uptime = datetime.datetime.fromtimestamp((
                datetime.datetime.now().timestamp() - self.__start_time.timestamp()),
            pytz.utc).strftime("%H:%M:%S")
        properties = self.__context_info.properties if not (self.__context_info is None) else ''

        components = []
        if self.__references2 is not None:
            for locator in self.__references2.get_all_locators():
                components.append(locator.__str__)

        status = {'id': _id,
                  'name': name,
                  'description': description,
                  'start_time': StringConverter.to_string(self.__start_time),
                  'current_time': StringConverter.to_string(datetime.datetime.now()),
                  'uptime': uptime,
                  'properties': properties,
                  'components': components}
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 200
        return json.dumps(status)
