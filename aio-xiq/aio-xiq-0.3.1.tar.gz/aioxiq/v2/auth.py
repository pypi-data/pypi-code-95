from typing import Optional, Set, Sequence

from .client import XiqBaseClient


class XiqAuth(XiqBaseClient):
    def __init__(self, *vargs, **kwargs):
        super(XiqAuth, self).__init__(*vargs, **kwargs)

        # The list of known permissions, as retrieved from calling
        # `fetch_permissions`
        self.auth_known_permissions: Optional[Set] = None

        # The list of read-only permissions; a subset of the
        # `auth_known_permissions` that end in ":r", ":list", or ":view"
        self.auth_known_permissions_read_only: Optional[Set] = None

    async def auth_new_token(
        self,
        permissions: Sequence[str],
        description: str,
        expiry_epoch: Optional[int] = None,
    ) -> dict:
        """
        Create a new API token.

        Parameters
        ----------
        permissions: Sequence[str]
            List of permission string values, for example "device:r". All
            permissions available can be obtained using `fetch_permissions`.

        description: str
            The description for this token.  Not currently used since API does
            not support token management (read/delete).  If not provided will
            default to empty-string.

        expiry_epoch: epoch
            Time in Unix epoch.  If null (default) then the token does no
            expire.

        Returns
        -------
        New token value.

        Raises
        ------
        ValueError if any permission is not valid.  The ValueError.args[1]
        will be the list of bad permission values.
        """

        # obtain the list of available permissions that the Caller can use;
        # which is dependent on the token they are using.  Only allow the
        # Caller to create a token with permissions for which they have access.

        if not self.auth_known_permissions:
            await self.fetch_permissions()

        # ensure the requested permissions are allowed.

        not_perms = [p for p in permissions if p not in self.auth_known_permissions]
        if not_perms:
            raise ValueError(f"Invalid permissions requested: {not_perms}", not_perms)

        res = await self.post(
            "/auth/apitoken",
            json=dict(
                description=description or "",
                expire_time=expiry_epoch,
                permissions=list(permissions),
            ),
        )

        res.raise_for_status()
        return res.json()

    async def fetch_token_info(self) -> dict:
        """
        Fetches information about the current token, as described in the Swagger API
        definition found here:
        https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config#/Authorization/getCurrentApiTokenInfo

        Typical interest in the dictionary fields:
            - `expires_in` identfies the TTL in seconds
            - `scopes` is a list of permissions

        Returns
        -------
        dict of data, per the API schema.
        """
        res = await self.get("/auth/apitoken/info")
        res.raise_for_status()
        return res.json()

    async def fetch_permissions(self) -> list:
        """
        This coroutine will fetch the permission values for the _current_ token
        in use. If you want to find the list of all permissions you will need
        to be using a token generated for an administrator (or be logged in as
        an administrator).

        Returns
        -------
        list[str]
        """
        res = await self.get("/auth/permissions")
        res.raise_for_status()
        body = res.json()
        self.auth_known_permissions = {p["name"] for p in body}
        self.auth_known_permissions_read_only = {
            p
            for p in self.auth_known_permissions
            if p.endswith((":r", ":list", ":view"))
        }
        return body
