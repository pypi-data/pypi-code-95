# -*- coding: utf-8 -*-
from ..interfaces import ILibraryCoreLayer
from collective.z3cform.select2.widget.widget import SingleSelect2FieldWidget
from z3c.form import interfaces

import zope.component
import zope.interface
import zope.schema.interfaces


@zope.component.adapter(zope.schema.interfaces.IChoice, ILibraryCoreLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ChoiceWidgetDispatcher(field, request):
    """Dispatch widget for IChoice based also on its source."""

    if not field.vocabulary:  # simple taxonomy
        return SingleSelect2FieldWidget(field, request)
    else:
        return zope.component.getMultiAdapter(
            (field, field.vocabulary, request), interfaces.IFieldWidget
        )
