from channels.worker import Worker as CWorker

from iacs.log import IacsLogger


# noinspection PyAbstractClass
class Worker(CWorker, metaclass=IacsLogger):

    async def listener(self, channel):
        while True:
            try:
                message = await self.channel_layer.receive(channel)
                if message.get('type', None):
                    scope = {"type": "channel", "channel": channel}
                    instance_queue = self.get_or_create_application_instance(channel, scope)
                    await instance_queue.put(message)
                else:
                    self.logger.warning(f'描述: 已忽略错误的消息; 消息内容: {message}')
            except Exception as e:
                self.error.exception(e)
                self.logger.error(f'描述: 出现异常，获取消息失败')
