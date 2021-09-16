# -*- coding: utf-8 -*-
from plone.app.z3cform.interfaces import ITextWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer


class IHiddenHoneyPotWidget(ITextWidget):
    """Marker interface for TextDate"""


@implementer(IHiddenHoneyPotWidget)
class HiddenHoneyPotWidget(TextWidget):

    style = "display:none"

    def title_renderer(self):
        return False


@implementer(IFieldWidget)
def HiddenHoneyPotFieldWidget(field, request):
    return FieldWidget(field, HiddenHoneyPotWidget(request))
