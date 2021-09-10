# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Dict
import asyncio
import os
from http import HTTPStatus

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from httpx import AsyncClient, Response
from tenacity import retry, wait_exponential

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["XiqBaseClient"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class XiqBaseClient(AsyncClient):
    """
    Base client class for Extreme Cloud IQ API access.  The following
    environment variables can be used:

       * XIQ_USER - login user name
       * XIQ_PASSWORD - login user password
       * XIQ_TOKEN - login token; no need for user/password

    If the Caller does not provide an API token, then the Caller must invoke
    the `login` coroutine to obtain an API token.
    """

    DEFAULT_URL = "https://api.extremecloudiq.com"
    DEFAULT_PAGE_SZ = 100
    DEFAULT_TIMEOUT = 10

    def __init__(
        self,
        *vargs,
        xiq_user: Optional[str] = None,
        xiq_password: Optional[str] = None,
        xiq_token: Optional[str] = None,
        **kwargs,
    ):
        kwargs.setdefault("base_url", self.DEFAULT_URL)
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)
        super(XiqBaseClient, self).__init__(*vargs, **kwargs)

        self.xiq_user = xiq_user or os.getenv("XIQ_USER")
        self.xiq_password = xiq_password or os.getenv("XIQ_PASSWORD")
        self.xiq_token = xiq_token or os.getenv("XIQ_TOKEN")
        if self.xiq_token:
            self.headers["Authorization"] = "Bearer " + self.xiq_token

    async def login(
        self, username: Optional[str] = None, password: Optional[str] = None
    ):
        """
        This coroutine is used to authenticate with the Extreme Cloud IQ system
        and obtain an API token for use.

        Parameters
        ----------
        username: str - login user name
        password: str - login user passowrd

        Raises
        ------
        HTTPException upon authentication error.
        """
        creds = {
            "username": username or self.xiq_user,
            "password": password or self.xiq_password,
        }
        res = await self.post("/login", json=creds)
        res.raise_for_status()
        self.xiq_token = res.json()["access_token"]
        self.headers["Authorization"] = "Bearer " + self.xiq_token

    async def paginate(
        self, url: str, page_sz: Optional[int] = None, **params
    ) -> List[Dict]:
        """
        Concurrently paginate GET on url for the given page_sz and optional
        parameters.  If page_sz is not provided then the DEFAULT_PAGE_SZ class
        attribute value is used.

        Parameters
        ----------
        url: str - The API URL endpoint
        page_sz: - Max number of result items per page

        Returns
        -------
        List of all API results from all pages
        """

        # always make a copy of the Caller provided parameters so we
        # do not trample any of their settings.

        _params = params.copy()

        # fetch the first page of data, which will also tell us the the total
        # number of pages we need to fetch.

        _params["limit"] = page_sz or self.DEFAULT_PAGE_SZ
        res = await self.get(url, params=_params)
        res.raise_for_status()
        body = res.json()
        records = body["data"]
        total_pages = body["total_pages"]

        # fetch the remaining pages concurrently; remember that the `range`
        # function does not include the ending value ... so +1 the total_pages.

        tasks = list()
        for page in range(2, total_pages + 1):
            _params["page"] = page
            tasks.append(self.get(url, params=_params.copy()))

        for next_r in asyncio.as_completed(tasks):
            res = await next_r
            body = res.json()
            records.extend(body["data"])

        # return the full list of all records.

        return records

    # -----------------------------------------------------------------------------
    #                            AsyncClient Overrides
    # -----------------------------------------------------------------------------

    async def request(self, *vargs, **kwargs) -> Response:
        @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
        async def _do_rqst():
            res = await super(XiqBaseClient, self).request(*vargs, **kwargs)

            if res.status_code == HTTPStatus.BAD_REQUEST and "UNKNOWN" in res.text:
                print("XIQ client bad request: retry")
                res.raise_for_status()

            # sometimes the XIQ system is unavailable; so retry before bailing
            # out completely.

            if res.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                print("XIQ service unavailable: retry")
                res.raise_for_status()

            return res

        return await _do_rqst()
