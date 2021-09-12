import json

from ..mixins import BaseModel, DeletableMixin, EditableMixin, OwnerMixin
from ..mixins.redditReddit import RedditAppMixin
from . import RedditApp
from .utils import resolveModelFromInput, resolveUser


class UserVerification(
    BaseModel, DeletableMixin, EditableMixin, OwnerMixin, RedditAppMixin
):
    _attrTypes = {
        **BaseModel._attrTypes,
        "id": "int",
        "user_id": "str",
        "redditor": "str",
        "reddit_app_id": "int",
        "extra_data": "dict",
        "owner_id": "int",
    }

    _editableAttrs = ["userId", "redditor", "redditAppId", "extraData"]
    _path = "/user_verifications"
    _credmgrCallable = "userVerification"
    _nameAttr = "userId"
    _nameMapping = {"user_id": "userId"}
    _canFetchByName = True
    _getByNamePath = "get_redditor"
    _apiNameMapping = {"userId": "user_id"}

    def __init__(self, credmgr, **kwargs):
        """Initialize an User Verification instance.

        User Verifications for associating an unique ID with a Redditor

        :param credmgr: An instance of :class:`.CredentialManager`.
        :param id: ID of this User Verification.
        :param userId: An unique ID to associate with a Redditor.
        :param redditor: Redditor username to associate with an unique ID.
        :param redditAppId: ID of the RedditApp the Refresh Token is for.
        :param extraData: Extra data to be associated with this User Verification
        :param ownerId: ID of the `.User` that owns this User Verification

        """
        super().__init__(credmgr, **kwargs)

    @staticmethod
    @resolveUser()
    def _create(_credmgr, userId, redditApp, redditor=None, extraData=None, owner=None):
        """Create a new User Verification

        User Verifications for associating an unique ID with a Redditor

        :param str userId: An unique ID to associate with a Redditor (required)
        :param Union[RedditApp,int,str] redditApp: Reddit app the User Verification is
            for (required)
        :param str redditor: Redditor the User Verification is for. This is not usually
            set manually.
        :param dict extraData: Extra JSON data to include with verification
        :param Union[User,int,str] owner: Owner of the verification. Requires Admin to
            create for other users.

        :returns: UserVerification

        """

        data = {
            "user_id": userId,
            "reddit_app_id": resolveModelFromInput(_credmgr, RedditApp, redditApp),
        }
        if redditor:
            data["redditor"] = redditor
        if extraData:
            data["extra_data"] = json.dumps(extraData)
        if owner:
            data["owner_id"] = owner
        return _credmgr.post("/user_verifications", data=data)
