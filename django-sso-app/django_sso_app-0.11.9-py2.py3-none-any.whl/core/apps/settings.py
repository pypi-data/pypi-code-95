from django.conf import settings


USERS_FOLDER = getattr(settings, 'USERS_FOLDER', settings.PRIVATE_ROOT.path("users"))
