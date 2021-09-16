from typing import List

from allauth.account.admin import EmailAddressAdmin
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.db import transaction

from NEMO.admin import UserAdmin


@transaction.atomic
def verify_user_emails(modeladmin, request, queryset):
    already_verified = EmailAddress.objects.filter(verified=True).values_list("email", flat=True)
    for user in queryset:
        if user.email and user.email not in already_verified:
            EmailAddress.objects.update_or_create(
                user=user, email=user.email, verified=False, defaults={"verified": True}
            )


verify_user_emails.short_description = "Mark the email address of the selected users as verified"


@transaction.atomic
def send_user_email_confirmation(modeladmin, request, queryset):
    already_verified = EmailAddress.objects.filter(verified=True).values_list("email", flat=True)
    for user in queryset:
        if user.email and user.email not in already_verified:
            send_email_confirmation(request, user)


send_user_email_confirmation.short_description = "Send an email verification to the selected users"


@transaction.atomic
def send_unverified_email_confirmation(modeladmin, request, queryset: List[EmailAddress]):
    for email in queryset:
        if not email.verified:
            send_email_confirmation(request=request, user=email.user, email=email.email)


send_unverified_email_confirmation.short_description = "Send an email verification to the selected unverified emails"


# Expand All Auth email address admin action to add send_unverified_email_confirmation
new_email_address_actions = EmailAddressAdmin.actions.copy()
new_email_address_actions.append(send_unverified_email_confirmation)
EmailAddressAdmin.actions = new_email_address_actions


# Expand NEMO user admin action to add verify_user_emails and send_user_email_confirmation
new_user_actions = UserAdmin.actions.copy()
new_user_actions.extend([verify_user_emails, send_user_email_confirmation])
UserAdmin.actions = new_user_actions
