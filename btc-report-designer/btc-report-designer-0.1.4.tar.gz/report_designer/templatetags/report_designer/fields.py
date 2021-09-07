from django.forms import BoundField
from django import template


register = template.Library()


@register.inclusion_tag(filename='report_designer/core/fields/field.html')
def field_wrapper(bound_field: BoundField, label: str = None, required: bool = None, **kwargs):
    """
    Обертка поля формы
    """
    context = {
        'field': bound_field,
        'label': label is not None and label or bound_field.label,
        'required': required is not None and required or bound_field.field.required,
        f'is_{bound_field.field.widget.input_type}': True,
        **kwargs
    }
    return context
