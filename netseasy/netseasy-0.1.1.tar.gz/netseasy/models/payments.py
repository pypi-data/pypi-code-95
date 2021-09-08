# -*- coding: utf-8 -*-
import datetime
import json
from django.conf import settings
from django.db import models
from netseasy.authorization import encrypt
from netseasy.credentials import get_easy_ctx
from netseasy.models.basedata import Client


class Payment(models.Model):
    """This model holds the payment-transaction that is created when a sale is
       initiated by the customer.
       The next step is to call the payment-interface to get the
       easy_payment_id.
    """
    PAYMENT_STATUS = (
        ('I', 'Payment initialized'),
        ('P', 'Payment paid'),
        ('C', 'Payment credited'),
        ('X', 'Payment cancelled'),
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ordernumber = models.CharField(
        max_length=32
    )
    amount = models.IntegerField(
        default=0,
        help_text='Pris i øre'
    )
    currency = models.CharField(
        max_length=3
    )
    easy_payment_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=1,
        default='I',
        choices=PAYMENT_STATUS
    )
    payment_method = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    payment_type = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    def validate_payment_item(self, item):
        """Validate item.
        """
        # XXX: probably need some real validation ;-)
        return {
            "reference": item['id'],
            "name": item['name'],
            "quantity": item['quantity'],
            "unit": item['unit'],
            "unitPrice": item['unit_price'],
            "taxRate": item['tax_rate'],
            "taxAmount": item['tax_amount'],
            "grossTotalAmount": item['gross_total_amount'],
            "netTotalAmount": item['net_total_amount']
        }

    def create_payment_json(self, items: list) -> str:
        """Create json that will be sent as a datastring to Nets Easy.

           ref: https://tech.dibspayment.com/easy/integration-guide#createpayment
           datastring: https://tech.dibspayment.com/easy/api/datastring-parameters

           Args: 
               items: This is a list of dicts with these fields:

                   id, 
                   name, 
                   quantity: (int) ... 
                   unit, 
                   unit_price, 
                   tax_rate,
                   tax_amount, 
                   gross_total_amount, 
                   net_total_amount

           Returns:
               A json-formatted string to be sent to Easy.
        """
        auth_key = encrypt(get_easy_ctx().encryption_key, self.id)
        payment = {
            "order": {
                "amount": self.amount * 100,
                "currency": self.currency,
                "reference": self.ordernumber,
                "items": []
            },
            "checkout": {
                "charge": self.client.checkout == 'DS',
                "url": self.client.site.domain,
                "termsUrl": self.client.terms_url,
                "shipping": {
                    "countries": [{
                        "countryCode": "NOR"
                    }],
                    "merchantHandlesShippingCost": False
                },
                "integrationType": self.client.INTEGRATION_TYPES[self.client.integration_type],
                "consumerType": {
                    "supportedTypes": ["B2C", "B2B"],
                    "default": "B2C"
                }
            },
            "notifications": {
                "webhooks": []
            }
        }

        for notification in self.client.webhook_set.all():
            payment['notifications']['webhooks'].append({
                "eventName": notification.eventName,
                "url": '{}/webhook/{}/'.format(
                    settings.EASY_WEBHOOK_URL,
                    notification.id
                ),
                "authorization": auth_key
            })
        for item in items:
            payment['order']['items'].append(self.validate_payment_item(item))

        return json.dumps(payment)

    @staticmethod
    def update_payment(easy_payment_id, status, payment_method='', payment_type=''):
        try:
            payment = Payment.objects.get(easy_payment_id=easy_payment_id)
            payment.status = status
            payment.processed_date = datetime.datetime.now()
            if payment_type:
                payment.payment_type = payment_type
            if payment_method:
                payment.payment_method = payment_method
            payment.save()
            return payment
        except Payment.DoesNotExist:
            raise

    def __str__(self):
        return '{id}: {order} - status'.format(
            id=self.id,
            order=self.ordernumber,
            status=self.status
        )

    class Meta:
        app_label = 'netseasy'
        verbose_name = 'Betaling'
        verbose_name_plural = 'Betalinger'


class PaymentEvent(models.Model):
    """The activated webhooks will put data into this model. If an action is
       required based on the webhook, create a signal-handler on post-save of
       this model.
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    easy_id = models.CharField(max_length=64)
    event = models.CharField(max_length=100)
    data = models.TextField()

    def __str__(self):
        return '{id}: {payment} - {event}'.format(
            id=self.id,
            payment=self.payment_id,
            event=self.event
        )

    class Meta:
        app_label = 'netseasy'
        verbose_name = 'Betalingsaktivitet'
        verbose_name_plural = 'Betalingsaktiviteter'
