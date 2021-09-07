import requests
import json

from pysecretserver.items import Secrets, Folders, Metadata
from pysecretserver.query import Request

class Api(object):
    """ The API object is the point of entry to pysecretserver.

    After instantiating the Api() with the appropriate named arguments
    you can specify which object type you with to interact with; namely
    secrets, folders and metadata, as an attribute.

    Calling any of these attributes will return
    :py:class:`.App`.

    :param str site: The base URL of the SecretServer instance you wish to connect
        to.
    :param str username: The Username to use to authenticate with.
    :param str password: The Password to use to authenticate with.
    """

    def __init__(self, site=None, username=None, password=None, proxies={}):

        self.site = site
        self.username = username
        self.password = password
        self.grant_type = 'password'
        self.http_session = requests.Session()
        if proxies:
          self.http_session.proxies.update(proxies)

        self.update_auth_token()

        self.Secrets = Secrets(self)
        self.Folders = Folders(self)
        self.Metadata = Metadata(self)

    def update_auth_token(self):

        req = Request(self.site, self.http_session)
        self.token = req.get_session_token({
            'username': self.username,
            'password': self.password,
            'grant_type': self.grant_type
        })
