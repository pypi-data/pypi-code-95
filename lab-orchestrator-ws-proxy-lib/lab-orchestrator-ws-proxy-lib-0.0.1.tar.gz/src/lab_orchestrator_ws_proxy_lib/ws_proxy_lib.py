import ssl
import threading
import asyncio
import websockets
import logging

from lab_orchestrator_lib_auth.auth import verify_auth_token


class WebsocketProxy:
    def __init__(self, remote_url, api_path, local_dev_mode, secret_key):
        self.remote_url = remote_url
        self.api_path = api_path
        self.thread = None
        self.local_dev_mode = local_dev_mode
        self.secret_key = secret_key

    def run(self, host, port):
        start_server = websockets.serve(self.proxy, host, port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def run_in_thread(self, host, port):
        start_server = websockets.serve(self.proxy, host, port)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(start_server)
        self.thread = threading.Thread(target=self.loop.run_forever)
        self.thread.start()

    def stop_thread(self):
        if self.thread is not None:
            self.loop.call_soon_threadsafe(self.loop.stop)
            logging.info("Stopped loop")
            self.thread.join()
            logging.info("Stopped thread")

    async def proxy(self, websocket, path):
        """Called whenever a new connection is made to the server.
        """
        # one token can include access to multiple vmi names, but is only valid for one namespace
        # split path to get vmi name and token
        splitted = path.split("/")
        if len(splitted) != 3:
            logging.warning("Invalid URL")
            await websocket.close(reason="invalid url")
            return
        token = splitted[1]
        vmi_name = splitted[2]

        # check if user has permissions to access this vmi
        jwt_token = verify_auth_token(token, vmi_name, secret_key=self.secret_key)
        if jwt_token is None:
            logging.warning("Invalid token")
            await websocket.close(reason="invalid token")
            return
        namespace_name = jwt_token.namespace_name

        # build websocket url and connect to
        url = self.remote_url + self.api_path.format(namespace=namespace_name, vmi_name=vmi_name)
        if not self.local_dev_mode:
            # adding selfsigned cert
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_verify_locations('/var/run/secrets/kubernetes.io/serviceaccount/ca.crt')
            # adding bearer authorization
            with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as reader:
                service_account_token = reader.read()
                header = {"Authorization": f"Bearer {service_account_token}"}
            async with websockets.connect(url, ssl=ssl_context, extra_headers=header) as ws:
                taskA = asyncio.create_task(WebsocketProxy.clientToServer(ws, websocket))
                taskB = asyncio.create_task(WebsocketProxy.serverToClient(ws, websocket))
                await taskA
                await taskB
        else:
            async with websockets.connect(url) as ws:
                taskA = asyncio.create_task(WebsocketProxy.clientToServer(ws, websocket))
                taskB = asyncio.create_task(WebsocketProxy.serverToClient(ws, websocket))
                await taskA
                await taskB

    @staticmethod
    async def clientToServer(ws, websocket):
        async for message in ws:
            await websocket.send(message)

    @staticmethod
    async def serverToClient(ws, websocket):
        async for message in websocket:
            await ws.send(message)
