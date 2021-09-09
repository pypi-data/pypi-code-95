from collections import namedtuple

from rest_framework.serializers import ModelSerializer as MSerializer, Serializer


class ModelSerializer(MSerializer):
    """
    ### 自定义要序列化的字段

    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        super(ModelSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)

        if exclude is not None:
            for field in exclude:
                self.fields.pop(field)

    @staticmethod
    def serialize(cls, obj, **kwargs):
        return cls(instance=obj, **kwargs).data


class TimestampModelSerializer(ModelSerializer):
    """
    ### 自动转换微妙时间戳
    """

    def to_representation(self, instance):
        res = super(TimestampModelSerializer, self).to_representation(instance)
        for key in res.keys():
            try:
                if str(key).endswith('_timestamp') and res[key]:
                    res[key] = res[key] / 1000
            except Exception as e:
                res[key] = None
        return res


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
