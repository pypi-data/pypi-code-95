# -*- coding: utf-8 -*-
from plone.schemaeditor.fields import FieldFactory
from plone.supermodel.exportimport import BaseHandler
from product.recaptcha_invisible import _
from product.recaptcha_invisible.interfaces import IRecaptchaInvisibleField
from zope.interface import implementer
from zope.schema import TextLine


@implementer(IRecaptchaInvisibleField)
class RecaptchaInvisibleField(TextLine):
    """ Recaptcha Invisible Field
    """


RecaptchaInvisibleFactory = FieldFactory(
    RecaptchaInvisibleField,
    _(u'Recaptcha Invisible'),
)
RecaptchaInvisibleHandler = BaseHandler(RecaptchaInvisibleField)
