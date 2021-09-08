import json
import aio_pika
import asyncio
from aio_pika.pool import Pool
from scan.common import logger
from json import JSONDecodeError


class RabbitMQ:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host') or 'localhost'
        self.port = kwargs.get('port') or 5672
        self.user = kwargs.get('user') or 'root'
        self.password = kwargs.get('password') or 'root'
        self.virtualhost = kwargs.get('virtualhost') or '/'
        self.channel_pool = None
        self.loop = None
        self.max_pool_size = kwargs.get('max_pool_size') or 20

    async def init(self):
        await self.get_channel_pool()

    async def get_channel_pool(self):
        if self.loop or self.channel_pool:
            try:
                await self.channel_pool.close()
                self.loop.close()
            except Exception as e:
                await logger.error(f'close error: {e}')
        self.loop = asyncio.get_event_loop()

        async def get_connection():
            return await aio_pika.connect_robust(host=self.host, port=int(self.port), login=self.user,
                                                 password=self.password, virtualhost=self.virtualhost)
        connection_pool = Pool(get_connection, max_size=int(self.max_pool_size), loop=self.loop)

        async def get_channel() -> aio_pika.Channel:
            async with connection_pool.acquire() as connection:
                return await connection.channel()

        self.channel_pool = Pool(get_channel, max_size=20, loop=self.loop)

    async def consume(self, queue_name):
        """
        :param queue_name: 队列名
        :return:
        """
        async with self.channel_pool.acquire() as channel:
            for _ in range(3):
                try:
                    await channel.set_qos(1)
                    queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False)
                    async with queue.iterator() as queue_iter:
                        async for message in queue_iter:
                            body = None
                            try:
                                body = message.body
                                data_dict = json.loads(body.decode())
                                await message.ack()
                                return data_dict
                            except JSONDecodeError as e:
                                await logger.error(f'JSONDecoder error: {e}  data:{body}')
                            except Exception as e:
                                await logger.error(f'consume msg error: {e}')
                                await message.ack()
                                await self.get_channel_pool()
                except Exception as e:
                    await logger.error(f'consume error: {e}')
                    await self.get_channel_pool()

    async def publish(self, data, routing_key):
        """
        :param data: 要发送的数据
        :param routing_key: 队列名
        :return:
        """
        async with self.channel_pool.acquire() as channel:
            data = json.dumps(data)
            for _ in range(3):
                try:
                    await channel.default_exchange.publish(aio_pika.Message(body=data.encode()), routing_key=routing_key)
                    return
                except Exception as e:
                    await logger.error(f'publish error: {e}')
                    await self.get_channel_pool()


__all__ = RabbitMQ








