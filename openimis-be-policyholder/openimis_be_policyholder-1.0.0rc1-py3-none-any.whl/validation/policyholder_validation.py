from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from policyholder.models import PolicyHolder


class PolicyHolderValidation:
    UNIQUE_DISPLAY_NAME_VALIDATION_ERROR = "Display name '{} {}' already in use"

    @classmethod
    def validate_create(cls, user, **data):
        code = data.get('code', None)
        trade_name = data.get('trade_name', None)
        if not cls.__unique_display_name(code, trade_name):
            raise ValidationError(cls.UNIQUE_DISPLAY_NAME_VALIDATION_ERROR.format(code, trade_name))

    @classmethod
    def validate_update(cls, user, **data):
        existing = PolicyHolder.objects.filter(id=data['id']).first()
        code = data.get('code', existing.code)  # New or current
        trade_name = data.get('trade_name', existing.trade_name)  # New or current
        duplicated = PolicyHolder.objects.filter(code=code, trade_name=trade_name).exclude(id=data['id']).exists()

        if duplicated:
            raise ValidationError(cls.UNIQUE_DISPLAY_NAME_VALIDATION_ERROR.format(code, trade_name))

    @classmethod
    def __unique_display_name(cls, code, trade_name):
        return not PolicyHolder.objects.filter(code=code, trade_name=trade_name).exists()
