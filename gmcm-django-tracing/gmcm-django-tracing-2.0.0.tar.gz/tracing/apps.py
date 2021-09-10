from django.apps import AppConfig


class TracingConfig(AppConfig):
    name = "tracing"
    verbose_name = "Rastreo"

    def ready(self):
        from . import signals
