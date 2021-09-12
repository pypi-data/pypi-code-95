
from .list import normalize_list
from django.http import HttpRequest

class UrlParamsUtils:
    STATUS_URL_PARAM_NAME = "status"
    STATUS_CODE_URL_PARAM_NAME = "status_code"

    CANCELED_URL_PARAM_VALUE = "canceled"

    def __init__(self, request: HttpRequest):
        self.request = request

    def get_param_value(self, param):
        return self.request.GET.get(param, None)

    def get_status(self):
        return self.get_param_value(self.STATUS_URL_PARAM_NAME)

    def has_status(self):
        return self.has_param(self.STATUS_URL_PARAM_NAME)

    def is_cancel_request(self):
        return self.get_status() == self.CANCELED_URL_PARAM_VALUE

    def has_param(self, params):
        params = normalize_list(params)

        for param in params:
            if self.get_param_value(param) != None:
                return True
        return False

    def has_status_code(self):
        return self.has_param(self.STATUS_CODE_URL_PARAM_NAME)

    def get_status_code(self):
        if self.has_status_code():
            return self.get_param_value(self.STATUS_CODE_URL_PARAM_NAME).upper()
        else:
            return None
