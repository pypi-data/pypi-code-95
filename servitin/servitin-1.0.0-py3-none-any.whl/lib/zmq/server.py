import datetime
import importlib
import sys
import traceback
import uuid
import json

from aiozmq import rpc as zmq_rpc
from jose import jwt
from functools import wraps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pydantic import ValidationError as PydanticValidationError


class AuthError(Exception):
    pass


class RequestError(Exception):
    pass


class ResponseError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, error, data):
        self.error = error
        self.data = data

    def __repr__(self):
        return self.error

    def __str__(self):
        return self.error


class ZMQServer(zmq_rpc.AttrHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = getattr(self, 'loop')
        self.log = getattr(self, 'log')
        self.app_name = getattr(self, 'app_name')

        try:
            self.ZMQ_CONN = getattr(settings, f'SERVITIN_{self.app_name.upper()}_ZMQ')
            self.ZMQ_HOST = self.ZMQ_CONN['HOST']
            self.ZMQ_PORT = self.ZMQ_CONN['PORT']
            self.ZMQ_SECRET = self.ZMQ_CONN['SECRET']
            self.ZMQ_ALG = self.ZMQ_CONN['CRYPTO_ALGORITHM']
            self.endpoints = self.load_endpoints()
            endpoints = ', '.join([e['name'] for e in self.endpoints]) if len(self.endpoints) else 'no endpoints declared!'

            self.zmq_server = self.loop.run_until_complete(
                zmq_rpc.serve_rpc(self, bind=f"{self.ZMQ_HOST}:{self.ZMQ_PORT}")
            )
            self.log.info(f"open: {self.ZMQ_HOST}:{self.ZMQ_PORT}, endpoints: {endpoints}", name='zmq')
        except AttributeError as e:
            raise ImproperlyConfigured(e.__repr__())
        except Exception as e:
            self.log.critical(f"can't start server on host: '{self.ZMQ_HOST}', port: '{self.ZMQ_PORT}', "
                              f"check settings, or network. {e.__str__()}", tb=traceback.format_exc(), name='zmq')
            sys.exit()

    def close(self):
        self.zmq_server.close()
        self.log.info(f"close: {self.ZMQ_HOST}:{self.ZMQ_PORT}", name='zmq')

    def load_endpoints(self):
        endpoints_module = f'{self.app_name}.zmq'
        try:
            m = importlib.import_module(endpoints_module)
            return [{'name': name, 'coro': coro} for name, coro in m.__dict__.items() if getattr(coro, '_zmq_endpoint', None)]
        except Exception as e:
            self.log.critical(f'load zmq module error: {e.__repr__()}', tb=traceback.format_exc(), name='zmq')
            sys.exit()

    def get_request(self, endpoint, data, request_id, received_dt):
        # auth and check data
        try:
            data = jwt.decode(data, self.ZMQ_SECRET, algorithms=self.ZMQ_ALG)
            if not isinstance(data, dict):
                raise RequestError('data must be a dictionary')
        except Exception:
            raise AuthError(f'data: {data}')

        # get decorated endpoint coro
        endpoints = [e['coro'] for e in self.endpoints if e['name'] == endpoint]
        if not len(endpoints):
            raise RequestError(f'endpoint {endpoint} not found')
        endpoint = endpoints[0]

        # make request
        request = Request(endpoint, data, self, request_id, received_dt)

        # validate request
        request.validate()

        return request

    @zmq_rpc.method
    async def endpoint(self, endpoint, data):

        request_id, received_dt = str(uuid.uuid4()), datetime.datetime.utcnow()
        response = None

        try:
            # get request
            request = self.get_request(endpoint, data, request_id, received_dt)

            # dispatch request
            _response = await request.endpoint

            # make response
            if isinstance(_response, Response):
                response = _response.serialized_data
            else:
                response = Response(request, _response, None).serialized_data

        except AuthError as e:
            self.log.critical(e.__repr__(), tb=traceback.format_exc(), id=request_id, name=f'@{endpoint}')
            response = Response(None, None, error=e.__repr__(), request_id=request_id, received_dt=received_dt).serialized_data

        except RequestError as e:
            self.log.error(e.__repr__(), id=request_id, name=f'@{endpoint}')
            response = Response(None, None, error=e.__repr__(), request_id=request_id, received_dt=received_dt).serialized_data

        except ValidationError as e:
            self.log.error(f'{e.__repr__()}, error data: {e.data}', id=request_id, name=f'@{endpoint}')
            response = Response(None, e.data, error=e.__repr__(), request_id=request_id, received_dt=received_dt).serialized_data

        except ResponseError as e:
            self.log.error(e.__repr__(), tb=traceback.format_exc(), id=request_id, name=f'@{endpoint}')
            response = Response(None, None, error=e.__repr__(), request_id=request_id, received_dt=received_dt).serialized_data

        except Exception as e:
            self.log.critical(e.__repr__(), tb=traceback.format_exc(), id=request_id, name=f'@{endpoint}')
            response = Response(None, None, error=e.__repr__(), request_id=request_id, received_dt=received_dt).serialized_data

        finally:
            return response


class Request:
    def __init__(self, endpoint, data, service, request_id, received_dt):
        self._endpoint = endpoint
        self.endpoint = None
        self.data = data
        self.service = service
        self.log = service.log
        self.request_id = request_id
        self.received_dt = received_dt
        self.validator = None
        self.set_endpoint(endpoint)

    def validate(self):
        validator = self._endpoint._zmq_endpoint.get('validator', None)
        if validator:
            try:
                validator(**self.data)
            except PydanticValidationError as e:
                raise ValidationError('ValidationError', data=e.errors())
            except Exception as e:
                raise RequestError(e.__repr__())

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint(self)


class Response:
    """
    Response format:
        {
            'request_id': request.request_id,
            'received_dt': request.received_dt.timestamp(),
            'error': error,  # None or error
            'data': data  # returned data if not error or error_data (if present) if error
        }

    """

    def __init__(self, request, data, error=None, request_id=None, received_dt=None):
        if request:
            self.data = {
                'request_id': request.request_id,
                'received_dt': request.received_dt.timestamp(),
                'error': error,
                'data': data
            }
        else:
            self.data = {
                'request_id': request_id,
                'received_dt': received_dt.timestamp(),
                'error': error,
                'data': data
            }
        self.error = error

        try:
            self.serialized_data = json.dumps(self.data)
        except Exception as e:
            raise ResponseError(f'Serialization error: {e.__repr__()}')


class ZmqEndpointDecorator:
    """
    Zmq endpoint decorator class
    """
    def __init__(self, coro, validator=None):
        self.coro = coro
        coro._zmq_endpoint = {'validator': validator}
        wraps(coro)(self)

    def __call__(self, request):
        return self.coro(request)


def zmq(coro=None, validator=None):
    """
    Wrapper for ZmqEndpointDecorator, need to get decorator arguments
    :param coro: zmq() coroutine
    :param validator: request validator
    :return: wrapped zmq() coroutine
    """
    if coro:
        return ZmqEndpointDecorator(coro)
    else:
        def wrapper(coro):
            return ZmqEndpointDecorator(coro, validator=validator)
        return wrapper
