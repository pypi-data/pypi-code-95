from django.conf import settings
from django.db.models.signals import pre_save, post_save

from NEMO_allauth.admin import send_user_email_confirmation
from NEMO.models import User


def post_save_user_verify_email(sender, instance: User, raw, created, using, update_fields, **kwargs):
    if settings.SEND_EMAIL_VERIFICATION_ON_USER_SAVE:
        if hasattr(instance, "_email_changed") and instance._email_changed:
            send_user_email_confirmation(None, None, [instance])


def pre_save_check_email_changed(sender, instance: User, raw, using, update_fields, **kwargs):
    if settings.SEND_EMAIL_VERIFICATION_ON_USER_SAVE:
        if not instance.pk or instance.email != User.objects.get(id=instance.pk).email:
            instance._email_changed = True


# Connect pre and post save so a verification email can be sent on user creation or email change
pre_save.connect(pre_save_check_email_changed, sender=User)
post_save.connect(post_save_user_verify_email, sender=User)
