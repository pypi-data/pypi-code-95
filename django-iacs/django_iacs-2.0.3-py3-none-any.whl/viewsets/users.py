import copy

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.forms.models import model_to_dict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.validators import ValidationError

from ..mixins import OperationLogMixin
from ..models import User, Menu, PermissionGroupType, MenuPermission, default_time, PermissionGroup
from ..rest.auth import NoAuthentication
from ..rest.decorator import action_name, request_params_validate
from ..rest.mixins import PartialFieldsListModelMixin
from ..rest.serializers import RequestParamsSerializer
from ..rest.viewsets import GenericViewSet
from ..serializers.group import GroupSerializer
from ..serializers.user import UserSerializer
from ..utils.encryption import cal_sha1_string, make_token
from ..utils.time import get_current_time_by_microsecond
from ..validators import *


class UserViewSetCreateParamsSerializer(RequestParamsSerializer):
    username = serializers.CharField(max_length=32)
    alias = serializers.CharField(max_length=32)
    password = serializers.CharField()
    cellphone_number = serializers.CharField(validators=[phone_number_validator])
    email = serializers.CharField(validators=[email_validator])
    expire_day = serializers.IntegerField(min_value=0)


class UserViewSetChangeInfoParamsSerializer(RequestParamsSerializer):
    alias = serializers.CharField(max_length=32, required=False)
    email = serializers.CharField(validators=[email_validator], required=False)
    cellphone_number = serializers.CharField(validators=[phone_number_validator], required=False)


class UserViewSetChangePasswordParamsSerializer(RequestParamsSerializer):
    password = serializers.CharField()
    new_password = serializers.CharField()


class UserViewSetUpdateParamsSerializer(RequestParamsSerializer):
    alias = serializers.CharField(max_length=32, required=False)
    password = serializers.CharField(required=False)
    cellphone_number = serializers.CharField(validators=[phone_number_validator], required=False)
    email = serializers.CharField(validators=[email_validator], required=False)
    expire_day = serializers.IntegerField(min_value=0)


# class UserViewSetGetMyMenuParamsSerializer(RequestParamsSerializer):


# noinspection PyUnusedLocal
class UserViewSet(GenericViewSet,
                  CreateModelMixin,
                  PartialFieldsListModelMixin,
                  UpdateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  OperationLogMixin):
    queryset = User.objects.prefetch_related('permission_group', 'api').exclude(pk=1)
    serializer_class = UserSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        'alias',
        'cellphone_number',
        'email'
    )
    ordering_fields = ('create_timestamp',)
    known_actions_name = {
        'list': '获取全部用户列表',
        'retrieve': '获取任意用户信息',
        'update': '修改用户信息',
        'destroy': '删除用户',
        'create': '创建用户'
    }

    simple_serialize_fields = [
        'id',
        'alias',
        'username',
        'cellphone_number',
        'email',
        'is_active',
        'create_timestamp',
        'is_super',
        'online',
        'expire_timestamp',
        'expire_day',
        'permission_group_id'
    ]

    def retrieve(self, request, *args, **kwargs):
        return super(UserViewSet, self).retrieve(request, *args, **kwargs)

    @request_params_validate(serializer_class=UserViewSetUpdateParamsSerializer)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.validated_data
        params = request.validated_params

        if hasattr(params, 'password'):
            data["password"] = make_password(cal_sha1_string(params.password))

        if params.expire_day == 0:
            data["expire_timestamp"] = None
        else:
            data["expire_timestamp"] = instance.create_timestamp + params.expire_day * 86400 * 1000000

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.save_operation_log(desc="更新用户信息", request_data=data)
        return Response(serializer.data)

    @request_params_validate(serializer_class=UserViewSetCreateParamsSerializer)
    def create(self, request, *args, **kwargs):
        params = request.validated_params
        try:
            User.objects.get(username=params.username)
            return Response({'msg': '用户已存在'}, status=400)
        except User.DoesNotExist:
            if params.expire_day == 0:
                expire_timestamp = None
            else:
                expire_timestamp = default_time() + params.expire_day * 86400 * 1000000

            created = User.objects.create(**{
                'username': params.username,
                'alias': params.alias,
                'cellphone_number': params.cellphone_number,
                'email': params.email,
                'password': make_password(cal_sha1_string(params.password)),
                'creator': request.user.id,
                'expire_day': params.expire_day,
                'expire_timestamp': expire_timestamp
            })

        data = self.get_serializer(instance=created).data
        # 记录操作日志
        self.save_operation_log(**{
            'desc': '创建新用户',
            'request_data': params,
            'after': data
        })
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_super:
            raise ValidationError({'msg': '不允许删除超级用户'})
        # 记录操作日志
        self.save_operation_log(**{
            'desc': '删除用户，用户名：{}'.format(user.username),
            'before': self.get_serializer(instance=user).data
        })
        return super(UserViewSet, self).destroy(request, *args, **kwargs)

    @action_name('用户登录', user_default=True)
    @action(methods=['post'], detail=False, permission_classes=[AllowAny], authentication_classes=[NoAuthentication])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        password = cal_sha1_string(password)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'msg': '用户不存在'}, status=HTTP_400_BAD_REQUEST)
        except User.MultipleObjectsReturned:
            return Response({'msg': '错误的用户, 用户名重复'}, status=HTTP_400_BAD_REQUEST)

        if user.permission_group.count() == 0:
            return Response({'msg': '用户没有分配权限, 无法登录'}, status=HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            return Response({'msg': '密码错误'}, status=HTTP_400_BAD_REQUEST)

        self.request.user = user
        token = make_token()
        login_token_key = settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=token)
        login_user_key = settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=user.id)
        data = {
            'id': user.id,
            'username': user.username,
            'token': token,
            'client_host': self.get_client_ip(),
            'create_timestamp': get_current_time_by_microsecond()
        }
        self.redis.hmset(login_token_key, data)
        self.redis.hmset(login_user_key, data)
        auth_times = [p.auth_time for p in user.permission_group.all()]
        self.redis.expire(login_token_key, max(auth_times))
        self.redis.expire(login_user_key, max(auth_times))
        self.save_operation_log(**{
            'desc': '登入系统'
        })
        return Response({'token': token, 'msg': '认证成功'})

    def single_login(self, user):
        """
        单点登录控制，用户登录时先删除其它所有的token
        :param user:
        :return:
        """
        key = settings.REDIS_LOGIN_USER_KEY.format(user_id=user.id)
        tokens = self.redis.hkeys(key)  # 查出用户所有的登录token
        # todo: 排除有用的token，其它token全部删除，目前单点登录控制只需要全部删除就行
        for token in tokens:
            self.redis.hdel(key, token)
            self.redis.delete(settings.REDIS_LOGIN_TOKEN_KEY.format(token=token.decode()))

    @action_name('获取当前用户认证状态', user_default=True)
    @action(methods=["get"], detail=False)
    def is_authenticated(self, request):
        return Response({'status': 'success'})

    @action_name('获取当前用户信息', user_default=True)
    @action(methods=['get'], detail=False)
    def info(self, request):
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)

    @action_name('注销用户登录', user_default=True)
    @action(methods=['get'], detail=False)
    def sign_out(self, request):
        auth_token = request.auth
        self.save_operation_log(**{
            'desc': '主动退出系统'
        })
        self.redis.delete(settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=auth_token))
        self.redis.delete(settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=request.user.id))
        return Response({'status': 'success'})

    @action_name('修改当前登录用户密码', user_default=True)
    @request_params_validate(serializer_class=UserViewSetChangePasswordParamsSerializer)
    @action(methods=['post'], detail=False)
    def change_password(self, request):
        user_id = request.user.id
        user = User.objects.get(pk=user_id)
        params = request.validated_params
        if not params.password:
            raise ValidationError({'msg': '密码不能为空'})
        password = cal_sha1_string(params.password)
        if not check_password(password, user.password):
            raise serializers.ValidationError({'msg': '密码校验失败'})
        user.password = make_password(cal_sha1_string(params.new_password))
        user.save()
        self.save_operation_log(**{
            'desc': '修改密码'
        })
        return Response({'status': '修改成功'})

    @action_name('修改当前登录用户信息', user_default=True)
    @request_params_validate(serializer_class=UserViewSetChangeInfoParamsSerializer)
    @action(methods=['post'], detail=False)
    def change_info(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 记录操作日志
        self.save_operation_log(**{
            'desc': '修改信息',
            'request_data': request.validated_data
        })
        return Response(self.get_serializer(instance=user).data)

    @action_name('修改用户权限组')
    @action(methods=['post'], detail=True)
    def grant(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_super:
            return Response({'msg': '禁止修改此用户权限'}, status=HTTP_400_BAD_REQUEST)
        op_log_user = copy.copy(user)  # 记录操作前的状态
        permission_group = request.data.get('permission_group')
        api_set = set()
        try:
            permission_group = [int(p) for p in permission_group]
            for g in permission_group:
                api_set = api_set | set(PermissionGroup.objects.get(id=g).api.all())

            # 禁用超级权限组
            if PermissionGroupType.SUPER in permission_group:
                return Response({'msg': f'参数错误; internal error'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': f'参数错误; {e}'}, status=HTTP_400_BAD_REQUEST)
        user.permission_group.set(permission_group)
        user.api.set(api_set)
        # 记录操作日志
        self.save_operation_log(**{
            'desc': '修改用户分组',
            'before': GroupSerializer(instance=op_log_user.permission_group, many=True).data,
            'after': GroupSerializer(instance=user.permission_group, many=True).data,
        })
        return Response({'msg': '修改成功'})

    @action_name('获取任意用户菜单')
    @action(methods=['get'], detail=True, url_path='menu')
    def get_user_menu(self, request, *args, **kwargs):
        user = self.get_object()
        return Response(self.get_user_menu_tree(user))

    @action_name('获取当前登录用户菜单', user_default=True)
    @action(methods=['get'], detail=False, url_path='menu')
    def get_my_menu(self, request, *args, **kwargs):
        return Response(self.get_user_menu_tree(request.user))

    def get_user_menu_tree(self, user):
        user_permission_groups = user.permission_group.values_list("id", flat=True)
        user_menus = MenuPermission.objects.filter(permission_group_id__in=user_permission_groups).values_list(
            "menu_id", flat=True)
        user_menus = set(user_menus)

        qs = Menu.objects.prefetch_related("supers").filter(
            id__in=user_menus,
            activate=True
        ).order_by("sequence")

        menu_list = []

        mp_qs = MenuPermission.objects.filter(
            permission_group__in=user_permission_groups,
        ).values()

        for obj in qs:
            menu = model_to_dict(obj, fields=[f.name for f in obj._meta.fields])
            if obj.link != "":
                for row in filter(lambda x: x["menu_id"] == obj.id, mp_qs):
                    if row["read"]:
                        menu["read"] = True
                    if row["write"]:
                        menu["write"] = True
                    if row["delete"]:
                        menu["delete"] = True
            else:
                menu["read"] = None
                menu["write"] = None
                menu["delete"] = None
            menu["father"] = obj.father_id
            menu["supers"] = obj.supers.values_list("id", flat=True)
            menu_list.append(menu)

        menu_tree = Menu.get_menu_tree(menu_list)
        return {'list': menu_list, 'tree': menu_tree}

    @action_name('获取已登录用户')
    @action(methods=['get'], detail=False)
    def online(self, request, *args, **kwargs):
        users = []
        tokens = self.redis.keys(settings.REDIS_LOGIN_TOKEN_KEY.format('*'))
        for t in tokens:
            _ids = self.redis.hmget(t, 'id')
            if all(_ids):
                users.append(int(_ids[0]))
        users = list(set(users))
        users_instances = []
        for u_id in users:
            ins = User.objects.get(pk=u_id)
            users_instances.append(ins)
        users_serializer = []
        for instance in users_instances:
            u = UserSerializer(instance=instance, fields=self.simple_serialize_fields)
            users_serializer.append(u.data)
        return Response(users_serializer)

    @action_name('检查登录账号是否存在')
    @action(methods=['get'], detail=False)
    def exists(self, request, *args, **kwargs):
        username = request.GET.get("username", None)
        if not username:
            return Response({"msg": "参数错误"})
        if User.objects.filter(username=username).exists():
            return Response({"msg": "账号已存在"})
        else:
            return Response({"msg": "账号未使用"})


def get_serialized_data(serializer_class, instance):
    return serializer_class(instance=instance).data
