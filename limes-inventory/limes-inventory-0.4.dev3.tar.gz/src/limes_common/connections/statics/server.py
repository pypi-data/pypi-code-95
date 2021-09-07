import requests as Requests
import uuid
from getpass import getuser
import os
from typing import Any, Callable, TypeVar, Union

from ..http import HttpConnection
from ... import config
from limes_common.models import Primitive, server as Models, provider as ProviderModels
# from limes_common.models.endpoints import ServerEndpoint

T = TypeVar('T')
class ServerConnection(HttpConnection):
    def __init__(self) -> None:
        super().__init__(config.SERVER_URL)
        self._id = ''
        self._csrf = ''
        self.Ready = False
        self.Reconnect()

    def Reconnect(self) -> bool:
        self._id = ('%012x:%s:%s' % (uuid.getnode(), getuser(), os.getppid()))
        self._csrf = ''
        req = Models.Init.Request()
        rawRes = self.MakeRequest(req, init=True)
        self.Ready = False
        if isinstance(rawRes.Body, dict):
            res = Models.Init.Response.Parse(rawRes.Body)
            if res.CsrfToken is not None and res.CsrfToken != '':
                self._csrf = res.CsrfToken
                self.Ready = True
        return self.Ready

    def _makeHeader(self):
        return {config.CSRF_NAME: self._csrf}

    def _makeJson(self, data: Models.ServerRequest) -> dict[str, Any]:
        data.ClientId = self._id
        d = data.ToDict()
        return d

    def MakeRequest(self, request: ProviderModels.ProviderRequest, init=False) -> ProviderModels.GenericResponse:
        def doErr():
            errmsg = 'failed to connect to limes server'
            return ProviderModels.GenericResponse(code=503, error=errmsg)

        if not self.Ready and not init:
            return doErr()

        try:
            return super().MakeRequest(request)
        except Requests.exceptions.ConnectionError:
            return doErr()
        except KeyboardInterrupt:
            return ProviderModels.GenericResponse(code=0, error='user interrupt')

    def Search(self, query: str):
        transaction = Models.Search
        req = transaction.Request()
        req.Query = query
        return self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )

    def Authenticate(self):
        transaction = Models.Authenticate
        return self._makeParseRequest(
            transaction.Request(),
            transaction.Response.Parse,
            transaction.Response()
        )

    def Login(self, firstName: str, lastName: str, token: str):
        req = Models.Login.Request()
        req.ELabKey = token
        req.FirstName = firstName
        req.LastName = lastName
        transaction = Models.Login
        return self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )

    def List(self):
        transaction = Models.List
        return self._makeParseRequest(
            transaction.Request(),
            transaction.Response.Parse,
            transaction.Response()
        )

    def ReloadProviders(self):
        transaction = Models.Reset
        return self._makeParseRequest(
            transaction.Request(),
            transaction.Response.Parse,
            transaction.Response()
        )

    def CallProvider(self, providerName: str, providerEndpoint: str, body: Primitive):
        transaction = Models.CallProvider
        req = transaction.Request()
        req.ProviderName = providerName
        payload = ProviderModels.GenericRequest()
        payload.TargetEndpoint = providerEndpoint
        payload.Body = body
        req.RequestPayload = payload
        return self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )
