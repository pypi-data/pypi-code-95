# -*- coding: utf-8 -*-
from plone.app.z3cform.interfaces import ITextWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer


class ITextTitleWidget(ITextWidget):
    """Marker interface for TextDate"""


@implementer(ITextTitleWidget)
class TextTitleWidget(TextWidget):
    def title_renderer(self):
        return True


@implementer(IFieldWidget)
def TextTitleFieldWidget(field, request):
    """IFieldWidget factory for TextDateWidget."""
    return FieldWidget(field, TextTitleWidget(request))
