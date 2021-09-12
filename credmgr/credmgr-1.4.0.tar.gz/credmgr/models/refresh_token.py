from credmgr.mixins import BaseModel, DeletableMixin, EditableMixin, OwnerMixin
from credmgr.mixins.redditReddit import RedditAppMixin


class RefreshToken(
    BaseModel, DeletableMixin, OwnerMixin, EditableMixin, RedditAppMixin
):
    _attrTypes = {
        **BaseModel._attrTypes,
        "reddit_app_id": "int",
        "redditor": "str",
        "refresh_token": "str",
        "owner_id": "int",
        "scopes": "str",
        "issued_at": "datetime",
        "revoked": "bool",
        "revoked_at": "datetime",
    }
    _editableAttrs = ["refreshToken"]
    _path = "/refresh_tokens"
    _credmgrCallable = "refreshToken"
    _nameMapping = {"redditor": "redditor"}
    _apiNameMapping = {"redditor": "redditor", "redditAppId": "reddit_app_id"}
    _getByNamePath = "by_redditor"
    _canFetchByName = True
    _nameAttr = "redditor"

    def __init__(self, credmgr, **kwargs):
        """Initialize a Refresh Token instance.

        Refresh Tokens are for authenticating with Reddit as a Reddit that has
        authorized a `.RedditApp` to access their Reddit account.

        :param credmgr: An instance of :class:`.CredentialManager`.
        :param int id: ID of this Refresh Token.
        :param str redditor: Redditor this Refresh Token is for.
        :param str redditAppId: ID of the `.RedditApp` this Refresh Token is for.
        :param str refreshToken: The Refresh Token to pass to a Reddit instance.
        :param list[str] scopes: The OAuth2 scopes this Refresh Token grants access to.
        :param int ownerId: ID of the `.User` that owns this Refresh Token.
        :param datetime.datetime issuedAt: Date and time this Refresh Token was issued.
        :param bool revoked: Indicates if this Refresh Token was revoked or superseded
            by another Refresh Token.
        :param datetime.datetime revokedAt: Date and time this Refresh Token was revoked
            or superseded.

        """
        super().__init__(credmgr, **kwargs)
