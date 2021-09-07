import boto3
import json
from abc import ABC, abstractclassmethod
from signal import signal, SIGINT, SIGTERM
from django.conf import settings


class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


class ExchangeBase(ABC):

    @abstractclassmethod
    def get_exchange_methods():
        pass


class ConsumerBase(ABC):

    @abstractclassmethod
    def __init__(self, exchanges):
        pass

    @abstractclassmethod
    def consume(cls):
        pass


class Sqs(ConsumerBase):

    def __init__(self, exchanges):
        self.exchanges = exchanges

    def consumer_fn():
        pass

    def consume(self):
        sqs_client_options = {
            'region_name': settings.AWS_REGION_NAME,
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
            'endpoint_url': settings.AWS_ENDPOINT_URL
        }
        sqs = boto3.resource('sqs', **sqs_client_options)
        queue = sqs.get_queue_by_name(QueueName=settings.SERVICE_QUEUE)
        signal_handler = SignalHandler()
        while not signal_handler.received_signal:
            for message in queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1):
                body = json.loads(message.body)
                exchange_fn = self.exchanges[body.get('Subject')]
                exchange_fn(body.get('Message'))
                message.delete()


class ConsumerFactory:

    @staticmethod
    def get_consumer(consumer_name, exchanges):
        CONSUMERS = {
            'SQS': Sqs
        }
        Consumer = CONSUMERS[consumer_name]
        return Consumer(exchanges=exchanges)
