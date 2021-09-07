import asyncio
import random
from abc import ABCMeta, abstractmethod
from scan import logger
from scan.config import Config
from scan.util import get_local_ip, get_local_name


class Spider(object):
    __metaclass__ = ABCMeta

    def __init__(self, spider_name, cfg_path):
        self.spider_name = spider_name
        self.spider_id = self.spider_id()
        self.config = Config(cfg_path)
        self.status = 1
        self.rabbitmq = None
        self.mongo_db = None
        self.redis_conn = None
        self.oss_conn = None

    def spider_id(self):
        local_ip = get_local_ip()
        container_id = get_local_name()[:12]
        spider_id = local_ip + '_' + container_id + '_' + self.spider_name
        with open('spider_id', 'w') as f:
            f.write(spider_id)
            f.close()
        return spider_id

    @staticmethod
    def get_proxy():
        proxy_list = ['http://127.0.0.1:1087']
        proxy = random.choice(proxy_list)
        return proxy

    @abstractmethod
    async def process(self, task_info):
        pass

    async def site(self):
        """
        1. 可以对配置文件进行修改
        eg：
            self.config.config.set('client', 'task_num', 1)
        :return:
        2. 可以设置新的成员变量
        eg:
            self.mq2 = ''
        """

    @abstractmethod
    async def init(self):
        """
        初始化数据处理连接
        eg:
            mq_config = self.config.rabbitmq()
            self.rabbitmq = RabbitMQ(host=mq_config.get('host'), port=mq_config.get('port'), user=mq_config.get('user'),
                           password=mq_config.get('password'))
            await self.rabbitmq.init()
        :return:
        """

    async def task(self):
        task_queue = self.config.rabbitmq.get('task_queue')
        if not self.rabbitmq:
            await logger.error('The task queue connection is not initialized')
            return
        while self.status:
            try:
                task_info = await self.rabbitmq.consume(task_queue)
                await self.process(task_info)
            except Exception as e:
                await logger.error(e)

    async def run(self):
        await self.site()
        await self.init()
        task_num = int(self.config.client.get('task_num'))
        task_list = []
        for _ in range(task_num):
            t = asyncio.create_task(self.task())
            task_list.append(t)
        await asyncio.gather(*task_list)

