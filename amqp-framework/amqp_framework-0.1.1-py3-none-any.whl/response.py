import traceback
from typing import Union

from amqp_framework.http_status import HTTPStatus


class Response:

    def __init__(self, status: Union[HTTPStatus, int], headers: dict = None, data: dict = None):

        if isinstance(status, HTTPStatus):
            self._status = status.value
        else:
            self._status = HTTPStatus(status)

        if headers is None:
            headers = {}
        else:
            assert isinstance(headers, dict), 'Unsupported type {0} for headers, dict required.' \
                .format(type(headers))
        self._headers = headers

        if data is None:
            data = {}
        else:
            assert isinstance(data, dict), 'Unsupported type {0} for data, dict required.' \
                .format(type(data))
        self.data = data

    def __repr__(self):
        return "<Response(status='{0}', data='{1}', headers='{2}')>".format(
            self._status, self.data, self._headers
        )

    @property
    def headers(self):
        return {
            **self._headers,
            'status': self._status,
        }

    @classmethod
    def from_exc(cls, status: Union[HTTPStatus, int], exc: Exception, headers=None, data=None):
        if not data:
            data = {}

        return cls(status=status, headers=headers, data={
            **data,
            **{
                'exc_info': getattr(exc, 'code', None) or status.phrase,
                'exc_traceback': traceback.format_exc(),
            },
        })
