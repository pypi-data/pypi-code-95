from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from ..models import Menu
from ..rest.decorator import action_name, request_params_validate
from ..rest.viewsets import GenericViewSet
from ..serializers.menu import MenuSerializer

# noinspection PyUnusedLocal
from ..swagger import MenuViewSetActiveRequest, MenuViewSetTreeRequest, MenuViewSetTreeResponse


class MenuViewSet(GenericViewSet, UpdateModelMixin):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    known_actions_name = {
        'update': '修改菜单信息',
    }

    @swagger_auto_schema(operation_description="获取全部菜单树",
                         query_serializer=MenuViewSetTreeRequest(),
                         responses={200: MenuViewSetTreeResponse})
    @request_params_validate(serializer_class=MenuViewSetTreeRequest)
    @action_name('获取全部菜单树')
    @action(methods=['GET'], detail=False)
    def tree(self, request):
        is_all = request.GET.get('all')
        if is_all:
            serializer = self.serializer_class(self.queryset.all(), many=True)
        else:
            serializer = self.serializer_class(self.queryset.filter(activate=True), many=True)
        return Response({'list': serializer.data, 'tree': Menu.get_menu_tree(serializer.data)})

    @swagger_auto_schema(operation_description="修改菜单激活状态",
                         request_body=MenuViewSetActiveRequest(),
                         responses={200: "修改成功"})
    @request_params_validate(serializer_class=MenuViewSetActiveRequest)
    @action_name('修改菜单激活状态')
    @action(methods=['PUT'], detail=False)
    def active(self, request):
        for menu in self.get_params().get('menus'):
            id = menu.get('id')
            activate = menu.get('activate')
            instance = self.queryset.filter(id=id).first()
            serializer = self.serializer_class(instance, data={'id': id, 'activate': activate})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({'msg': '修改成功'})
