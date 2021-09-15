from django.apps import AppConfig


class ExamplesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'examples'

    def ready(self):
        import examples.signals
