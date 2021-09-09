# -*- coding: utf-8 -*-
from plone import api
from product.recaptcha_invisible import _
from Products.Five import BrowserView
from zope import schema
from zope.annotation import factory
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import requests


class IRecaptchaInvisibleInfo(Interface):
    error = schema.TextLine()
    verified = schema.Bool()


@adapter(IBrowserRequest)
@implementer(IRecaptchaInvisibleInfo)
class RecaptchaInvisibleInfoAnnotation(object):
    def __init__(self):
        self.error = None
        self.verified = False


RecaptchaInvisibleInfo = factory(RecaptchaInvisibleInfoAnnotation)


class RecaptchaResponse:
    """ Recaptcha Response
    """

    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code

    def __repr__(self):
        return 'Recaptcha response: {0} {1}'.format(self.is_valid, self.error_code)

    def __str__(self):
        return self.__repr__()


class RecaptchaInvisibleVerifyView(BrowserView):
    """ Recaptcha Invisible Verify View
    """

    VERIFY_SERVER = 'www.google.com'

    def verify(self, input=None):
        info = IRecaptchaInvisibleInfo(self.request)
        if info.verified:
            return True

        private_key = api.portal.get_registry_record('recaptcha_invisible.private_key')
        if not private_key:
            raise ValueError(_('No recaptcha private key configured'))

        response_field = self.request.get('g-recaptcha-response')
        remote_addr = self.request.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
        if not remote_addr:
            remote_addr = self.request.get('REMOTE_ADDR')

        res = self.verify_requests(response_field, private_key, remote_addr, self.VERIFY_SERVER)
        if res.error_code:
            info.error = res.error_code

        info.verified = res.is_valid
        return res.is_valid

    def verify_requests(self, recaptcha_response_field, secret_key, remoteip, verify_server):
        if not (recaptcha_response_field and len(recaptcha_response_field)):
            return RecaptchaResponse(is_valid=False, error_code='incorrect-captcha-sol')

        params = {
            'secret': secret_key,
            'remoteip': remoteip,
            'response': recaptcha_response_field,
        }

        r = requests.post(
            url='https://{0}/recaptcha/api/siteverify'.format(verify_server),
            data=params,
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'noReCAPTCHA Python',
            },
        )

        response = r.json()
        return_code = response['success']
        error_codes = response.get('error-codes', [])

        if return_code:
            return RecaptchaResponse(is_valid=True)
        else:
            return RecaptchaResponse(is_valid=False, error_code=error_codes)
