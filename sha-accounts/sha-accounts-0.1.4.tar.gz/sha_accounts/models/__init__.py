from django.conf import settings
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured


def get_user_profile_model():
    try:
        return django_apps.get_model(settings.SHA_ACCOUNTS.get(
                                         'AUTH_USER_PROFILE_MODEL'))
    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_USER_PROFILE_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_PROFILE_MODEL refers to model '%s' that has not been installed" %
            settings.SHA_ACCOUNTS.get('AUTH_USER_PROFILE_MODEL'))


if settings.AUTH_USER_MODEL == 'sha_accounts.User':
    from .permission_models import Permission
    from .user_models import User
