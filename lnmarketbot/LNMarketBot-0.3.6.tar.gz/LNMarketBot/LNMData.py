import aiohttp
import asyncio
from .Data import Data


class LNMData(Data):

    def __init__(self, **params):
        self.session = aiohttp.ClientSession()
        self.wsurl = 'wss://api.lnmarkets.com/realtime'
        super().__init__(**params)

    async def dataGenerator(self):
        async with self.session.ws_connect(self.wsurl) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        print(msg.data)
                        await ws.send_str(msg.data + '/answer')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
