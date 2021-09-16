#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#


class BaseAuth:
    def get_auth_param(self):
        """
        Метод должен вернуть два значение: ключ - куда добавляются параметры в запрос для модуля requests,
        например headers|params|auth|data (разные случаи бывают)
        И собственно отправляемые значение, может быть словарь/кортеж/список
        """
        raise NotImplementedError


class TokenHeaderAuth(BaseAuth):
    token = None
    auth_header = 'Bearer '

    def __init__(self, token, auth_header=None):
        self.token = token
        if auth_header:
            self.auth_header = auth_header

    def get_auth_param(self):
        assert self.token
        params = {
            'Authorization': f"{self.auth_header}{self.token}"
        }
        return 'headers', params


class TokenAuth(BaseAuth):
    ALLOWED_AUTH_KEYS = ('params', 'data')
    token = None
    token_key = 'token'
    auth_key = 'params'

    def __init__(self, token, token_key=None, auth_key=None):
        self.token = token
        if token_key:
            self.token_key = token_key
        if auth_key:
            assert auth_key in self.ALLOWED_AUTH_KEYS
            self.auth_key = auth_key

    def get_auth_param(self):
        assert self.token
        params = {
            self.token_key: self.token
        }
        return self.auth_key, params


class LoginPassAuth(BaseAuth):
    username_key = 'username'
    password_key = 'password'

    def __init__(self, username, password, username_key=None, password_key=None):
        self.username = username
        self.password = password

        if username_key:
            self.username_key = username_key
        if password_key:
            self.password_key = password_key

    def get_auth_param(self):
        params = {
            self.username_key: self.username,
            self.password_key: self.password
        }
        return 'params', params


class HttpBasicAuth(BaseAuth):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_auth_param(self):
        params = (self.username, self.password)
        return 'auth', params
