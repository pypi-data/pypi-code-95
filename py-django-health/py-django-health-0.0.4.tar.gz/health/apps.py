from django.apps import AppConfig


class HealthConfig(AppConfig):
    name = 'health'

    def ready(self):
        """
        Configure health checkers
        """
        from health.conf import configurations
        from health.service import checker

        if configurations.enabled:
            for checker_pkg in configurations.checkers:
                checker.register(checker_pkg)
