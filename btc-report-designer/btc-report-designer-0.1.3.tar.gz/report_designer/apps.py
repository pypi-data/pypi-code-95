from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ReportDesignerConfig(AppConfig):
    name = 'report_designer'
    verbose_name = _('Конструктор отчетов')
