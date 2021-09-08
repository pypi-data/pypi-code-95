# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.db import models


class Client(models.Model):
    """This model holds site-specific data that is used to connect to Easy.
    """
    CHECKOUT_TYPES = (
        ('DS', 'Digital goods / services checkout'),
        ('FC', 'Full checkout'),
        ('OF', 'Payment methods on file'),
        ('MO', 'Mobile SDK')
    )
    INTEGRATION_TYPES = {
        'E': 'EmbeddedCheckout',
        'H': 'HostedPaymentCheckout'
    }
    site = models.OneToOneField(
        Site,
        on_delete=models.PROTECT,        
    )
    test_mode = models.BooleanField(
        default=True,
        verbose_name="Testmodus"
    )
    merchant_id = models.CharField(
        max_length=20,
        verbose_name="Forhandler ID",
        help_text="Kontakt Nets for å få merchant-id",
        unique=True
    )
    checkout = models.CharField(
        max_length=2,
        choices=CHECKOUT_TYPES,
        verbose_name="Utsjekk"
    )
    integration_type = models.CharField(
        max_length=1,
        choices=tuple(INTEGRATION_TYPES.items()),
        verbose_name="Integrasjonstype"
    )
    terms_url = models.URLField(verbose_name="Url til vilkår")
    return_url = models.URLField(
        verbose_name="Url som Easy skal redirecte til"
    )

    def __str__(self):
        return self.site.name

    class Meta:
        app_label = 'netseasy'
        verbose_name = 'Klient'
        verbose_name_plural = 'Klienter'


class Webhook(models.Model):
    """Activate webhooks by adding them here.
    
       Find a list of avaliable webhooks here:
       https://developers.nets.eu/nets-easy/en-EU/api/webhooks/

       Adding the webhook here will make sure that the data posted to the
       webhook will be stored in the PaymentEvent model. If further actions
       are required based on a webhook, you must implement a signal handler
       that triggers post-save on PaymentEvent in your app.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    eventName = models.CharField(max_length=32)

    class Meta:
        app_label = 'netseasy'
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
