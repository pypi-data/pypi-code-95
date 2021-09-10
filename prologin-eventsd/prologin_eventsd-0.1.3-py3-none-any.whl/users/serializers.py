from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "address",
            "city",
            "zip_code",
            "country",
            "is_staff",
        )

        read_only_fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "email",
            "is_staff",
        )
