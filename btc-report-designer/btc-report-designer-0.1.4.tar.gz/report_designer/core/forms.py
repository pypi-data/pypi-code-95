from django.forms import (FileInput, CheckboxInput, RadioSelect, Select, NullBooleanSelect,)


class StyledFormMixin:
    """
    Миксин стилизации форм
    """

    js_class_prefix = 'js-rd-field'
    field_css_class = 'input__input'
    empty_choice_filter = 'Не выбрано'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Поля формы
        self.form_fields = self.get_form_fields()

        # Установка базовых классов виджетов
        self.init_processing_fields()

    def init_processing_fields(self):
        """
        Обработка полей при инициализации
        """
        for field_name, field in self.form_fields.items():
            self.init_processing_field(field_name, field)

    def init_processing_field(self, field_name, field):
        """
        Обработка поля при инициализации
        """
        widget_type = field.widget.__class__.__name__.lower()
        field_classes = (
            f'{self.js_class_prefix}_{field_name}',
            f'{self.field_css_class} {self.field_css_class}_{widget_type}',
        )
        self.set_widget_class(field_name, field_classes)

        # Установка пустого значения для Select
        if isinstance(field.widget, Select) and hasattr(field, 'empty_label') and field.empty_label is not None:
            field.empty_label = self.empty_choice_filter

    def set_widget_class(self, field, value):
        """
        Установка класса виджету поля
        """
        self.add_or_update_widget_attr(field, 'class', value)

    def add_or_update_widget_attr(self, field, attr, value):
        """
        Добавление класса к виджету поля
        """
        attrs = self.form_fields[field].widget.attrs
        value = isinstance(value, (list, tuple)) and value or [value]
        self.form_fields[field].widget.attrs.update({attr: ' '.join(filter(None, [attrs.get(attr), *value]))})

    def get_form_fields(self):
        """
        Получение полей формы
        """
        return self.fields.copy()
