from django.db import models
from shortuuidfield import ShortUUIDField
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _
from .validate import is_valid_short_uuid, is_valid_uuid
from django.db import IntegrityError


class AbstractBaseModel(models.Model):
    """
    Base abstract model, that has `uuid` instead of `id` and includes `created_at`, `updated_at` fields.
    """
    uuid = ShortUUIDField(
        primary_key=True, editable=False, unique=True, max_length=22)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        abstract = True

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.uuid}>'


class UserField(CharField):
    description = 'User field'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 36

        if 'null' not in kwargs:
            kwargs['null'] = False

        if 'blank' not in kwargs:
            kwargs['blank'] = False

        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add: bool):
        value = super().pre_save(model_instance, add)

        if self.null and value == None:
            return value
        elif self.blank and value == '':
            return value
        elif not is_valid_uuid(value):
            raise IntegrityError("Invalid uuid")
        else:
            return value

class MicroserviceForginKey(CharField):
    description = _("Key used by different BarTab microservice")


    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 22
        
        if 'null' not in kwargs:
            kwargs['null'] = False

        if 'blank' not in kwargs:
            kwargs['blank'] = False

        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add: bool):
        value = super().pre_save(model_instance, add)

        if self.null and value == None:
            return value
        elif self.blank and value == '':
            return value
        elif not is_valid_short_uuid(value):
            raise IntegrityError("Invalid short uuid")
        else:
            return value
