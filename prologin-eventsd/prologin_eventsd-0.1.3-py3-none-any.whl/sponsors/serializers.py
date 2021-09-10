from rest_framework import serializers
from . import models


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sponsor
        fields = (
            "name",
            "logo",
            "order",
        )
