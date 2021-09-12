import configparser
import os

from . import models
from .auth import ApiTokenAuth
from .config import Config
from .exceptions import InitializationError
from .models.utils import CachedProperty
from .requestor import Requestor, urljoin
from .serializer import Serializer

User = models.User
Bot = models.Bot
RedditApp = models.RedditApp
RefreshToken = models.RefreshToken
UserVerification = models.UserVerification
SentryToken = models.SentryToken
DatabaseCredential = models.DatabaseCredential


class CredentialManager(object):
    """The CredentialManager class provides a way to interact with CredentialManager's API.

    The official way to initialize an instance of this class is to:

    .. code-block:: python

        from credmgr import CredentialManager

        credentialManager = CredentialManager(apiToken="LIqbGjAeep3Ws5DH3LOEQPmw8UZ6ek")

    .. note::

        It is recommended to use environment variables or a ``.credmgr.ini`` file. See
        :ref:`Auth documentation <auth>` for more details.

    """

    _default = None
    _endpoint = "/api/v1"

    def __init__(
        self, configName=None, sessionClass=None, sessionKwargs=None, **kwargs
    ):
        """Initialize a CredentialManager instance.

        :param str configName: The name of a section in your ``.credmgr.ini`` file that
            credmgr will load its configuration is loaded from. If ``configName`` is
            ``None``, then it will look for it in the environment variable
            ``credmgr_configName``. If it is not found there, the ``default`` section is
            used.
        :param Session sessionClass: A Session class that will be used to create a
            requestor. If not set, use ``requests.Session`` (default: None).
        :param dict sessionKwargs: Dictionary with additional keyword arguments used to
            initialize the session (default: None).

        Additional keyword arguments will be used to initialize the :class:`.Config`
        object. This can be used to specify configuration settings during instantiation
        of the :class:`.CredentialManager` instance. For more details please see
        :ref:`configuration`.

        Required settings are:

        - apiToken

        OR

        - username
        - password

        .. warning::

            Using an API Token instead of a username/password is strongly recommended!

        The ``sessionClass`` and ``sessionKwargs`` allow for customization of the
        session :class:`.CredentialManager` will use. This allows, e.g., easily adding
        behavior to the requestor or wrapping its |Session|_ in a caching layer. Example
        usage:

        .. |Session| replace:: ``Session``

        .. _session: https://2.python-requests.org/en/master/api/#requests.Session

        .. code-block:: python

            import json, betamax, requests


            class JSONDebugRequestor(Requestor):
                def request(self, *args, **kwargs):
                    response = super().request(*args, **kwargs)
                    print(json.dumps(response.json(), indent=4))
                    return response


            mySession = betamax.Betamax(requests.Session())
            credentialManager = CredentialManager(
                ..., sessionClass=JSONDebugRequestor, session=mySession
            )

        """
        if sessionKwargs is None:
            sessionKwargs = {}
        configSection = None
        try:
            configSection = configName or os.getenv("credmgr_configName") or "DEFAULT"
            self.config = Config(configSection, **kwargs)
        except configparser.NoSectionError as exc:
            if configSection is not None:
                exc.message += "\nYou provided the name of a .credmgr.ini section that doesn't exist."
            raise

        self._server = urljoin(
            getattr(self.config, "server"), getattr(self.config, "endpoint")
        )
        apiToken = getattr(self.config, "apiToken")
        username = getattr(self.config, "username")
        password = getattr(self.config, "password")

        initErrorMessage = "Required settings are missing. Either 'apiToken' OR 'username' and 'password' must be specified, These settings can be provided in a .credmgr.ini file, as a keyword argument during the initialization of the `CredentialManager` class, or as an environment variable."
        if all([apiToken, username, password]):
            raise InitializationError(initErrorMessage)
        if apiToken:
            self._auth = ApiTokenAuth(apiToken)
        elif username and password:
            self._auth = (username, password)
        else:
            raise InitializationError(
                "API Token or a username/password pair must be set."
            )

        self._requestor = Requestor(
            self._server, self._auth, sessionClass, **sessionKwargs
        )
        self.serializer = Serializer(self)
        self._currentUser = None
        self._userDefaults = None
        self.getUserDefault = lambda key, default: self.userDefaults.get(key, default)
        self.user = models.UserHelper(self)
        """An instance of :class:`.UserHelper`.

        Provides an interface for interacting with :class:`.User`. For example, to get a
        :class:`.User` with :attr:`id` of ``1`` you can do:

        .. code-block:: python

            user = credentialManager.user(1)
            print(user.id)

        To create a :class:`.User` do:

        .. code-block:: python

            user = credentialManager.user.create(**userKwargs)

        See :meth:`~.UserHelper.create` for the required params.

        """
        self.bot = models.BotHelper(self)
        """An instance of :class:`.BotHelper`.

        Provides an interface for interacting with :class:`.Bot`. For example, to get a
        :class:`.Bot` with :attr:`id` of ``1`` you can do:

        .. code-block:: python

            bot = credentialManager.bot(1)
            print(bot.id)

        To create a :class:`.Bot` do:

        .. code-block:: python

            bot = credentialManager.bot.create(**botKwargs)

        See :meth:`~.BotHelper.create` for the required params.

        """

        self.redditApp = models.RedditAppHelper(self)
        """An instance of :class:`.RedditAppHelper`.

        Provides an interface for interacting with :class:`.RedditApp`. For example, to
        get a :class:`.RedditApp` with :attr:`id` of ``1`` you can do:

        .. code-block:: python

            redditApp = credentialManager.redditApp(1)
            print(redditApp.id)

        To create a :class:`.RedditApp` do:

        .. code-block:: python

            redditApp = credentialManager.redditApp.create(**redditAppKwargs)

        See :meth:`~.RedditAppHelper.create` for the required params.

        """

        self.refreshToken = models.RefreshTokenHelper(self)
        """An instance of :class:`.RefreshTokenHelper`.

        Provides an interface for interacting with :class:`.RefreshToken`. For example
        to get a :class:`.RefreshToken` with :attr:`id` of ``1`` you can do:

        .. code-block:: python

            refreshToken = credentialManager.refreshToken(1)
            print(refreshToken.id)

        .. note::

            Refresh tokens cannot be manually created.

        """

        self.userVerification = models.UserVerificationHelper(self)
        """An instance of :class:`.UserVerificationHelper`.

        Provides an interface for interacting with :class:`.UserVerification`. For
        example to get a :class:`.UserVerification` with :attr:`id` of ``1`` you can do:

        .. code-block:: python

            userVerification = credentialManager.userVerification(1)
            print(userVerification.id)

        To create a :class:`.UserVerification` do:

        .. code-block:: python

            userVerification = credentialManager.userVerification.create(**userVerificationKwargs)

        See :meth:`~.UserVerificationHelper.create` for the required params.

        """

        self.sentryToken = models.SentryTokenHelper(self)
        """An instance of :class:`.SentryTokenHelper`.

        Provides an interface for interacting with :class:`.SentryToken`. For example to
        get a :class:`.SentryToken` with :attr:`id` of ``1`` you can do:

        .. code-block:: python

            sentryToken = credentialManager.sentryToken(1)
            print(sentryToken.id)

        To create a :class:`.SentryToken` do:

        .. code-block:: python

            sentryToken = credentialManager.sentryToken.create(**sentryTokenKwargs)

        See :meth:`~.SentryTokenHelper.create` for the required params.

        """

        self.databaseCredential = models.DatabaseCredentialHelper(self)
        """An instance of :class:`.DatabaseCredentialHelper`.

        Provides an interface for interacting with :class:`.DatabaseCredential`. For
        example to get a :class:`.DatabaseCredential` with :attr:`id` of ``1`` you can
        do:

        .. code-block:: python

            databaseCredential = credentialManager.databaseCredential(1)
            print(databaseCredential.id)

        To create a :class:`.DatabaseCredential` do:

        .. code-block:: python

            databaseCredential = credentialManager.databaseCredential.create(
                **databaseCredentialKwargs
            )

        See :meth:`~.DatabaseCredentialHelper.create` for the required params.

        """

    def users(self, batchSize=10, limit=None):
        """List Users

        :param int batchSize: Number of Users to return in each batch (default: ``20``)
        :param int limit: Maximum number of Users to return

        :returns: A :class:`.Paginator` to iterate through the Users

        """
        return User(self).listItems(batchSize=batchSize, limit=limit)

    def bots(self, batchSize=20, limit=None, owner=None):
        """List Bots

        :param int batchSize: Number of Bots to return in each batch (default: ``20``)
        :param int limit: Maximum number of Bots to return
        :param Union[int,str,User] owner: Return Bots that are owner by this user

        :returns: A :class:`.Paginator` to iterate through the Bots

        """
        return Bot(self).listItems(batchSize=batchSize, limit=limit, owner=owner)

    def redditApps(self, batchSize=20, limit=None, owner=None):
        """List RedditApps

        :param int batchSize: Number of RedditApps to return in each batch (default:
            ``20``)
        :param int limit: Maximum number of RedditApps to return
        :param Union[int,str,User] owner: Return RedditApps that are owner by this user

        :returns: A :class:`.Paginator` to iterate through the Reddit Apps

        """
        return RedditApp(self).listItems(batchSize=batchSize, limit=limit, owner=owner)

    def refreshTokens(self, batchSize=20, limit=None, owner=None):
        """List RefreshTokens

        :param int batchSize: Number of RefreshTokens to return in each batch (default:
            ``20``)
        :param int limit: Maximum number of RefreshTokens to return
        :param Union[int,str,User] owner: Return RefreshTokens that are owned by this
            user

        :returns: A :class:`.Paginator` to iterate through the Refresh Tokens

        .. note::

            This is *not* the intended way to fetch refresh tokens. See:
            :meth:`~.RedditApp.reddit` for obtaining an authorized reddit instance.

        """
        return RefreshToken(self).listItems(
            batchSize=batchSize, limit=limit, owner=owner
        )

    def userVerifications(self, batchSize=20, limit=None, owner=None):
        """List UserVerifications

        :param int batchSize: Number of UserVerifications to return in each batch
            (default: ``20``)
        :param int limit: Maximum number of UserVerifications to return
        :param Union[int,str,User] owner: Return UserVerifications that are owned by
            this user

        :returns: A :class:`.Paginator` to iterate through the UserVerifications.

        """
        return UserVerification(self).listItems(
            batchSize=batchSize, limit=limit, owner=owner
        )

    def sentryTokens(self, batchSize=20, limit=None, owner=None):
        """List SentryTokens

        :param int batchSize: Number of SentryTokens to return in each batch (default:
            ``20``)
        :param int limit: Maximum number of SentryTokens to return
        :param Union[int,str,User] owner: Return SentryTokens that are owned by this
            user

        :returns: A :class:`.Paginator` to iterate through the SentryTokens

        """
        return SentryToken(self).listItems(
            batchSize=batchSize, limit=limit, owner=owner
        )

    def databaseCredentials(self, batchSize=20, limit=None, owner=None):
        """List DatabaseCredentials

        :param int batchSize: Number of DatabaseCredentials to return in each batch
            (default: ``20``)
        :param int limit: Maximum number of DatabaseCredentials to return
        :param Union[int,str,User] owner: Return DatabaseCredentials that are owned by
            this user

        :returns: A :class:`.Paginator` to iterate through the DatabaseCredentials

        """
        return DatabaseCredential(self).listItems(
            batchSize=batchSize, limit=limit, owner=owner
        )

    @CachedProperty
    def currentUser(self) -> User:
        """Returns the currently authenticated :class:`.User`"""
        if not self._currentUser:
            self._currentUser = self.get("/users/me")
        return self._currentUser

    @CachedProperty
    def userDefaults(self):
        """Returns the currently authenticated :class:`.User`'s default settings"""
        if not self._userDefaults:
            self._userDefaults = self.currentUser.defaultSettings
        return self._userDefaults

    def get(self, path, params=None):
        return self.serializer.deserialize(
            self._requestor.request(path, "GET", params=params)
        )

    def post(self, path, data):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return self.serializer.deserialize(
            self._requestor.request(path, "POST", data=data, headers=headers)
        )

    def patch(self, path, data):
        return self.serializer.deserialize(
            self._requestor.request(path, "PATCH", json=data)
        )

    def delete(self, path):
        return self._requestor.request(path, "DELETE")
