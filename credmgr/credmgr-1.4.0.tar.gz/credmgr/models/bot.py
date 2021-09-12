from ..mixins import BaseApp
from .utils import resolveUser


class Bot(BaseApp):
    """A class for Bot

    To obtain an instance of this class execute:

    .. code-block:: python

        bot = credmgr.bot("botName")

    Bots is the intended way to use CredentialManager. Bots are for grouping credentials
    that would be used in a single app.

    The following is the intended usage:

    .. code-block:: python

        from credmgr import CredentialManager

        credentialManager = CredentialManager(apiToken="apiToken")
        bot = credmgr.bot("botName")

        reddit = bot.reddit("Lil_SpazJoekp")
        dbCreds = bot.databaseCredentials
        sentryDSN = bot.sentryToken

    """

    _attrTypes = {
        **BaseApp._attrTypes,
        "reddit_app": "RedditApp",
        "sentry_token": "SentryToken",
        "database_credential": "DatabaseCredential",
    }
    _editableAttrs = BaseApp._editableAttrs + [
        "redditAppId",
        "sentryTokenId",
        "databaseCredentialId",
    ]
    _path = "/bots"
    _credmgrCallable = "bot"
    _canFetchByName = True

    def __init__(self, credmgr, **kwargs):
        """Initialize a Bot instance.

        Bots are used for grouping credentials into a single app

        :param credmgr: An instance of :class:`.CredentialManager`.
        :param id: ID of this Bot.
        :param name: Name of this Bot.
        :param ownerId: ID of the `.User` that owns this Bot.
        :param redditApp: `.RedditApp` that will be used with this Bot.
        :param sentryToken: `.SentryToken` that will be used with this Bot.
        :param databaseCredential: `.DatabaseCredential` that will be used with this
            Bot.

        """
        super().__init__(credmgr, **kwargs)

    @staticmethod
    @resolveUser()
    def _create(_credmgr, name, redditApp, sentryToken, databaseCredential, owner=None):
        """Create a new Bot

        Bots are used for grouping credentials into a single app

        :param str name: Name of the Bot (required)
        :param Union[RedditApp,int] redditApp: Reddit App the bot will use
        :param Union[SentryToken,int] sentryToken: Sentry Token the bot will use
        :param Union[DatabaseCredential,int] databaseCredential: Database Credentials
            the bot will use
        :param Union[User,int,str] owner: Owner of the bot. Requires Admin to create for
            other users.

        :returns: Bot

        """

        from . import DatabaseCredential, RedditApp, SentryToken

        additionalParams = {}
        if isinstance(redditApp, RedditApp):
            redditApp = redditApp.id
        if redditApp:
            additionalParams["reddit_app_id"] = redditApp
        if isinstance(sentryToken, SentryToken):
            sentryToken = sentryToken.id
        if sentryToken:
            additionalParams["sentry_token_id"] = sentryToken
        if isinstance(databaseCredential, DatabaseCredential):
            databaseCredential = databaseCredential.id
        if databaseCredential:
            additionalParams["database_credential_id"] = databaseCredential
        if owner:
            additionalParams["owner_id"] = owner
        return _credmgr.post("/bots", data={"app_name": name, **additionalParams})

    def edit(self, **kwargs):
        """:param name: Changes the name of the :class:`.Bot`
        :param Union[RedditApp,int] redditApp: Changes the :class:`.RedditApp` the Bot
            will use
        :param Union[SentryToken,int] sentryToken: Changes the :class:`.SentryToken` the
            Bot will use
        :param Union[DatabaseCredential,int] databaseCredential: Changes the
            :class:`.DatabaseCredential` the Bot will use

        .. note::

            Parameters, ``redditApp``, ``sentryToken``, and ``databaseCredential`` can
            accept the initialized object or its :attr:`id`. Passing a ``str`` to it
            will not work. The intended was to create bots in with the web interface.

        :returns: The modified :class:`.Bot`

        """
        from credmgr.models import DatabaseCredential, RedditApp, SentryToken

        iterKwargs = dict(kwargs.items())
        for key, value in iterKwargs.items():
            if key in ["redditApp", "sentryToken", "databaseCredential"]:
                if isinstance(
                    kwargs[key], (RedditApp, SentryToken, DatabaseCredential)
                ):
                    newKey = f"{key}Id"
                    kwargs[newKey] = kwargs.pop(key).id
                else:
                    newKey = f"{key}Id"
                    kwargs[newKey] = kwargs.pop(key)
        super(Bot, self).edit(**kwargs)
