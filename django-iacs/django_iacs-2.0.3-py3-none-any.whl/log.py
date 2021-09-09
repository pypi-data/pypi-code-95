import logging

from django.conf import settings


class IacsLogger(type):

    def __new__(cls, name, bases, attrs):
        attrs['logger'] = logging.getLogger(settings.IACS_SETTINGS["RUNNING_LOG_NAME"])
        attrs['error'] = logging.getLogger(settings.IACS_SETTINGS["ERROR_LOG_NAME"])
        return super(IacsLogger, cls).__new__(cls, name, bases, attrs)
