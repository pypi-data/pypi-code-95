from rest_framework import serializers

from iacs.models import OperationLog
from iacs.rest.serializers import TimestampModelSerializer


class OperationLogSerializer(TimestampModelSerializer):
    before = serializers.CharField(default='', allow_blank=True)
    after = serializers.CharField(default='', allow_blank=True)
    request_data = serializers.CharField(default='', allow_blank=True)

    class Meta:
        model = OperationLog
        fields = '__all__'
