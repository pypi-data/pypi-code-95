from rest_framework.test import APIRequestFactory
from django.urls.resolvers import ResolverMatch
from django.urls import reverse
import shortuuid
import uuid

def generate_uuid():
    return str(uuid.uuid4())

def generate_short_uuid():
    return str(shortuuid.uuid())


def create_uuid(long: bool = False, value: str = None):
    if isinstance(value, bool) and not value:
        return None
    elif value == None or (isinstance(value, bool) and value):
        return generate_uuid() if long else generate_short_uuid()
    else:
        return value
    
class MockAuthorizedRequest:

    GET ='get'
    POST = 'post'
    DELETE = 'delete'
    PUT = 'put'

    format='json'

    factory = APIRequestFactory()

    def __init__(self, bartab_user: str = generate_uuid()):
        self.bartab_user = bartab_user

    def __get_request_by_request_type(self, request_type: str, endpoint_name: str, data: dict, url_kwargs: dict):        
        if request_type == self.GET:
            request = self.factory.get(
                reverse(endpoint_name, kwargs=url_kwargs), data,  format=self.format)
        elif request_type == self.POST:
            request = self.factory.post(
                reverse(endpoint_name, kwargs=url_kwargs), data,  format=self.format)
        elif request_type == self.DELETE:
            request = self.factory.delete(
                reverse(endpoint_name, kwargs=url_kwargs), data,  format=self.format)
        elif request_type == self.PUT:
            request = self.factory.put(
                reverse(endpoint_name, kwargs=url_kwargs), data,  format=self.format)
        else:
            raise ValueError(f"Invalid request type {request_type}")

        request.resolver_match = ResolverMatch(None, None, url_kwargs)

        request.bartab_user = self.bartab_user

        return request


    def get_post_request(self, endpoint_name: str, data: dict = {}, url_kwargs: dict = {}):
        return self.__get_request_by_request_type(self.POST, endpoint_name, data, url_kwargs)
    
    def get_get_request(self, endpoint_name: str, data: dict = {}, url_kwargs: dict = {}):
        return self.__get_request_by_request_type(self.GET, endpoint_name, data, url_kwargs)

    def get_put_request(self, endpoint_name: str, data: dict = {}, url_kwargs: dict = {}):
        return self.__get_request_by_request_type(self.PUT, endpoint_name, data, url_kwargs)

    def get_delete_request(self, endpoint_name: str, data: dict = {}, url_kwargs: dict = {}):
        return self.__get_request_by_request_type(self.DELETE, endpoint_name, data, url_kwargs)


class MockMicroserviceResponse:
    def __init__(self, data: dict = {}, status_code: int = 200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data