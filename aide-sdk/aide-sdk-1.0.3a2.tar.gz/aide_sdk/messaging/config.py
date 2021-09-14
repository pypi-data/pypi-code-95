import os
from distutils.util import strtobool

from aide.messaging.queue_config import RabbitClientConfiguration


class QueueConfiguration:
    def __init__(self, username="",
                 password="",
                 host="",
                 port="",
                 model_exchange="",
                 output_exchange="",
                 model_routing_key="",
                 output_routing_key="",
                 input_queue="",
                 outout_queue="",
                 connection_retry_limit=None,
                 connection_retry_wait=None):
        username = username if username != "" else os.getenv("RABBITMQ_USERNAME", "admin")
        password = password if password != "" else os.getenv("RABBITMQ_PASSWORD", "admin")
        host = host if host != "" else os.getenv("RABBITMQ_HOST", "localhost")
        port = port if port != "" else os.getenv("RABBITMQ_PORT", 5672)
        model_exchange = model_exchange if model_exchange != "" else os.getenv("RABBITMQ_MODEL_EXCHANGE",
                                                                               "model-exchange")
        output_exchange = output_exchange if output_exchange != "" else os.getenv("RABBITMQ_OUTPUT_EXCHANGE",
                                                                                  "output-exchange")
        model_routing_key = model_routing_key if model_routing_key != "" else os.getenv("RABBITMQ_MODEL_ROUTING_KEY",
                                                                                        "")
        output_routing_key = output_routing_key if output_routing_key != "" else os.getenv(
            "RABBITMQ_OUTPUT_ROUTING_KEY", "input")
        connection_retry_limit = connection_retry_limit if connection_retry_limit is not None else int(
            os.getenv("RABBITMQ_CONNECTION_RETRY_LIMIT", 5))
        connection_retry_wait = connection_retry_wait if connection_retry_wait is not None else int(
            os.getenv("RABBITMQ_CONNECTION_RETRY_WAIT", 30))

        self.consumer_config = RabbitClientConfiguration(username=username,
                                                         password=password,
                                                         host=host,
                                                         port=port,
                                                         exchange=model_exchange,
                                                         routing_key=model_routing_key,
                                                         retry_wait=connection_retry_wait,
                                                         retry_limit=connection_retry_limit,
                                                         queue=input_queue)

        self.publisher_config = RabbitClientConfiguration(username=username,
                                                          password=password,
                                                          host=host,
                                                          port=port,
                                                          exchange=output_exchange,
                                                          routing_key=output_routing_key,
                                                          retry_wait=connection_retry_wait,
                                                          retry_limit=connection_retry_limit,
                                                          queue=outout_queue)


class ElasticConfiguration:
    def __init__(self, username=None,
                 password=None,
                 host=None,
                 port=None,
                 verify_certs=None,
                 scheme=None):
        self.username = username or os.getenv("ELASTICSEARCH_USERNAME", "admin")
        self.password = password or os.getenv("ELASTICSEARCH_PASSWORD", "admin")
        self.host = host or os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
        self.port = port or int(os.getenv("ELASTICSEARCH_PORT", 0)) or 443
        self.verify_certs = verify_certs or bool(strtobool(os.environ.get("ELASTICSEARCH_VERIFY_CERTS", 'false')))
        self.scheme = scheme or os.environ.get("ELASTICSEARCH_SCHEME", "http")


class PacsConfiguration:
    def __init__(self, ae_title=None,
                 host=None,
                 port=None,
                 dimse_timeout=None):
        self.ae_title = ae_title or os.getenv("PACS_AE_TITLE", "ORTHANC")
        self.host = host or os.getenv("PACS_HOST", "localhost")
        self.port = port or int(os.getenv("PACS_PORT", 0)) or 4242
        self.dimse_timeout = dimse_timeout or int(os.getenv("PACS_DIMSE_TIMEOUT", 30))
