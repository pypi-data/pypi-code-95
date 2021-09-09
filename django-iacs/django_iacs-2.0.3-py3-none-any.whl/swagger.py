from iacs.rest.serializers import RequestParamsSerializer
from rest_framework import serializers

from iacs.serializers.menu import MenuSerializer


class MenuViewSetTreeRequest(RequestParamsSerializer):
    all = serializers.BooleanField(help_text="是否需要全部菜单", required=False)


class MenuViewSetTreeResponse(serializers.Serializer):
    list = MenuSerializer(many=True, help_text="菜单信息列表")
    tree = serializers.ListField(
        child=serializers.DictField(),
        help_text="菜单子节点和父节点字典列表",
    )


class MenuViewSetActiveRequest(RequestParamsSerializer):
    menus = serializers.ListField(
        child=serializers.DictField(),
        label="需要修改的菜单信息字典列表",
        help_text="需要修改的菜单信息字典列表; 包含id和activate"
    )
