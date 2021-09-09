from zeep import Client

from ..constants import WSDL_URL


class BaseSoapWrapper:
    def __init__(self, wsdl_url=None):
        if wsdl_url is None:
            self.wsdl = WSDL_URL
        else:
            self.wsdl = wsdl_url

    def get_client(self):
        return Client(self.wsdl)
