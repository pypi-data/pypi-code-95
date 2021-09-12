from rest_framework.serializers import ValidationError

class AbstractDisplayValueValidator:
    def get_display(self, value_with_display):
        return value_with_display['display']

    def get_value(self, value_with_display):
        return value_with_display['value']

    def raise_error(self, value_with_display, error_messages):
        raise ValidationError(
            {self.get_display(value_with_display): error_messages})

    class Meta:
        abstract = True
