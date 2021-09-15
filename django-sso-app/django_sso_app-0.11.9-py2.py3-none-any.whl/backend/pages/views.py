from django.conf import settings

from meta.views import MetadataMixin

from ...core.mixins import WebpackBuiltTemplateViewMixin
from ... import app_settings


class HomeView(MetadataMixin, WebpackBuiltTemplateViewMixin):
    description = settings.META_DESCRIPTION
    url = app_settings.APP_URL
