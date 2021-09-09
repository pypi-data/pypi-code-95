import copy

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.response import Response

from ..mixins import OperationLogMixin
from ..models import PermissionGroup, Api, PermissionGroupType, Menu, MenuPermission, User
from ..rest.decorator import action_name
from ..rest.viewsets import GenericViewSet
from ..serializers.group import GroupSerializer
from ..serializers.menu import MenuSerializer


class PermissionGroupViewSet(GenericViewSet,
                             CreateModelMixin,
                             ListModelMixin,
                             UpdateModelMixin,
                             RetrieveModelMixin,
                             DestroyModelMixin,
                             OperationLogMixin):
    queryset = PermissionGroup.objects.prefetch_related('api').exclude(type=PermissionGroupType.SUPER)
    serializer_class = GroupSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        'name',
    )
    known_actions_name = {
        'list': '获取全部权限分组列表',
        'update': '更新权限分组信息',
        'retrieve': '获取任意权限分组信息',
        'destroy': '删除权限分组',
        'create': '创建权限分组'
    }
    simple_serialize_fields = [
        'id',
        'name',
        'auth_time',
        'description',
        'type_display'
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True,
                                             fields=self.simple_serialize_fields)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True,
                                         fields=self.simple_serialize_fields)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        description = request.data.get('description')
        auth_time = request.data.get('auth_time', None)
        try:
            PermissionGroup.objects.get(name=name)
            return Response({'msg': '分组已存在'}, status=400)
        except PermissionGroup.DoesNotExist:
            created = PermissionGroup.objects.create(**{
                'name': name,
                'description': description,
                'auth_time': auth_time
            })
        created.api.add(*Api.objects.filter(user_default=True))
        serializer = self.get_serializer(instance=created)

        self.save_operation_log("创建权限分组", request_data=request.data, after=serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        permission_group = self.get_object()
        if permission_group.user_set.count() > 0:
            return Response({'msg': '该分组存在用户，禁止删除'},
                            status=status.HTTP_400_BAD_REQUEST)

        self.save_operation_log(f'删除分组， 组名：{permission_group.name}',
                                before=self.get_serializer(instance=permission_group).data)
        return super(PermissionGroupViewSet, self).destroy(request, args,
                                                           kwargs)

    @action_name('权限组赋权')
    @action(methods=['post'], detail=True)
    def grant(self, request, *args, **kwargs):
        obj = self.get_object()
        op_log_obj = copy.copy(obj)  # 记录操作前的状态
        menu_permission = request.data.get('menu_permission')

        if not isinstance(menu_permission, list) or len(menu_permission) == 0:
            return Response({'msg': '参数错误'},
                            status=status.HTTP_400_BAD_REQUEST)

        all_menu = set(
            map(str, Menu.objects.all().values_list("id", flat=True)))

        menu_in_params = set([str(m["menu_id"]) for m in menu_permission])

        # 取交集
        intersection = all_menu & menu_in_params

        # 交集结果与参数中菜单id不相等则表示参数中有无法识别的菜单ID
        if intersection != menu_in_params:
            return Response(
                data={'msg': '无效菜单', 'menu_id': menu_in_params - intersection},
                status=status.HTTP_400_BAD_REQUEST)

        menu_permission_objs = []
        apis = set()

        # 记录修改权限中的叶子菜单
        leaf_menus = set()

        for mp in menu_permission:
            mp["permission_group_id"] = obj.id
            menu = Menu.objects.get(id=mp["menu_id"])
            if menu.link != "":
                leaf_menus.add(menu)
                if mp.get("read", False):
                    apis = apis | set(menu.read_apis())
                if mp.get("write", False):
                    apis = apis | set(menu.write_apis())
                if mp.get("delete", False):
                    apis = apis | set(menu.delete_apis())
                menu_permission_objs.append(MenuPermission(**mp))

        # 将叶子菜单的父级菜单权限加上
        for menu in leaf_menus:
            for father in menu.supers.all():
                menu_permission_objs.append(MenuPermission(**{
                    'permission_group_id': obj.id,
                    'menu_id': father.id
                }))

        # 加上用户默认拥有的api
        apis = apis | set(Api.objects.filter(user_default=True))

        # 先删除原有的记录
        MenuPermission.objects.filter(permission_group_id=obj.id).delete()
        MenuPermission.objects.bulk_create(menu_permission_objs)
        obj.api.set(apis)

        # 将已有的权限组的用户重新分配权限
        users = User.objects.filter(permission_group__id=obj.id)
        if users:
            for user in users:
                user.api.set(apis)

        self.save_operation_log(**{
            "desc": f'赋予分组 {obj.name} 接口权限',
            "request_data": self.request.data,
            "before": self.get_serializer(instance=op_log_obj).data,
            "after": self.get_serializer(instance=obj).data,
        })
        return Response({'msg': '授权成功'})

    @action_name('获取权限组拥有的菜单')
    @action(methods=["get"], detail=True)
    def menu(self, request, *args, **kwargs):
        group = self.get_object()
        menu_ids = MenuPermission.objects.filter(
            permission_group_id=group.id).values_list("menu_id", flat=True)
        serializer = MenuSerializer(Menu.objects.filter(id__in=menu_ids, activate=True),
                                    many=True)
        menu_list = serializer.data
        for menu in menu_list:
            if menu["link"] != "":
                mp = MenuPermission.objects.filter(
                    permission_group=group.id,
                    menu__id=menu["id"]
                )
                menu["read"] = any(mp.values_list("read", flat=True))
                menu["write"] = any(mp.values_list("write", flat=True))
                menu["delete"] = any(mp.values_list("delete", flat=True))
            else:
                menu["read"] = None
                menu["write"] = None
                menu["delete"] = None
        return Response(
            {'list': menu_list, 'tree': Menu.get_menu_tree(menu_list)})
