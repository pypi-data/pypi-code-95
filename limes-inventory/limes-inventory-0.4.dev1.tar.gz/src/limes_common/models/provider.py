from __future__ import annotations
from typing import Union

from requests.models import codes

from . import Model, Primitive
    
class Endpoints:
    GET_SCHEMA = 'schema'
    GENERIC = 'generic'
    SEARCH = 'search'

    @classmethod
    def Paths(cls):
        return [i[1] for i in filter(lambda i: i[0].isupper(), cls.__dict__.items())]

class ProviderRequest(Model):
    TargetEndpoint: str
    Method: str
    QueryParams: dict

    def __init__(self, endpoint: str='', method: str='', queryParams:dict={}) -> None:
        super().__init__()
        self.TargetEndpoint = endpoint
        self.Method = method
        self.QueryParams = queryParams

class GenericRequest(ProviderRequest):
    Body: Primitive

    def __init__(self, endpoint: str=Endpoints.GENERIC, method: str='', body: Primitive={}) -> None:
        super().__init__()
        self.Body = body
        self.TargetEndpoint = endpoint
        self.Method = method

class ProviderResponse(Model):
    Code: int
    Error: str
    Type: str

    def ToDict(self) -> dict:
        self.Type = self.GetType()
        return super().ToDict() 

    @classmethod
    def GetType(cls):
        return str(cls)

class GenericResponse(ProviderResponse):
    Body: Primitive

    def __init__(self, body: Primitive={}, code: int=200, error: str='') -> None:
        super().__init__()
        self.Body = body
        self.Code = code
        self.Error = error

    def BodyAsDict(self) -> dict:
        if isinstance(self.Body, dict):
            return self.Body
        else:
            return {'value': self.Body}

class Transaction:
    class Request(GenericRequest):
        pass

    class Response(GenericResponse):
        pass

DataSchema = Union[str, dict]
class Service(Model):
    Endpoint: str
    Input: DataSchema
    Output: DataSchema
    def __init__(self, endpoint: str='', input: DataSchema={}, output: DataSchema={}) -> None:
        super().__init__()
        self.Endpoint = endpoint
        self.Input = input
        self.Output = output

class Schema(ProviderResponse):
    Services: list[Service]
    def __init__(self, services: list[Service]=[]) -> None:
        super().__init__()
        self.Services = services

class Search(Transaction):
    class Request(ProviderRequest):
        Query: str
        Parameters: Primitive

    class Hit(Model):
        DataType: str
        Data: list[dict]

    class Response(ProviderResponse):
        Hits: dict[str, Search.Hit]
        def AddFrom(self, other: Search.Response):
            if self.Hits is None and 'Hits' in other.__dict__:
                self.Hits = other.Hits
            else:
                for k, v in other.Hits.items():
                    i = 2
                    key = k
                    while key in self.Hits:
                        key = '%s_%s' % (k, i)
                        i+=1
                    self.Hits[key] = v

            if self.Code == 200:
                self.Code = other.Code
                if 'Error' in other.__dict__:
                    self.Error = other.Error
            return self