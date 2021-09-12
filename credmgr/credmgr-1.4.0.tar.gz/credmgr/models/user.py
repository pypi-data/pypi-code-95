import json

from ..exceptions import InitializationError
from ..mixins import BaseModel, DeletableMixin, EditableMixin


class User(BaseModel, DeletableMixin, EditableMixin):
    _attrTypes = {
        **BaseModel._attrTypes,
        "id": "int",
        "username": "str",
        "is_active": "bool",
        "is_regular_user": "bool",
        "is_admin": "bool",
        "default_settings": "dict(str, str)",
        "reddit_username": "str",
        "created": "datetime",
        "updated": "datetime",
        "reddit_apps": "list[RedditApp]",
        "sentry_tokens": "list[SentryToken]",
        "database_credentials": "list[DatabaseCredential]",
    }
    _editableAttrs = [
        "username",
        "isActive",
        "isRegularUser",
        "isAdmin",
        "defaultSettings",
        "redditUsername",
    ]
    _path = "/users"
    _credmgrCallable = "user"
    _nameAttr = "username"
    _nameMapping = {"username": "username"}
    _canFetchByName = True
    _apiNameMapping = {_nameAttr: "username"}

    def __init__(self, credmgr, **kwargs):
        """Initialize an User instance

        Users are for logging into and accessing that user's credentials

        :param credmgr: An instance of :class:`.CredentialManager`.
        :param int id: ID of the User.
        :param username: Username of the User.
        :param bool isActive: Indicates if the User can log in and access
            CredentialManager.
        :param bool isRegularUser: Indicates if this is a regular user.
        :param bool isAdmin: Indicates if this User can create other users and their
            credentials.
        :param defaultSettings: Default settings used when creating new items without
            those settings explicitly set.
        :param str redditUsername: This User's Reddit username. Used for
            :class:`.RedditApp`'s userAgent.
        :param datetime.datetime created: Date and time this User was created.
        :param datetime.datetime updated: Date and time this User was last updated.
        :param list[RedditApp] redditApps: A list of Reddit Apps this User owns.
        :param list[SentryToken] sentryTokens: A list of Sentry Tokens this User owns.
        :param list[DatabaseCredential] databaseCredentials: A list of Database
            Credentials this User owns.

        """
        super().__init__(credmgr, **kwargs)
        self._apps = {}
        if "redditApps" in kwargs:
            self._apps["redditApps"] = kwargs["redditApps"]
        if "sentryTokens" in kwargs:
            self._apps["sentryTokens"] = kwargs["sentryTokens"]
        if "databaseCredentials" in kwargs:
            self._apps["databaseCredentials"] = kwargs["databaseCredentials"]

    @staticmethod
    def _create(
        _credmgr,
        username,
        password,
        defaultSettings=None,
        redditUsername=None,
        isAdmin=False,
        isActive=True,
        isRegularUser=True,
        isInternal=False,
    ):
        """Create a new User

        **PERMISSIONS: Admin role is required.**

        :param str username: Username for new user (Example: ``spaz``) (required)
        :param str password: Password for new user (Example: ``supersecurepassword``)
            (required)
        :param dict defaultSettings: Default values to use for new apps (Example:
            ``{"databaseFlavor": "postgres", "databaseHost": "localhost"}``)
        :param str redditUsername: User's Reddit username (Example: ``Lil_SpazJoekp``)
        :param bool isAdmin: Is the user an admin? Allows the user to see all objects
            and create users (Default: ``False``)
        :param bool isActive: Is the user active? Allows the user to sign in (Default:
            ``True``)
        :param bool isRegularUser: (Internal use only)
        :param bool isInternal: (Internal use only)

        :returns: User

        """
        additionalParams = {}
        if defaultSettings:
            additionalParams["default_settings"] = json.dumps(defaultSettings)
        if isAdmin:  # pragma: no cover
            additionalParams["is_admin"] = isAdmin
        if isActive:
            additionalParams["is_active"] = isActive
        if isRegularUser:
            additionalParams["is_regular_user"] = isRegularUser
        if isInternal:  # pragma: no cover
            additionalParams["is_internal"] = isInternal
        if redditUsername:
            additionalParams["reddit_username"] = redditUsername
        return _credmgr.post(
            "/users",
            data={"username": username, "password": password, **additionalParams},
        )

    def apps(self, only=None):
        """Returns apps that are owned by this user

        :param str only: Pass one of ``redditApps``, ``sentryTokens``,
            ``databaseCredentials`` to only get that type of apps

        :returns: Returns the user's apps.

        """
        appTypes = ["redditApps", "sentryTokens", "databaseCredentials"]
        if not self._apps:
            response = self._credmgr.get(f"/users/{self.id}/apps")
            self._apps = response._apps
            for app in appTypes:
                setattr(self, app, self._apps[app])
        if only:
            if only in appTypes:
                return self._apps[only]
            else:
                raise InitializationError(
                    f"App type: {only} is not valid. Only 'redditApps', 'sentryTokens', and 'databaseCredentials' are valid."
                )
        return self._apps
