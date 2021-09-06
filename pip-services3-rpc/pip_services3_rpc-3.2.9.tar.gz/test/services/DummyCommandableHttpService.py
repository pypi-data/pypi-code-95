# -*- coding: utf-8 -*-
"""
    test.rest.DummyCommandableHttpService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy commandable HTTP service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer import Descriptor

from pip_services3_rpc.services import CommandableHttpService


class DummyCommandableHttpService(CommandableHttpService):

    def __init__(self):
        super(DummyCommandableHttpService, self).__init__('dummy')
        self._dependency_resolver.put('controller', Descriptor('pip-services-dummies', 'controller', '*', '*', '*'))

    def register(self):
        if not self._swagger_auto and self._swagger_enabled:
            self._register_open_api_spec('swagger yaml content')

        super().register()
