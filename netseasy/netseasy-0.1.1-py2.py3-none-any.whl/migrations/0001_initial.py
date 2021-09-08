# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('test_mode', models.BooleanField(default=True, verbose_name='Testmodus')),
                ('merchant_id', models.CharField(unique=True, help_text='Kontakt Nets for å få merchant-id', max_length=20, verbose_name='Forhandler ID')),
                ('checkout', models.CharField(choices=[('DS', 'Digital goods / services checkout'), ('FC', 'Full checkout'), ('OF', 'Payment methods on file'), ('MO', 'Mobile SDK')], max_length=2, verbose_name='Utsjekk')),
                ('integration_type', models.CharField(choices=[('H', 'HostedPaymentCheckout'), ('E', 'EmbeddedCheckout')], max_length=1, verbose_name='Integrasjonstype')),
                ('terms_url', models.URLField(verbose_name='Url til vilkår')),
                ('return_url', models.URLField(verbose_name='Url som Easy skal redirecte til')),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'Klienter',
                'verbose_name': 'Klient',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('ordernumber', models.CharField(max_length=32)),
                ('amount', models.IntegerField(help_text='Pris i øre', default=0)),
                ('currency', models.CharField(max_length=3)),
                ('easy_payment_id', models.CharField(null=True, max_length=100, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('processed_date', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(choices=[('I', 'Payment initialized'), ('P', 'Payment paid'), ('C', 'Payment credited')], default='I', max_length=1)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='netseasy.Client', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Betalinger',
                'verbose_name': 'Betaling',
            },
        ),
        migrations.CreateModel(
            name='PaymentEvent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('easy_id', models.CharField(max_length=64)),
                ('event', models.CharField(max_length=100)),
                ('data', models.TextField()),
                ('payment', models.ForeignKey(to='netseasy.Payment')),
            ],
            options={
                'verbose_name_plural': 'Betalingsaktiviteter',
                'verbose_name': 'Betalingsaktivitet',
            },
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('eventName', models.CharField(max_length=32)),
                ('client', models.ForeignKey(to='netseasy.Client')),
            ],
            options={
                'verbose_name_plural': 'Webhooks',
                'verbose_name': 'Webhook',
            },
        ),
    ]
