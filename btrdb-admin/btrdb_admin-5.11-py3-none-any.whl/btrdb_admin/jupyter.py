# btrdb_admin.jupyter
# BTrDB Authenticator for JupyterHub
#
# Author:   PingThings
# Created:  Fri Oct 04 16:24:51 2019 -0400
#
# For license information, see LICENSE.txt
# ID: jupyter.py [] benjamin@pingthings.io $

"""
BTrDB Authenticator for JupyterHub
"""

##########################################################################
## Imports
##########################################################################

try:
    from tornado import gen
    from jupyterhub.auth import Authenticator
except ImportError:
    # Because these dependencies are not in requirements.txt
    raise ImportError("btrdb_admin.jupyter requires jupyterhub to be installed")

from btrdb_admin import connect
from btrdb_admin.exceptions import AdminAPIError
from btrdb_admin.utils.credentials import credentials_by_env, require_credentials


class BTrDBAuthenticator(Authenticator):
    """
    Authenticate JupyterHub access using the BTrDB IDP.
    """

    def __init__(self, *args, **kwargs):
        self._api = None
        super(BTrDBAuthenticator, self).__init__(*args, **kwargs)

    def _connect(self):
        # Was not sure if JupyterHub would keep this connection open forever so
        # am connecting and closing the API on each request to the server.
        # TODO: determine if this is efficient or not
        if not self._api:
            # For now we get the credentials entirely from the environment
            # TODO: look into JupyterHub specific configuration
            creds = require_credentials(credentials_by_env())
            self._api = connect(**creds)

    def _close(self):
        if self._api:
            try:
                self._api.close()
            finally:
                self._api = None

    @gen.coroutine
    def authenticate(self, handler, data):
        """
        Authenticate a user with login form data

        This must be a tornado gen.coroutine.
        It must return the username on successful authentication,
        and return None on failed authentication.

        Checking the whitelist is handled separately by the caller.

        Parameters
        ----------
        handler : tornado.web.RequestHandler
            the current request handler

        data : dict
            The formdata of the login form.
            The default form has 'username' and 'password' fields.

        Returns
        -------
        username : str or None
            The username of the authenticated user, or None if Authentication failed
        """
        try:
            # TODO: do we need to yield to ensure the coroutine is efficient?
            self._connect()
            user = self._api.authenticate_user(data["username"], data["password"])
            return user["username"]
        except AdminAPIError as e:
            # 445: user does not exist
            # 437: password is incorrect
            if handler is not None:
                req = "{}@{}".format(data["username"], handler.request.remote_ip)
            else:
                req = data["username"]

            self.log.warning(
                "BTrDB Authentication failed ({}): {}".format(req, e)
            )

        finally:
            self._close()
