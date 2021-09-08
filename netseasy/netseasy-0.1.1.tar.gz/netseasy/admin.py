# -*- coding: utf-8 -*-
from django.contrib import admin
from netseasy.models import Client, Webhook, PaymentEvent, Payment


class WebhookOptions(admin.TabularInline):
    model = Webhook


class ClientOptions(admin.ModelAdmin):
    list_display = 'merchant_id site test_mode checkout integration_type'.split()
    search_fields = 'merchant_id site'.split()
    list_filter = 'checkout integration_type'.split()
    inlines = [
        WebhookOptions,
    ]


class PaymentEventOptions(admin.TabularInline):
    model = PaymentEvent

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PaymentOptions(admin.ModelAdmin):
    list_display = 'ordernumber client amount created_date status payment_type payment_method '.split()
    search_fields = 'ordernumber'.split()
    list_filter = 'client status payment_type payment_method'.split()
    inlines = [
        PaymentEventOptions,
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Client, ClientOptions)
admin.site.register(Payment, PaymentOptions)
