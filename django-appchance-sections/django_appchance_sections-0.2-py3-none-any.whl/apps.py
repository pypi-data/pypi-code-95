from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SectionsConfig(AppConfig):
    name = "appchance_sections"
    label = "appchance_sections"
    verbose_name = _("Sections")
