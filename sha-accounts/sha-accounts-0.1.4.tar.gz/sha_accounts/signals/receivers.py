from django.core.cache import caches
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from ..utils.jwt import JwtHelper
from ..models.user_models import User
from ..models import get_user_profile_model
from .signals import user_logged_in, user_logged_out, user_login_failed


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created, **kwargs):
    if created:
        get_user_profile_model().objects.create(user=instance)


@receiver(user_logged_in, sender=User)
def set_jwt_token(sender, user, **kwargs):
    user_fields = {}
    for field in settings.SHA_ACCOUNTS.get('JWT_USER_ENCODED_FIELDS'):
        if field == 'id':
            user_fields[field] = str(getattr(user, field, None))
            continue
        user_fields[field] = getattr(user, field, None)
    token = JwtHelper.encode({'user': user_fields})
    caches['token-cache'].set(token, 0)
    return token


@receiver(user_logged_out, sender=User)
def delete_jwt_token(sender, request, **kwrargs):
    token = request.headers.get('Authorization').split(' ')[1]
    caches['token-cache'].delete(token)
