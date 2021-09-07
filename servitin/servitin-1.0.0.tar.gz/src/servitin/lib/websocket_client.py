import traceback
import asyncio
import json
import aiohttp
from async_timeout import timeout
from servitin.utils import serializable, mail_admins


class ConnectionLost(Exception):
    pass


class WebsocketClient:
    def __init__(self, loop, settings, log, connection_check_tries=3, connection_check_interval=60, on_connection_error=None):
        self.log = log
        self.loop = loop
        self.ws_url = settings['URL']
        self.ws_username = settings['USER']['username']
        self.ws_password = settings['USER']['password']
        self.ws_socket = None

        # connection checker vars
        self.connection_check_tries = connection_check_tries
        self.connection_check_interval = connection_check_interval
        self.connection_check_try = 0
        self.connection_error = None
        self.on_connection_error = on_connection_error

        self.connection_task = self.loop.create_task(self.connect())
        self.connection_checker = self.loop.create_task(self.connection_checker())
        self.write_queue = asyncio.Queue()
        self.writer_task = self.loop.create_task(self.write_worker())

    def close(self):
        self.connection_checker.cancel()
        self.writer_task.cancel()
        self.connection_task.cancel()
        if self.ws_socket:
            self.loop.run_until_complete(self.ws_socket.close())
            self.log.info(f'close: {self.ws_url}', name='websocket')

    async def connect(self):
        try:
            async with aiohttp.ClientSession(loop=self.loop, headers={'Origin': self.ws_url},
                                             auth=aiohttp.BasicAuth(self.ws_username, self.ws_password)) as session:
                async with session.ws_connect(self.ws_url, autoping=True) as self.ws_socket:
                    self.log.info(f'open: {self.ws_url}', name='websocket')

                    async for msg in self.ws_socket:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            pass
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

        except asyncio.CancelledError as e:
            pass
        except aiohttp.ClientConnectionError as e:
            self.log.error(e.__str__(), name='websocket')
            self.connection_error = e.__str__()
        except aiohttp.WSServerHandshakeError as e:
            self.log.error(e.__str__(), name='websocket')
            self.connection_error = e.__str__()
        except Exception as e:
            self.connection_error = e.__str__()
            tb = traceback.format_exc()
            self.log.critical(f"connection error: {e.__repr__()}, url: {self.ws_url}", tb=tb, name='websocket')
            await mail_admins(self.loop, f'WebsocketClient error', f'Error: {e.__repr__()}\n\n{tb}')

        await asyncio.sleep(3)
        return await self.connect()

    async def write_worker(self):
        """
        Task for write to websocket
        """

        try:
            while True:
                data = await self.write_queue.get()
                if self.ws_socket and not self.ws_socket.closed:
                    with timeout(10, loop=self.loop):
                        await self.ws_socket.send_str(json.dumps(serializable(data)))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            tb = traceback.format_exc()
            self.log.critical(f"send error: {e.__repr__()}, url: {self.ws_url}", tb=traceback.format_exc(), name='websocket')
            await mail_admins(self.loop, f'WebsocketClient error', f'Error: {e.__repr__()}\n\n{tb}')

    async def send(self, msg):
        await self.write_queue.put(msg)

    async def connection_checker(self):
        """
        Periodically checks websocket connection
        """
        try:
            while True:
                await asyncio.sleep(self.connection_check_interval)
                if not self.ws_socket or self.ws_socket.closed:
                    self.connection_check_try += 1
                else:
                    self.connection_check_try = 0
                    self.connection_error = None

                if self.connection_check_try == self.connection_check_tries:
                    self.connection_check_try = 0
                    error = f'connection problem after {self.connection_check_tries} checks with {self.connection_check_interval} sec. interval, ' \
                            f'last error: {self.connection_error}'
                    self.log.critical(error, name="websocket")

                    if self.on_connection_error:
                        await self.on_connection_error(error)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            tb = traceback.format_exc()
            self.log.critical(e.__repr__(), name="websocket", traceback=tb)
            await mail_admins(self.loop, f'Servitin WebsocketClient error', f'Error: {e.__repr__()}\n\n{tb}')
