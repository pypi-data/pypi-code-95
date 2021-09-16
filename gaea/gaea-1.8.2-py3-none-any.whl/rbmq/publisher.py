import datetime
import json
import pika

from gaea.config import CONFIG
from gaea.log import logger

from .base import RBMQClient


class RBMQPublisher(RBMQClient):
    @staticmethod
    def _get_default_headers():
        return {
            "emitter": CONFIG.SERVICE_NAME,
            "created_at": datetime.datetime.utcnow().isoformat(),
        }

    def publish(self, routing_key, content, headers=None):
        if headers is None:
            headers = {}
        headers.update(self._get_default_headers())
        properties = pika.BasicProperties(headers=headers)
        body = json.dumps(content, default=str)

        try:
            with self.connection_manager as channel:
                channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=properties,
                )
        except:
            logger.exception(
                "Fail to publish message in rbmq",
                body=body,
                properties=properties,
                routing_key=routing_key,
            )
            raise
