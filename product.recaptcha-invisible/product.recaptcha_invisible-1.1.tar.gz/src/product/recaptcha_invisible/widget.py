# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from product.recaptcha_invisible import _
from product.recaptcha_invisible.interfaces import IRecaptchaInvisibleField
from product.recaptcha_invisible.interfaces import IRecaptchaInvisibleWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@implementer(IRecaptchaInvisibleWidget)
class RecaptchaInvisibleWidget(TextWidget):

    name = 'recaptcha-invisible-widget'
    label = _('Recaptcha Invisible Widget')
    timestamp = datetime.now().strftime('%s')

    def site_key(self):
        public_key = api.portal.get_registry_record('recaptcha_invisible.public_key')
        return public_key


@implementer(IFieldWidget)
@adapter(IRecaptchaInvisibleField, IFormLayer)
def ReCaptchaInvisibleFieldWidget(field, request):
    return FieldWidget(field, RecaptchaInvisibleWidget(request))
