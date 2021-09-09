from cnvrg.modules.base_module import CnvrgBase
from cnvrg.helpers.apis_helper import update_credentials, credentials as cred


class Cnvrg(CnvrgBase):
    def __init__(self, url="https://app.cnvrg.io", email=None, password=None, owner=None):
        if email and password:
            cred.login(email, password, api_url=url, owner=owner)
            update_credentials(cred)
