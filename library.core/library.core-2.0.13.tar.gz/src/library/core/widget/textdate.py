# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from plone.app.z3cform.interfaces import ITextWidget
from re import match
from z3c.form.browser.text import TextWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import FormatterValidationError
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapts
from zope.interface import implementer
from zope.schema.interfaces import ITextLine


class ITextDateWidget(ITextWidget):
    """Marker interface for TextDate"""


@implementer(ITextDateWidget)
class TextDateWidget(TextWidget):
    pass


@implementer(IFieldWidget)
def TextDateFieldWidget(field, request):
    """IFieldWidget factory for TextDateWidget."""
    return FieldWidget(field, TextDateWidget(request))


@implementer(IDataConverter)
class TextDateConverter(BaseDataConverter):
    """Text field, accepting dates only"""

    adapts(ITextLine, ITextDateWidget)

    regex_formats = {
        "\d{8}$": "%d%m%Y",
        "\d{6}$": "%m%Y",
        "\d{4}$": "%Y",
        "\d{1,2}/\d{1,2}/\d{4}$": "%d/%m/%Y",
        "\d{1,2}/\d{4}$": "%m/%Y",
        "\d{1,2}-\d{1,2}-\d{4}$": "%d-%m-%Y",
        "\d{1,2}-\d{4}$": "%m-%Y",
    }

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return u""

        if type(value) == date:
            return "{v.day:02d}/{v.month:02d}/{v.year}".format(v=value)
        else:
            return value

    def toFieldValue(self, value):
        if value == u"":
            return self.field.missing_value

        stripped = value.strip()
        for regex, datetime_format in self.regex_formats.items():
            if match(regex, stripped):
                try:
                    datetime.strptime(stripped, datetime_format)
                except ValueError:
                    raise FormatterValidationError(u"Date invalide {0}", value)
                else:
                    return stripped
        raise FormatterValidationError(
            u"Format d'encodage non reconnu (jour/mois/année, mois/année ou année)",
            value,
        )
