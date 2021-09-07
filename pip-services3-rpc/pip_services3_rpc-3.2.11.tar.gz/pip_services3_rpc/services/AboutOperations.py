# -*- coding: utf-8 -*-
import datetime
from socket import AddressFamily
from typing import Callable

import bottle
import psutil
from pip_services3_commons.refer.Descriptor import Descriptor
from pip_services3_commons.refer.IReferences import IReferences
from pip_services3_components.info.ContextInfo import ContextInfo

from .HttpRequestDetector import HttpRequestDetector
from .RestOperations import RestOperations


class AboutOperations(RestOperations):

    def __init__(self):
        super().__init__()
        self.__context_info: ContextInfo = None

    def set_references(self, references: IReferences):
        super(AboutOperations, self).set_references(references)

        self.__context_info = references.get_one_optional(
            Descriptor('pip-services', 'context-info', '*', '*', '*')
        )

    def get_about_operation(self) -> Callable:
        return self.get_about

    def __is_local_adress(self, addr: str, mask: str):
        addr = addr.split('.')
        if not ((int(addr[0]) == 10 or int(addr[0]) == 127) or (
                int(addr[0]) == 172 and 16 <= int(addr[1]) <= 31) or (
                        int(addr[0]) == 192 and int(addr[1]) == 168) or (
                        int(addr[0]) == 100 and 64 <= int(addr[1]) <= 127)) or mask not in ['255.0.0.0',
                                                                                            '255.240.0.0',
                                                                                            '255.255.0.0',
                                                                                            '255.192.0.0']:
            return True

        return False

    def __get_network_adresses(self) -> list:

        interfaces = psutil.net_if_addrs()
        addresses = []
        for key in interfaces.keys():
            for adress in interfaces[key]:
                if AddressFamily.AF_INET == adress.family and self.__is_local_adress(adress.address, adress.netmask):
                    addresses.append(adress.address)

        return addresses

    def get_about(self) -> str:

        req = bottle.request
        about = {
            'server': {
                'name': self.__context_info.name if not (self.__context_info is None) else "unknown",
                'description': self.__context_info.description if not (self.__context_info is None) else "",
                'properties': self.__context_info.properties if not (self.__context_info is None) else "",
                'uptime': self.__context_info.uptime if not (self.__context_info is None) else None,
                'start_time': self.__context_info.start_time if not (self.__context_info is None) else None,
                'current_time': datetime.datetime.now().isoformat(),
                'protocol': req.method,
                'host': HttpRequestDetector.detect_server_host(req),
                'port': HttpRequestDetector.detect_server_port(req),
                'addresses': self.__get_network_adresses(),
                'url': req.url
            },
            'client': {
                'address': HttpRequestDetector.detect_address(req),
                'client': HttpRequestDetector.detect_browser(req),
                'platform': HttpRequestDetector.detect_platform(req),
                'user': req.get_header('user')
            }
        }
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 200

        return self._send_result(about)
