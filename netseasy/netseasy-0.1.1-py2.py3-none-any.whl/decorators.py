# -*- coding: utf-8 -*-
import json

from django.core.exceptions import PermissionDenied
from netseasy.authorization import decrypt
from netseasy.credentials import get_easy_ctx
from netseasy.models import Payment


def validate_request(function):
    """Validate the webhook-calls by checking the authorization header in the
       request using the decrypt-function provided by this app.
       The decrypted value must be equal to the paymentId.
    """
    def wrap(request, *args, **kwargs):
        auth = request.META['HTTP_AUTHORIZATION']
        auth_value = decrypt(
            get_easy_ctx().encryption_key,
            auth
        )
        data = json.loads(request.body.decode('utf-8'))['data']
        payment = Payment.objects.get(easy_payment_id=data['paymentId'])
        if auth_value == payment.id:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
