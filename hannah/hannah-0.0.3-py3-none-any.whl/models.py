from functools import lru_cache

import httpx
from cached_property import cached_property

from hannah.parsers import SwaggerParser, SwaggerOperation
from hannah.exceptions import OperationNotFound


def http_request_template(http_session, op: SwaggerOperation):

    async def request_wrapper(**kwargs):

        path_params: dict = {k: v for k, v in kwargs.items() if k in op.path_params}
        query_params: dict = {k: v for k, v in kwargs.items() if k in op.query_params}
        headers: dict = {k: v for k, v in kwargs.items() if k in op.headers}
        payload = kwargs.get('requestBody', kwargs.get(op.body, {}))

        for param in kwargs.get('parameters', []):
            if param['in'] == 'path':
                path_params.update(**{param['name']: param['value']})
            if param['in'] == 'query':
                query_params.update(**{param['name']: param['value']})
            if param['in'] == 'header':
                headers.update(**{param['name']: param['value']})

        return await http_session.request(op.method, op.uri.format(**path_params), params=query_params,
                                          json=payload, headers=headers, timeout=120)

    return request_wrapper


class SwaggerService:

    def __init__(self, name: str, base_url: str, http_session=None, spec: dict=None):
        self.name = name
        self.base_url = base_url
        self.http_session = http_session
        self.swagger_spec = spec
        http_session.set_base_url(self.base_url)

    @classmethod
    def from_url(cls, name: str, base_url: str, http_session=None, swagger_path=None):
        spec = cls.get_api_doc(f'{base_url}{swagger_path}')
        return cls(name, base_url, http_session, spec)

    @cached_property
    def swagger(self) -> SwaggerParser:
        if not self.swagger_spec:
            self.swagger_spec = self.get_api_doc(f'/v2/api-docs')
        return SwaggerParser(spec=self.swagger_spec)

    @staticmethod
    def get_api_doc(url) -> dict:
        r = httpx.get(url)
        r.raise_for_status()
        return r.json()

    @lru_cache(maxsize=128)
    def get_operation(self, name):
        if name not in self.swagger.operations:
            raise OperationNotFound(f'{self.name} service has no operation named {name}')
        return http_request_template(self.http_session, self.swagger.operations[name])

    def __getattr__(self, name: str):
        return self.get_operation(name) if name in self.swagger.operations else self.__getattribute__(name)
