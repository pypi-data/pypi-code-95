from django.apps import AppConfig


class FlashboardConfig(AppConfig):
    name = "flashboard"

    def ready(self):
        from touchtechnology.content.utils import install_placeholder

        install_placeholder("flashboard")
