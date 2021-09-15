from django.conf import settings

from django_sso_app import dist_name, __version__


def get_stats_info(_request):
    return {
        "APP_NAME": dist_name,
        "DEPLOYMENT_ENV": settings.DEPLOYMENT_ENV,
        "REPOSITORY_REV": settings.REPOSITORY_REV,
        "SEMANTIC_VER": __version__
    }


def settings_context(_request):
    return {"settings": settings}
