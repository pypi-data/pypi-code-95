from __future__ import annotations

from limes_common.models import Model, Primitive, provider as Models
from limes_common.models import provider
from limes_common.models.provider import Transaction
from limes_common.models.http import GET, POST

class Endpoints(provider.Endpoints):
    LOGIN = 'login'
    AUTHENTICATE = 'authenticate'
    INIT = 'init'
    # ADD = 'add'
    LIST = 'list'
    CALL = 'call'
    SEARCH = 'search'
    RESET = 'reset'

class ServerRequest(Models.ProviderRequest):
    ClientId: str

class ServerResponse(Models.ProviderResponse):
    pass

class Init(Transaction):
    class Request(ServerRequest):
        def __init__(self) -> None:
            super().__init__(Endpoints.INIT, GET)
    class Response(ServerResponse):
        CsrfToken: str
        def __init__(self, token: str = '') -> None:
            self.CsrfToken = token

class Authenticate(Transaction):
    class Request(ServerRequest):
        def __init__(self) -> None:
            super().__init__(Endpoints.AUTHENTICATE, POST)

    class Response(ServerResponse):
        Success: bool
        Token: str
        FirstName: str
        LastName: str

class Login(Transaction):
    class Request(ServerRequest):
        ELabKey: str
        FirstName: str
        LastName: str
        def __init__(self) -> None:
            super().__init__(Endpoints.LOGIN, POST)

    class Response(ServerResponse):
        Success: bool
        def __init__(self, success: bool=False) -> None:
            super().__init__()
            self.Success = success

class ProviderInfo(Model):
    Name: str
    Schema: provider.Schema

class List(Transaction):
    class Request(ServerRequest):
        def __init__(self) -> None:
            super().__init__(Endpoints.LIST, POST)

    class Response(ServerResponse):
        Providers: list[ProviderInfo]
        def __init__(self) -> None:
            super().__init__()
            self.Providers = []

class Reset(Transaction):
    class Request(ServerRequest):
        def __init__(self) -> None:
            super().__init__(Endpoints.RESET, POST)

    class Response(List.Response):
        pass

class CallProvider(Transaction):
    class Request(ServerRequest):
        ProviderName: str
        Endpoint: str
        RequestPayload: Models.GenericRequest
        def __init__(self) -> None:
            super().__init__(Endpoints.CALL, POST)

    class Response(ServerResponse):
        ResponsePayload: Models.GenericResponse

class Search(Transaction):
    class Request(ServerRequest, Models.Search.Request):
        def __init__(self) -> None:
            super().__init__(Endpoints.SEARCH, POST)

    class Response(Models.Search.Response):
        pass