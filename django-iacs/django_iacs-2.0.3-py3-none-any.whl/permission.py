from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from .models import Api


class APIPermission(BasePermission):
    method_map = {
        'get': 0,
        'post': 1,
        'delete': 2,
        'put': 3,
        'patch': 4
    }

    def has_permission(self, request, view):
        func = getattr(view, view.action, None)
        url_name = getattr(func, 'url_name', None)
        if url_name:
            base_name = f'{view.basename}-{url_name}'
        else:
            base_name = f'{view.basename}-{view.action}'
        try:
            api = Api.objects.get(base_name=base_name)
        except Api.DoesNotExist:
            raise PermissionDenied(detail=f'{base_name}此接口未被记录')
        except Api.MultipleObjectsReturned:
            raise PermissionDenied(detail=f'{base_name}此接口重复')
        try:
            request.user.api.get(id=api.id)
            return True
        except Api.DoesNotExist:
            raise PermissionDenied(detail=f'您没有{api.name}接口的权限, 请联系管理员')
