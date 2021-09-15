from django.conf import settings
from .signals import user_logged_in, user_logged_out, user_login_failed

if settings.AUTH_USER_MODEL == 'sha_accounts.User':
    from .receivers import create_profile
