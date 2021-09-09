# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from product.recaptcha_invisible import _
from z3c.form import validator
from zope.component import getMultiAdapter
from zope.schema import ValidationError


class InvalidRecaptchaInvisibleError(ValidationError):
    __doc__ = _('Failed to verify Recaptcha')


class RecaptchaInvisibleValidator(validator.SimpleFieldValidator):
    """ Recaptcha Invisible Validator
    """

    def validate(self, value):
        super().validate(value)

        recaptcha_invisible_verify = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='recaptcha_invisible_verify',
        )

        if not recaptcha_invisible_verify.verify():
            raise InvalidRecaptchaInvisibleError

        return True
