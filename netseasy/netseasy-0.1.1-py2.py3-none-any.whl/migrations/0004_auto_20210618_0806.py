# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netseasy', '0003_auto_20210617_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='integration_type',
            field=models.CharField(choices=[('H', 'HostedPaymentCheckout'), ('E', 'EmbeddedCheckout')], max_length=1, verbose_name='Integrasjonstype'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='easy_payment_id',
            field=models.CharField(blank=True, null=True, max_length=100, db_index=True),
        ),
    ]
