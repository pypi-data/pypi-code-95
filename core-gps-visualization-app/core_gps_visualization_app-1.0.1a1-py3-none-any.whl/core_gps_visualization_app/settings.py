""" Apps file for setting core package when app is ready

"""

from django.conf import settings

if not settings.configured:
    settings.configure()

# MENU
GPS_VISUALIZATION_USER_MENU_NAME = getattr(settings, 'GPS_VISUALIZATION_USER_MENU_NAME', 'GPS Charts')
