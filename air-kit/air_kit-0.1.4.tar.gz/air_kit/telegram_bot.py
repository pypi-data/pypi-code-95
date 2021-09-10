from abc import ABC, abstractmethod
from queue import Queue

from aiohttp.web import Application, AppRunner, Request, Response, TCPSite, post
from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater


class Mode:
    WEBHOOK = "webhook"
    POOLING = "pooling"

class TelegramBot(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass


class PoolingTelegramBot(TelegramBot):
    def __init__(self, token: str):
        super().__init__()
        self.updater = Updater(token, use_context=True)

    async def start(self):
        self.updater.start_polling()

    async def stop(self):
        self.updater.stop()

    @property
    def dispatcher(self):
        return self.updater.dispatcher


class WebhookTelegramBot(TelegramBot):
    def __init__(self, host: str, port: int, fqdn: str, token: str):
        super().__init__()

        class Stub:
            def __init__(self):
                self.defaults = None

        bot = Bot(token)
        dispatcher = Dispatcher(Stub(), workers=0, update_queue=Queue())

        application = Application()
        application.add_routes(
            [
                post(
                    "/{token}",
                    self._index,
                ),
            ]
        )

        async def on_start(_):
            bot.setWebhook(f"https://{fqdn}/{token}")

        async def on_stop(_):
            bot.deleteWebhook()

        application.on_startup.append(on_start)
        application.on_shutdown.append(on_stop)

        self.host = host
        self.port = port

        self.bot = bot
        self.dispatcher = dispatcher

        self.application = application
        self.runner = None
        self.site = None

    async def start(self):
        # Create runner.
        self.runner = AppRunner(self.application)
        await self.runner.setup()

        # Create tcp site.
        self.site = TCPSite(self.runner, self.host, self.port)
        await self.site.start()

    async def stop(self):
        pass

    async def _index(self, request: Request) -> Response:
        self.dispatcher.process_update(
            Update.de_json(
                await request.json(),
                self.bot,
            ),
        )
        return Response()
