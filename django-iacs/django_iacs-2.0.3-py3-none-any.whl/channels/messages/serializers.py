from rest_framework import serializers


class MessageBaseSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.meta = getattr(self, 'Meta', None)
        super().__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class RequestMessageHeader(MessageBaseSerializer):
    msg_id = serializers.IntegerField()
    msg_type = serializers.CharField()


class ResponseMessageHeader(RequestMessageHeader):
    status = serializers.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        self.meta = getattr(self, 'Meta', None)
        if isinstance(kwargs.get('data'), dict):
            try:
                kwargs['data']['msg_type'] = self.meta.MSG_TYPE
            except AttributeError:
                raise
        super().__init__(*args, **kwargs)


class HeaderErrorResponse(MessageBaseSerializer):
    origin = serializers.DictField()
    errors = serializers.DictField()
    status = serializers.IntegerField(default=1)
