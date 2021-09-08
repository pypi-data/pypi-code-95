import asyncio
import aiohttp
from exceptions import BadAuth
from bingresponse import BingResponse

class Search:
    """The searching part of asyncbing"""
    def __init__(self, auth: str=None):
        self.headers = {'Ocp-Apim-Subscription-Key': auth}
        self.bing = 'https://api.bing.microsoft.com/v7.0/search'
        self.session = asyncio.run(self.session_setup())
    
    async def session_setup(self) -> aiohttp.ClientSession:
        async with aiohttp.ClientSession() as session:
            return session
    
    async def fetch(self, *, search: str) -> BingResponse:
        """Searches with the bing api for the search string provided, with the global market set."""
        async with self.session.post(self.bing, headers=self.headers, params={'q': search}) as resp:
            if (await resp.json())['error']['code'] == '401':
                raise BadAuth('You passed an invalid authorization token.')
            return BingResponse((await resp.json()))
