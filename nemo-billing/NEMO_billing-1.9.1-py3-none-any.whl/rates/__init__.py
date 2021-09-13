from django.apps import AppConfig

from . import app_settings as defaults
from django.conf import settings

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NEMORatesConfig(AppConfig):
    name = "NEMO_billing.rates"
    verbose_name = "Rates"


default_app_config = "NEMO_billing.rates.NEMORatesConfig"
