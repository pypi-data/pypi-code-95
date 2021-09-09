from collections import namedtuple

from rest_framework.serializers import Serializer


class RequestParamsSerializer(Serializer):
    """
    查询参数序列化类
    """

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        namedtuple_fields = list()
        for key, field in self.fields.items():

            if field.required:
                namedtuple_fields.append(key)
            else:
                if key in validated_data.keys():
                    namedtuple_fields.append(key)

        Obj = namedtuple('Params', namedtuple_fields)
        return Obj(**validated_data)
