from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventsd.events"
    label = "eventsd_events"
    verbose_name = _("Evènements")
