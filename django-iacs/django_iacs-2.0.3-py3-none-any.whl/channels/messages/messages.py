from rest_framework import serializers

from .serializers import RequestMessageHeader, ResponseMessageHeader
from .validators import ResultCodeValidator


class SnowFlakeRequest(RequestMessageHeader):
    count = serializers.IntegerField()

    class Meta:
        MSG_TYPE = "iacs__SnowFlakeRequest"


class SnowFlakeResponse(ResponseMessageHeader):
    data = serializers.ListField()

    class Meta:
        MSG_TYPE = "iacs__SnowFlakeResponse"


class ServerTimeRequest(RequestMessageHeader):
    class Meta:
        MSG_TYPE = "iacs__ServerTimeRequest"


class ServerTimeResponse(ResponseMessageHeader):
    class ResultCode:
        NORMAL = 0
        ERROR = 100

    result_code = serializers.IntegerField(
        validators=[
            ResultCodeValidator(ResultCode)
        ]
    )
    time = serializers.IntegerField()

    class Meta:
        MSG_TYPE = "iacs__ServerTimeResponse"


class UserPingRequest(RequestMessageHeader):
    token = serializers.CharField()

    class Meta:
        MSG_TYPE = "iacs__UserPingRequest"


class UserPingResponse(ResponseMessageHeader):
    class ResultCode:
        NORMAL = 0
        ANTHER_LOGIN = 1
        ERROR = 100

    desc = serializers.CharField(required=False)
    time = serializers.IntegerField()
    data = serializers.CharField(required=False)
    errors = serializers.DictField(required=False)
    result_code = serializers.IntegerField(
        validators=[
            ResultCodeValidator(ResultCode)
        ]
    )

    class Meta:
        MSG_TYPE = "iacs__UserPingResponse"