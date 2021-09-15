from django.dispatch import receiver
from sha_accounts.signals import user_logged_in
from django.contrib.auth import get_user_model


@receiver(user_logged_in, sender=get_user_model())
def send_activation_mail(sender, user, **kwargs):
    pass
