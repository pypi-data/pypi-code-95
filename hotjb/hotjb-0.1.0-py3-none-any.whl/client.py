import aiohttp
import json
from urllib.parse import urljoin

class HotJBClient:
    '''
    '''

    def __init__(self, host='127.0.0.1', port=30000):
        '''
        '''

        self.host = host
        self.port = port

    async def request(self, path, data):
        '''
        '''

        url = urljoin(f'http://{self.host}:{self.port}', path)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = {
                    'status': response.status,
                    'headers': response.headers,
                    'content': await response.json()
                }
                return result

    async def tokenize(self, text):
        '''
        '''

        return await self.request('/tokenize', {
            'text': text,
        })
        
        

    