import functools

from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from ..models import Menu
from ..rest.serializers import ModelSerializer


class MenuSerializer(ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, instance):
        return Menu.objects.filter(supers=instance.id).values_list("id", flat=True)

    class Meta:
        model = Menu
        exclude = ["apis", "supers"]
        read_only_fields = ["father"]


class MenuTreeSerializer(MenuSerializer):
    sub_menu = SerializerMethodField(read_only=True)

    def to_representation(self, instance):
        """
        判断是否为叶子节点，为返回结果添加叶子节点属性leaf_node
        :param instance:
        :return:
        """
        ret = super(MenuTreeSerializer, self).to_representation(instance)
        # 返回一个数组
        sub = ret.get('sub_menu')
        ret['leaf_node'] = True if len(sub) == 0 else False
        return ret

    def get_sub_menu(self, obj):
        func = functools.partial(self.serialize, MenuTreeSerializer)

        results = []

        for m in Menu.objects.filter(father=obj):
            results.append(func(m))

        return results


class UserMenuTreeSerializer(MenuTreeSerializer):
    sub_menu = SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        """
        初始化的时候加入user参数，建立user的菜单树
        :param args:
        :param kwargs:
        """
        user = kwargs.pop('user', None)
        self.user = user
        if not self.user:
            raise Exception('this serializer class must have user param')
        super(UserMenuTreeSerializer, self).__init__(*args, **kwargs)

    def get_sub_menu(self, obj):
        sub_menus = Menu.objects.filter(father=obj, permissiongroup__user__id=self.user.id)

        func = functools.partial(self.serialize, UserMenuTreeSerializer, user=self.user)

        results = []

        for m in sub_menus:
            results.append(func(m))

        return results

    # def execute(self, ):

    @staticmethod
    def serialize(serializer_class, obj, **kwargs):
        return serializer_class(instance=obj, user=kwargs.get('user')).data
