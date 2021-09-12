from rest_framework.serializers import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers

class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices

        if 'default_value' in kwargs:
            self.default_value = kwargs.pop("default_value")

        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, value):        
        display_value = self.get_display_value_or_none(value)
        if display_value != None:
            return display_value
        else:
            try:
                return self.default_value[1]
            except AttributeError:
                raise ValidationError("{} is not a valid value.".format(value))

    def to_internal_value(self, value):
        internal_value = self.get_internal_value_or_none(value)
        if internal_value != None:
            return internal_value
        else:
            try:
                return self.default_value[0]
            except AttributeError:
                raise ValidationError("{} is not a valid value.".format(value))
        

    def get_display_value_or_none(self, value):
        for choice in self._choices:
            if choice[0] == value or choice[1] == value:
                return choice[1]
        return None

    def get_internal_value_or_none(self, value):
        for choice in self._choices:
            if choice[0] == value or choice[1] == value:
                return choice[0]
        return None


class UUIDField(serializers.CharField):

    def __init__(self, **kwargs):
        kwargs['max_length'] = 22
        kwargs['min_length'] = 22
        kwargs['allow_blank'] = False
        kwargs['trim_whitespace'] = True

        super().__init__(**kwargs)

    @ staticmethod
    def getField(error_message="Invalid UUID"):
        return serializers.CharField(
            max_length=22, validators=[RegexValidator(regex=r"^[a-zA-Z0-9]{22}$", message=error_message)])
