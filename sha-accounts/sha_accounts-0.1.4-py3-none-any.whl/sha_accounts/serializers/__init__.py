from django.conf import settings

if settings.SHA_ACCOUNTS.get('AUTH_USER_MODEL') == 'User':
    from .user_serializers import UserSignUpRequest, UserSignUpResponse
