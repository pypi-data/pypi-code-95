import logging

from ..exceptions import InitializationError
from ..mixins import BaseModel
from . import (
    Bot,
    DatabaseCredential,
    RedditApp,
    RefreshToken,
    SentryToken,
    User,
    UserVerification,
)
from .utils import resolveUser

log = logging.getLogger(__package__)


class Paginator:
    @resolveUser()
    def __init__(self, credmgr, model, batchSize=20, limit=None, itemsOwner=None):
        """Initialize a Paginator instance.

        :param credmgr: An instance of :class:`.CredentialManager`.
        :param model: A CredentialManager model to list.
        :param int batchSize: The number of items to fetch at a time. If ``batchSize``
            is None, it will fetch them 100 at a time. (default: 20).
        :param int limit: The maximum number of items to get.
        :param Union[int,User,str] itemsOwner: Owner to filter the items by.

        """
        self._credmgr = credmgr
        self._model = model(self._credmgr)
        self.batchSize = batchSize
        self.limit = limit
        self.itemsOwner = itemsOwner
        self._itemsReturned = 0
        self._completed = False
        self._offset = 0
        self._currentItemIndex = None
        self._response = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.limit is not None and self._itemsReturned >= self.limit:
            raise StopIteration()  # pragma: no cover

        if self._response is None or self._currentItemIndex >= len(self._response):
            self._next()

        self._currentItemIndex += 1
        self._itemsReturned += 1
        return self._response[self._currentItemIndex - 1]

    def _next(self):
        if self._completed:
            raise StopIteration()
        params = dict(limit=self.batchSize, offset=self._offset)
        if self.itemsOwner:
            params["owner_id"] = self.itemsOwner
        self._response = self._credmgr.get(self._model._path, params=params)
        self._currentItemIndex = 0
        if not self._response:
            raise StopIteration()  # pragma: no cover
        if self._response and len(self._response) == self.batchSize:
            self._offset += self.batchSize  # pragma: no cover
        else:
            self._completed = True


class BaseHelper(BaseModel):
    _model = None

    def __call__(self, id=None, **kwargs):
        modelKwargs = {}
        byName = False
        if isinstance(id, str):
            name = id
            id = None
            if self._model._canFetchByName:
                byName = True
                kwargs[self._model._nameAttr] = name
            else:
                raise InitializationError(
                    f"Cannot get {self._model.__name__!r} by name"
                )
        if id:
            modelKwargs["id"] = id
        elif self._model._canFetchByName:
            byName = True
            for key in self._model._apiNameMapping.keys():
                name = kwargs.get(key, None)
                if name:
                    modelKwargs[key] = name
                else:
                    raise InitializationError(
                        f"Missing required keyword argument, {key!r}, to fetch object by name"
                    )
        else:
            raise InitializationError("'id' is required")
        item = self._model(self._credmgr, **modelKwargs)
        item._fetch(byName)
        return item


class UserHelper(BaseHelper):
    _model = User

    def __call__(self, id=None, username=None):
        """Fetches a :class:`.User` instance by :attr:`id`` or :attr:`name`.

        :param Union[int,str] id: ID of the :class:`.User` to fetch. .. note:: If a
            ``str`` is passed it will be treated as the :attr:`username` attr.
        :param str username: Username of the :class:`.User` to fetch. .. note:: If both
            :attr:`id` and :attr:`username` are passed the :attr:`id` will take
            precedence. If :attr:`id` is a ``str`` it will be treated as an
            :attr:`username` and will also take precedence.

        :returns: An initialized :class:`.User` instance.

        """
        kwargs = {}
        byName = False
        if isinstance(id, str):
            byName = True
            username = id
            id = None
        if id:
            kwargs["id"] = id
        if username:
            kwargs["username"] = username
        if not (id or username):
            raise InitializationError("At least 'id' or 'username' is required")
        item = User(self._credmgr, **kwargs)
        item._fetch(byName)
        return item

    def create(
        self,
        username,
        password,
        defaultSettings=None,
        isAdmin=False,
        isActive=True,
        isRegularUser=True,
        isInternal=False,
        redditUsername=None,
    ) -> User:
        """Create a new user.

        **PERMISSIONS: At least ``isAdmin`` is required.**

        :param str username: Username for new user (Example: ``spaz``) (required)
        :param str password: Password for new user (Example: ``supersecurepassword``)
            (required)
        :param dict defaultSettings: Default values to use for new apps (Example:
            ``{"databaseFlavor": "postgres", "databaseHost": "localhost"}``)
        :param bool isAdmin: Is the user an admin? Allows the user to see all objects
            and create users (Default: ``False``)
        :param bool isActive: Is the user active? Allows the user to sign in (Default:
            ``True``)
        :param bool isRegularUser: (Internal use only)
        :param bool isInternal: (Internal use only)
        :param str redditUsername: The user's Reddit username.

        :returns: User

        """

        return self._model._create(
            self._credmgr,
            username=username,
            password=password,
            defaultSettings=defaultSettings,
            isAdmin=isAdmin,
            isActive=isActive,
            isRegularUser=isRegularUser,
            isInternal=isInternal,
            redditUsername=redditUsername,
        )


class BotHelper(BaseHelper):
    _model = Bot

    def create(
        self,
        name,
        redditApp=None,
        sentryToken=None,
        databaseCredential=None,
        owner=None,
    ) -> Bot:
        """Create a new Bot.

        Bots are used for grouping credentials into a single app.

        :param str name: Name of the Bot (required).
        :param Union[RedditApp,int] redditApp: Reddit App the bot will use.
        :param Union[SentryToken,int] sentryToken: Sentry Token the bot will use.
        :param Union[DatabaseCredential,int] databaseCredential: Database Credentials
            the bot will use.
        :param Union[User,int,str] owner: Owner of the bot. Requires Admin to create for
            other users.

        :returns: Bot

        """

        return self._model._create(
            self._credmgr,
            name=name,
            redditApp=redditApp,
            sentryToken=sentryToken,
            databaseCredential=databaseCredential,
            owner=owner,
        )


class RedditAppHelper(BaseHelper):
    _model = RedditApp

    def create(
        self,
        name,
        clientId,
        userAgent=None,
        appType="web",
        redirectUri=None,
        clientSecret=None,
        appDescription=None,
        enabled=True,
        owner=None,
    ) -> RedditApp:
        """Create a new RedditApp.

        Reddit Apps are used for interacting with reddit.

        :param str name: Name of the RedditApp (required).
        :param str clientId: Client ID of the Reddit App (required).
        :param str userAgent: User agent used for requests to Reddit's API (required,
            defaults to user set default, then to 'python:{name} by /u/{redditUsername}'
            if currentUser.redditUsername is set or 'python:{name}' if it is not set).
        :param str appType: Type of the app. One of `web`, `installed`, or `script`
            (required, default: 'web').
        :param str redirectUri: Redirect URI for Oauth2 flow. (required, defaults to
            user set default then to
            `https://credmgr.jesassn.org/oauth2/reddit_callback` if neither are set).
        :param str clientSecret: Client secret of the Reddit App.
        :param str appDescription: Description of the Reddit App.
        :param bool enabled: Allows the app to be used.
        :param Union[User,int,str] owner: Owner of the Reddit App. Requires Admin to
            create for other users.

        :returns: RedditApp

        """
        if not userAgent:
            redditUsername = self._credmgr.currentUser.redditUsername
            redditUsernameStr = ""
            if redditUsername:
                redditUsernameStr = f" by /u/{redditUsername}"
            userAgent = self._credmgr.getUserDefault(
                "user_agent", f"python:{name}{redditUsernameStr}"
            )
        redirectUri = self._credmgr.getUserDefault(
            "redirect_uri",
            redirectUri or "https://credmgr.jesassn.org/oauth2/reddit_callback",
        )
        return self._model._create(
            self._credmgr,
            name=name,
            clientId=clientId,
            userAgent=userAgent,
            appType=appType,
            redirectUri=redirectUri,
            clientSecret=clientSecret,
            appDescription=appDescription,
            enabled=enabled,
            owner=owner,
        )


class UserVerificationHelper(BaseHelper):
    _model = UserVerification

    def create(
        self, userId, redditApp, redditor=None, extraData=None, owner=None
    ) -> UserVerification:
        """Create a new User Verification.

        User Verifications for verifying a redditor with a User ID.

        :param str userId: User ID to associate Redditor with (required).
        :param Union[RedditApp,int,str] redditApp: Reddit app the User Verification is
            for (required).
        :param str redditor: Redditor the User Verification is for.
        :param dict extraData: Extra JSON data to include with verification.
        :param int owner: Owner of the verification. Requires Admin to create for other
            users.

        :returns: UserVerification

        """
        return self._model._create(
            self._credmgr,
            userId=userId,
            redditApp=redditApp,
            redditor=redditor,
            extraData=extraData,
            owner=owner,
        )


class SentryTokenHelper(BaseHelper):
    _model = SentryToken

    def create(self, name, dsn, owner=None) -> SentryToken:
        """Create a new Sentry Token

        Sentry Tokens are used for logging and error reporting in applications

        :param str name: Name of the Sentry Token (required).
        :param str dsn: DSN of the Sentry Token (required).
        :param Union[User,int,str] owner: Owner of the verification. Requires Admin to
            create for other users.

        :returns: SentryToken

        """
        return self._model._create(self._credmgr, name=name, dsn=dsn, owner=owner)


class DatabaseCredentialHelper(BaseHelper):
    _model = DatabaseCredential

    def create(
        self,
        name,
        databaseFlavor="postgres",
        database="postgres",
        databaseHost="localhost",
        databasePort=5432,
        databaseUsername="postgres",
        databasePassword=None,
        useSsh=False,
        sshHost=None,
        sshPort=None,
        sshUsername=None,
        sshPassword=None,
        useSshKey=False,
        privateKey=None,
        privateKeyPassphrase=None,
        enabled=True,
        owner=None,
    ) -> DatabaseCredential:
        """Create a new Database Credential

        Database Credentials are used for..ya know..databases

        :param str name: Name of the Database Credential (required)
        :param str databaseFlavor: Type of database, (default: ``postgres``)
        :param str database: Working database to use, (default: ``postgres``)
        :param str databaseHost: Database server address, (default: ``localhost``)
        :param int databasePort: Port the database server listens on, (default:
            ``5432``)
        :param str databaseUsername: Username to use to connect to the database
        :param str databasePassword: Password to use to connect to the database
        :param bool useSSH: Determines if the database will be connected to through a
            tunnel
        :param str sshHost: The address of the server that the SSH tunnel will connect
            to
        :param str sshPort: The port the SSH tunnel will use
        :param str sshUsername: Username for the SSH tunnel
        :param str sshPassword: Password for the SSH tunnel
        :param bool useSSHKey: Allows the credentials to be used
        :param str privateKey: SSH private key. Note: No validation will be performed.
        :param str privateKeyPassphrase: Passphrase for the SSH key
        :param bool enabled: Allows the credentials to be used
        :param Union[User,int,str] owner: Owner of the app. Requires Admin to create for
            other users.

        :returns: DatabaseCredential

        """
        return self._model._create(
            self._credmgr,
            name=name,
            databaseFlavor=databaseFlavor,
            database=database,
            databaseHost=databaseHost,
            databasePort=databasePort,
            databaseUsername=databaseUsername,
            databasePassword=databasePassword,
            useSsh=useSsh,
            sshHost=sshHost,
            sshPort=sshPort,
            sshUsername=sshUsername,
            sshPassword=sshPassword,
            useSshKey=useSshKey,
            privateKey=privateKey,
            privateKeyPassphrase=privateKeyPassphrase,
            enabled=enabled,
            owner=owner,
        )


class RefreshTokenHelper(BaseHelper):
    _model = RefreshToken

    def __call__(self, id=None, redditor=None, redditAppId=None):
        kwargs = {}
        if isinstance(id, str):
            if redditor:
                redditAppId = redditor
            redditor = id
            id = None
        if id:
            kwargs["id"] = id
        if redditor:
            kwargs["redditor"] = redditor
        if redditAppId:
            kwargs["redditAppId"] = redditAppId
        return super().__call__(**kwargs)
