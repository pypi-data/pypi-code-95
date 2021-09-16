#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#

import requests
from astersay.utils import import_string


class BaseHttpClient:
    ALLOWED_METHODS = ('get', 'post', 'put', 'path', 'delete')
    auth = None
    parser = None
    method = 'get'
    get_args = None
    post_args = None

    def __init__(self, config):
        assert 'url' in config
        self.url = config['url']
        method = config.get('method')
        if method:
            assert method in self.ALLOWED_METHODS
            self.method = method
        if 'auth' in config:
            self.init_auth(config['auth'])
        if 'parser' in config:
            self.init_parser(config['parser'])
        if 'get_args' in config:
            self.get_args = config['get_args']
        if 'post_args' in config:
            self.post_args = config['post_args']

    def init_auth(self, config):
        auth = import_string(config['class'])
        auth_conf = config.get('settings', {})
        self.auth = auth(**auth_conf)

    def init_parser(self, config: dict):
        parser = import_string(config.get('class'))
        self.parser = parser(config.get('settings'))

    def make_request(self, variables):
        url = self.url.format(**variables)
        params = self.build_request_params(variables)
        response = requests.request(self.method, url, timeout=(2, 5), **params)
        if response.status_code in (200, 201, 203):
            """
            если в настройках не был указан парсер, возвращаем None вместо текста ответа
            """
            result = self.parser.parse(response.text) if self.parser else None
            return True, result
        if response.status_code == 204:
            return True, None
        return False, None

    def build_request_params(self, variables):
        params = {}
        if self.get_args:
            params['params'] = {key: val.format(**variables) for key, val in self.get_args.items()}
        if self.post_args:
            params['data'] = {key: val.format(**variables) for key, val in self.post_args.items()}
        if self.auth:
            key, val = self.auth.get_auth_param()
            if key in params:
                """
                параметры авторизации могут передаваться в GET или POST, тогда их нужно добаить к существующим
                """
                assert isinstance(val, dict)
                params[key] = {**params[key], **val}
            else:
                params[key] = val

        return params
