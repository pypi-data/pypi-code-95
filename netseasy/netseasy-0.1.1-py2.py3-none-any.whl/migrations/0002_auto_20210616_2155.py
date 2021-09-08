# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netseasy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='integration_type',
            field=models.CharField(choices=[('E', 'EmbeddedCheckout'), ('H', 'HostedPaymentCheckout')], verbose_name='Integrasjonstype', max_length=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('I', 'Payment initialized'), ('P', 'Payment paid'), ('C', 'Payment credited'), ('X', 'Payment cancelled')], default='I', max_length=1),
        ),
    ]
