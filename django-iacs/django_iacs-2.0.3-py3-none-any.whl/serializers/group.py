from rest_framework import serializers

from ..models import PermissionGroup
from ..rest.serializers import ModelSerializer


class GroupSerializer(ModelSerializer):
    type_display = serializers.ReadOnlyField(source='get_type_display')

    class Meta:
        model = PermissionGroup
        exclude = ["api"]
