from rest_framework import serializers


class BinaryField(serializers.Field):
    def to_internal_value(self, data):
        return data
