import copy
from dataclasses import dataclass

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

APP_LABEL = "iacs"


def default_time():
    return int(timezone.now().timestamp() * 1000000)


@dataclass(frozen=True)
class PermissionGroupType:
    NORMAL = 0
    SUPER = 1


class Api(models.Model):
    GET = 0
    POST = 1
    DELETE = 2
    PUT = 3
    PATCH = 4

    METHOD = (
        (GET, _('get')),
        (POST, _('post')),
        (DELETE, _('delete')),
        (PUT, _('put')),
        (PATCH, _('patch'))
    )
    PROTOCOL = (
        (0, _('http | https')),
        (1, _('ws | wss'))
    )
    id = models.AutoField(primary_key=True, verbose_name=_('api id'))
    regex = models.CharField(max_length=255, default='', verbose_name=_('api regex'))
    protocol = models.IntegerField(default=0, choices=PROTOCOL, verbose_name=_('api protocol'))
    method = models.IntegerField(default=0, choices=METHOD, null=True, verbose_name=_('api http request method'))
    # 按照rest风格定义的请求方法，不一定与http请求方法一致
    rest_method = models.IntegerField(default=0, choices=METHOD, null=True, verbose_name=_('rest method'))
    name = models.CharField(max_length=255, default='', verbose_name=_('api name'))
    base_name = models.CharField(max_length=255, default='', verbose_name=_('api base name'))
    position = models.CharField(max_length=128, default='', verbose_name=_('api position'))
    group = models.CharField(max_length=128, default='', verbose_name=_('api group'))
    user_default = models.BooleanField(default=0, verbose_name=_('is user default'))
    app_name = models.CharField(max_length=64, default='', verbose_name=_('app name'))

    class Meta:
        verbose_name = _('api')
        app_label = APP_LABEL


class PermissionGroup(models.Model):
    TYPES = (
        (PermissionGroupType.NORMAL, _('normal group')),
        (PermissionGroupType.SUPER, _('super group')),
    )

    id = models.AutoField(primary_key=True, )
    description = models.CharField(max_length=128, default='', null=True)
    name = models.CharField(max_length=50, default='', )
    type = models.SmallIntegerField(default=0, choices=TYPES)
    auth_time = models.IntegerField(default=3600)  # 单次认证的有效时间
    api = models.ManyToManyField(Api)

    class Meta:
        app_label = APP_LABEL
        verbose_name = _('permission group')


class User(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=_('user id'))
    username = models.CharField(max_length=50, default='', verbose_name=_('user account'))
    password = models.CharField(max_length=255, default='', verbose_name=_('user pass code'))
    alias = models.CharField(max_length=128, default='', verbose_name=_('user alias'))
    cellphone_number = models.BigIntegerField(null=True, verbose_name=_('user cellphone number'))
    email = models.EmailField(default='', verbose_name=_('user email'))
    is_active = models.BooleanField(default=1, verbose_name=_('user is active or not'))
    create_timestamp = models.BigIntegerField(default=default_time, verbose_name=_('create time'))
    creator = models.IntegerField(null=True, verbose_name=_('creator'))
    is_super = models.BooleanField(default=0)
    expire_day = models.IntegerField(default=0)
    expire_timestamp = models.BigIntegerField(null=True)
    permission_group = models.ManyToManyField('PermissionGroup')
    api = models.ManyToManyField(Api)

    _is_authenticated = False

    @property
    def is_authenticated(self):
        return self._is_authenticated

    def authenticate(self):
        self._is_authenticated = True

    class Meta:
        app_label = APP_LABEL
        verbose_name = _('user')


class Menu(models.Model):
    id = models.CharField(max_length=128, primary_key=True, verbose_name=_('menu id'))
    name = models.CharField(max_length=255, default='', verbose_name=_('menu name'))
    expandable = models.BooleanField(default=0, verbose_name=_('expandable'))
    bold = models.BooleanField(default=0, verbose_name=_('bold'))
    css_icon = models.CharField(max_length=255, default='', verbose_name=_('css icon'))
    link = models.CharField(max_length=255, default='', verbose_name=_('link'))
    father = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name='father_set',
                               verbose_name=_('super menu id'))
    supers = models.ManyToManyField("self", symmetrical=False)
    apis = models.ManyToManyField('Api')
    activate = models.BooleanField(default=True, verbose_name=_('activate'))
    sequence = models.IntegerField(default=0, verbose_name=_('sequence'))

    def read_apis(self):
        return self.apis.filter(method=Api.GET)

    def write_apis(self):
        return self.apis.filter(method__in=[Api.POST, Api.PUT, Api.PATCH])

    def delete_apis(self):
        return self.apis.filter(method=Api.DELETE)

    @staticmethod
    def get_menu_tree(menu_list):
        menu_tree = []

        # 递归方法
        def tree(menu):
            copy_menu = copy.copy(menu)
            copy_menu["sub_menu"] = []
            for _m in filter(lambda m: m["father"] == menu["id"], menu_list):
                __m = tree(_m)
                copy_menu["sub_menu"].append(__m)
            copy_menu["leaf_node"] = len(copy_menu["sub_menu"]) == 0
            return copy_menu

        for root_menu in filter(lambda m: m["father"] is None, menu_list):
            menu_dict = tree(root_menu)
            menu_tree.append(menu_dict)

        return menu_tree

    class Meta:
        app_label = APP_LABEL
        ordering = ('sequence',)
        verbose_name = _('menu')


class MenuPermission(models.Model):
    id = models.AutoField(primary_key=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE, null=True)
    read = models.SmallIntegerField(null=True, verbose_name='读取权限')
    write = models.SmallIntegerField(null=True, verbose_name='写入权限')
    delete = models.SmallIntegerField(null=True, verbose_name='删除权限')

    class Meta:
        app_label = APP_LABEL
        verbose_name = _('menu permission')


class OperationLog(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=_('auto id'))
    username = models.CharField(max_length=255, default='', verbose_name=_('user name'))
    ipv4 = models.GenericIPAddressField(protocol='IPv4', default='', null=True, verbose_name=_('user ipv4 address'))
    ipv6 = models.GenericIPAddressField(protocol='IPv6', default='', null=True, verbose_name=_('user ipv6 address'))
    desc = models.CharField(default="", max_length=255, verbose_name=_('operation desc'))
    before = models.TextField(default='', verbose_name=_('data before change'))
    after = models.TextField(default='', verbose_name=_('data after change'))
    request_data = models.TextField(default='', verbose_name=_('request data'))
    create_timestamp = models.BigIntegerField(default=default_time, verbose_name=_('create time'))

    class Meta:
        app_label = APP_LABEL
        verbose_name = _('operation log')
