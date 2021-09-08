""" Add GPS Visualization in main menu
"""

from django.urls import reverse
from menu import Menu, MenuItem

from core_gps_visualization_app.settings import GPS_VISUALIZATION_USER_MENU_NAME

Menu.add_item("main", MenuItem(GPS_VISUALIZATION_USER_MENU_NAME, reverse("core_gps_visualization_index")))
