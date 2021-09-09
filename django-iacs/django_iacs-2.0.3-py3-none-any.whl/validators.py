import re

from rest_framework import serializers

__all__ = [
    'email_validator',
    'phone_number_validator'
]


def email_validator(value):
    email_re = re.compile(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(.[a-zA-Z0-9_]+)?(.[a-zA-Z][a-zA-Z]+)+$')
    if not email_re.search(value):
        raise serializers.ValidationError("无效的邮箱")


def phone_number_validator(value):
    number_re = re.compile(r'^1([3456789])[0-9]{9}$')
    if not number_re.search(value):
        raise serializers.ValidationError("无效的手机号")
