from django.http import HttpRequest, QueryDict
from rest_framework.request import Request

def get_visitor_ip_address(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_pk_from_url(request) -> str:
    return request.resolver_match.kwargs.get('pk')


def get_named_id_from_url(request, name: str, allow_pk: bool = False) -> str:
    value = request.resolver_match.kwargs.get(name)

    if value != None:
        return value

    id_posfix = '_id'
    if len(name) < len(id_posfix) or name[len(name) - len(id_posfix):] != id_posfix:
        name = f'{name}{id_posfix}'
        value = request.resolver_match.kwargs.get(name)

    if value != None or (value == None and not allow_pk):
        return value

    return request.resolver_match.kwargs.get('pk')


def get_id_from_obj(obj) -> str:
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        if 'uuid' in obj:
            return obj['uuid']
        elif 'pk' in obj:
            return obj['pk']

    try:
        return obj.uuid
    except:
        return None


def create_get_request_with_query_params(query_params: dict = None) -> Request:
    http_request = HttpRequest()

    if query_params != None and len(query_params.keys()) > 0:
        http_request.GET = QueryDict(
            "&".join(map(lambda q: f"{q}={query_params[q]}", query_params.keys())))
    return Request(http_request)
