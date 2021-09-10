from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SponsorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventsd.sponsors"
    label = "eventsd_sponsors"
    verbose_name = _("Sponsors")
