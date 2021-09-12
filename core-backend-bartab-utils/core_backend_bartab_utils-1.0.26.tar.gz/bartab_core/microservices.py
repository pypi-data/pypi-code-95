from . import api_config as microservices_config
from rest_framework.exceptions import APIException
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from rest_framework import status
from http.client import responses
import requests


class MicroserviceServiceUnavailable(APIException):
    status_code = 502
    default_code = 'service_unavailable'


class MicroserviceResponse:
    def __init__(self,
                 response,
                 exception,
                 ):
        if status.is_server_error(response.status_code):
            raise exception
        else:
            for key in response.__dict__:
                setattr(self, key, response.__dict__[key])

            self.response = response

    def json(self):
        try:
            return self.response.json()
        except:
            if status.is_success(self.response.status_code):
                return None
            else:
                return {'detail': responses[self.status_code]}

    def close(self):
        self.response.close()

    def iter_content(self):
        return self.response.iter_content()

    def iter_lines(self):
        return self.response.iter_lines()

    def raise_for_status(self):
        return self.response.raise_for_status()


class AbstractMicroservice:

    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'

    def __init__(self, *,
                 url_prefix,
                 localhost_port,
                 service_name,
                 exception,
                 api_version,
                 service_description
                 ):

        self.service_description = service_description

        try:
            self.api_key = microservices_config.get_api_key(service_name)
            self.valid_connection = True
        except ImproperlyConfigured:
            self.valid_connection = False
            
            if settings.DEBUG:
                self.invalid_configuration_error_message = microservices_config.get_invalid_configuration_error_message(
                    service_name)
            else:
                self.invalid_configuration_error_message = "{} service is currently unaviable, please try again later.".format(
                    self.service_description).capitalize()

        self.endpoint = microservices_config.get_endpoint(
            url_prefix=url_prefix,
            api_version=api_version,
            localhost_port=localhost_port
        )

        self.exception = exception

    def __make_endpoint(self, path, request_type):
        if request_type == self.POST and len(path) > 0 and path[-1] != '/':
            path = "{}/".format(path)

        return '{0}/{1}'.format(self.endpoint, path)

    def __make_request(self,
                       path,
                       request,
                       request_type):

        if not self.valid_connection:
            raise MicroserviceServiceUnavailable(self.invalid_configuration_error_message)

        headers = {
            'content-type': 'application/json',
            settings.API_KEY_PARAM_NAME: self.api_key
        }

        if request != None:
            data = request.data
            params = request.query_params

            bearer_header = request.META.get('HTTP_AUTHORIZATION')
            if bearer_header != None and bearer_header != '':
                headers['Authorization'] = bearer_header
        else:
            data = None
            params = None

        if request_type == self.POST:
            response = requests.post(
                self.__make_endpoint(path, self.POST),
                json=data,
                params=params,
                headers=headers
            )
        elif request_type == self.PUT:
            response = requests.put(
                self.__make_endpoint(path, self.PUT),
                json=data,
                params=params,
                headers=headers
            )
        elif request_type == self.DELETE:
            response = requests.delete(
                self.__make_endpoint(path, self.DELETE),
                json=data,
                params=params,
                headers=headers
            )
        else:
            response = requests.get(
                self.__make_endpoint(path, self.GET),
                json=data,
                params=params,
                headers=headers
            )

        return MicroserviceResponse(response, self.exception)

    def get(self, path, request=None):
        return self.__make_request(path, request, self.GET)

    def post(self, path, request=None):
        return self.__make_request(path, request, self.POST)

    def put(self, path, request=None):
        return self.__make_request(path, request, self.PUT)

    def delete(self, path, request=None):
        return self.__make_request(path, request, self.DELETE)

    class Meta:
        abstract = True
