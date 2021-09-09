import logging
import os

from channels.layers import get_channel_layer
from django.conf import settings
from django.db import connection, transaction
from django.http import Http404
from ngs.tools.snowflake import snowflake
from redis import Redis
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet as GViewSet

from iacs.redis import REDIS_CONNECTION_POOL
from .pagination import PageNumberPaginationExtension


def set_rollback():
    atomic_requests = connection.settings_dict.get('ATOMIC_REQUESTS', False)
    if atomic_requests and connection.in_atomic_block:
        transaction.set_rollback(True)


def exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        return Response({'msg': exc.detail}, status=exc.status_code)

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None


def get_params(request):
    """
    ### 将request中的参数提取到一个字典

    :return: 参数字典
    """
    data = request.data
    results = {}
    if isinstance(data, dict):
        for key in data.keys():
            results[key] = data.get(key, None)
    data_get = {k: v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
    results_get = {}
    if isinstance(data_get, dict):
        for key in data_get.keys():
            results_get[key] = data_get.get(key, None)
    results.update(results_get)
    return results


class GenericViewSet(GViewSet):
    pagination_class = PageNumberPaginationExtension
    renderer_classes = (JSONRenderer,)
    known_actions_name = None

    def __init__(self, *args, **kwargs):
        self.redis = Redis(connection_pool=REDIS_CONNECTION_POOL)
        self.layer = get_channel_layer()
        self.logger = logging.getLogger(settings.IACS_SETTINGS["RUNNING_LOG_NAME"])
        self.error = logging.getLogger(settings.IACS_SETTINGS["ERROR_LOG_NAME"])
        super(GenericViewSet, self).__init__(*args, **kwargs)

    def save_file_in_request(self):
        files = {}
        for key, file in self.request.FILES.items():
            file_name = f'tmp__{self.__class__.__name__}.{self.action}__{snowflake()}__{file.name}'
            with open(os.path.join(settings.TEMP_FOLDER, file_name), 'wb+') as f:
                for c in file.chunks():
                    f.write(c)
            files[key] = file_name

        return files

    def get_params(self):
        """
        ### 将request中的参数提取到一个字典

        :return: 参数字典
        """
        return get_params(self.request)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ModelViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    pass
