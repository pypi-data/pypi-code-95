import logging

import httpx

GET = "get"
POST = "post"


class Connection:

    def __init__(self, websession: httpx.AsyncClient, host):
        self._host = host
        self._series = []
        self._websession = websession

    async def get(self, url):
        return await self.__open(url)

    async def __open(
        self, url, method=GET, headers=None,
        params=None, baseurl="", decode_json=True,
        auth=None, username=None, password=None
    ):

        logging.debug("URL: %s", url)
        try:
            resp = await getattr(self._websession, method)(
                url, headers=headers, params=params,auth=auth
            )
            
            #if decode_json:
            #    return (await resp.json())
            return resp
        except httpx.HTTPError as err:
            logging.error("Err: %s", err)
