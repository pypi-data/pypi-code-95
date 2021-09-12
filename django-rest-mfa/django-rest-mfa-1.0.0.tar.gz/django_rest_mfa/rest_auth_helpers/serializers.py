from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer
from ..helpers import has_mfa


class NoopTokenSerializer(serializers.Serializer):
    """dj-rest-auth requires tokens, but we don't use them."""
