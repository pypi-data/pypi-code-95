from wtforms import validators
from wtforms import fields
from tornadmin.backends.forms import BaseModelForm, NullDateField, NullDateTimeField
from tornadmin.utils import get_display_name


class ModelForm(BaseModelForm):
    pass


TORTOISE_TO_WTF_MAP = {
    'BigIntField': fields.IntegerField,
    'BooleanField': fields.BooleanField,
    'CharField': fields.StringField,
    'DateField': NullDateField,
    'DatetimeField': NullDateTimeField,
    'FloatField': fields.FloatField,
    'IntField': fields.IntegerField,
    'SmallIntField': fields.IntegerField,
    'TextField': fields.TextAreaField,
}


def tortoise_to_wtf(tortoise_field):
    return TORTOISE_TO_WTF_MAP.get(
        type(tortoise_field).__name__, 
        fields.StringField
    )


def modelform_factory(admin, model):
    fields = {}

    for field_name, model_field in model._meta.fields_map.items():

        if field_name not in admin.readonly_fields:
            if model_field.pk:
                continue

            if getattr(model_field, 'auto_now', False):
                continue

            if getattr(model_field, 'auto_now_add', False):
                continue

        name = get_display_name(field_name)

        validators_list = []

        if model_field.required and field_name not in admin.readonly_fields:
            validators_list.append(validators.required())

        if hasattr(model_field, 'max_length'):
            validators_list.append(validators.Length(max=model_field.max_length))

        attrs = {'placeholder': name}

        if field_name in admin.readonly_fields:
            attrs['readonly'] = True

        form_field = tortoise_to_wtf(model_field)

        fields[field_name] = form_field(
            name,
            validators_list,
            render_kw=attrs
        )

    fields['_fields'] = list(fields.keys())

    form = type('%sForm' % model.__name__, (ModelForm,), fields)

    return form
