from rest_framework import serializers

from iacs.models import Api
from ..rest.serializers import ModelSerializer


class ApiSerializer(ModelSerializer):
    class Meta:
        model = Api
        fields = serializers.ALL_FIELDS
