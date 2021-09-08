""" Apps file for setting gps visualization when app is ready
"""
import sys

from django.apps import AppConfig


class GpsVisualizationAppConfig(AppConfig):
    """Core application settings"""

    name = "core_gps_visualization_app"

    def ready(self):
        """Run when the app is ready

        Returns:

        """
        if "migrate" not in sys.argv:
            import core_gps_visualization_app.permissions.discover as discover
            discover.init_permissions()
