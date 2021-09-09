from typing import Union


class UBotHTTPResponse:
    def __init__(self,
                 content: Union[bytes, str],
                 code: int = 200,
                 **kwargs):
        self._content = content
        self._code = code
        self._kwargs = kwargs

    @property
    def content(self) -> Union[bytes, str]:
        return self._content

    @property
    def code(self) -> int:
        return self._code

    @property
    def params(self) -> dict:
        return self._kwargs


DEFAULT_SUCCESS_HTTP_RESPONSE = UBotHTTPResponse(b'ok')
