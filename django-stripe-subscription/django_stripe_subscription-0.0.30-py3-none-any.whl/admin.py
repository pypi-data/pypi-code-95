from django.conf import settings
from django.contrib import admin

import stripe

from . import models


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_id', 'product_id', 'price', 'published')
    list_filter = ('published',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price_id', 'product_id']

        if obj and obj.id:
            readonly_fields += ['price', 'recurring_interval']

        return readonly_fields


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    change_form_template = 'stripe_subscription/admin/change-form.html'

    readonly_fields = (
            'created_at', 'updated_at', 'user',
            'plan', 'customer_id', 'subscription_id', 'quiz')
    list_display = ('user_email', 'created_at', 'updated_at',
                    'customer_id', 'subscription_id', 'is_active')
    search_fields = ('user__email', 'customer_id', 'subscription_id')
    list_filter = ('is_active', 'created_at')

    def stripe_plan(self, obj=None):
        if obj:
            return obj.plan.title

    def user_email(self, obj=None):
        if obj:
            return obj.user.email or 'not specified'

    stripe_plan.short_description = 'Plan'

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                "fields": ['is_active', 'created_at', 'updated_at']
            }),
            ('Stripe', {
                "fields": ['customer_id', 'subscription_id']
            }),
        ]

        if request.user.is_superuser:
            fieldsets[0][1]['fields'].insert(0, 'user')
            fieldsets[1][1]['fields'].insert(0, 'plan')
        else:
            fieldsets[1][1]['fields'].insert(0, 'stripe_plan')

        return fieldsets

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        obj = self.get_object(request, object_id)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        if obj:
            customer = stripe.Customer.retrieve(obj.customer_id)
            subscription = stripe.Subscription.retrieve(obj.subscription_id)

            if subscription.default_payment_method:
                payment_method = stripe.PaymentMethod.retrieve(
                        subscription.default_payment_method)
            else:
                payment_method = None

            extra_context.update({
                'object': obj,
                'request': request,
                'customer': customer,
                'subscription': subscription,
                'payment_method': payment_method
            })

        return super().change_view(request, object_id, form_url, extra_context)
