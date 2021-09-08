# -*- coding: utf-8 -*-
import requests
from django.conf import settings
from netseasy.credentials import get_easy_ctx
from netseasy.models import Payment


class NetsEasyPaymentException(Exception):
    """Failed to create payment in Nets Easy
    """


def get_easy_payment_id(payment_id, items):
    """This is where we call the Payment REST-API at Nets Easy and store the
       payment_id if everything goes ok.
       The Payment API is the initial step. After this step, we must display
       a webpage that includes a checkout.js file to display the terminal.
    """
    payment = Payment.objects.get(id=payment_id)
    payment_json = payment.create_payment_json(items)
    response = requests.post(
        settings.EASY_PAYMENT_URL,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": get_easy_ctx().secret_key
        },
        data=payment_json,
    )
    try:
        if response.status_code != 201:
            raise NetsEasyPaymentException
        easy_payment_id = response.json()["paymentId"]
        payment.easy_payment_id = easy_payment_id
        payment.save()
    except NetsEasyPaymentException:
        easy_payment_id = None

    return easy_payment_id, response.status_code
