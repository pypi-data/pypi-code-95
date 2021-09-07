from django import template


register = template.Library()


@register.filter(name='fields_exists')
def fields_exists(form, input_type: str):
    """
    Проверка, есть ли в форме фильтров чекбоксы
    """
    def check_field(field):
        return hasattr(field.field.widget, 'input_type') and field.field.widget.input_type == input_type
    return any(map(check_field, form))
