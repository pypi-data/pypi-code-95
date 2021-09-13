import os


class QueueConfiguration:
    def __init__(self, username="",
                 password="",
                 host="",
                 port="",
                 model_exchange="",
                 output_exchange="",
                 model_routing_key="",
                 output_routing_key="",
                 queue="",
                 prefetch_count=None,
                 connection_retry_limit=None,
                 connection_retry_wait=None):
        self.username = username if username != "" else os.getenv("RABBITMQ_USERNAME", "admin")
        self.password = password if password != "" else os.getenv("RABBITMQ_PASSWORD", "admin")
        self.host = host if host != "" else os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port if port != "" else os.getenv("RABBITMQ_PORT", 5672)
        self.model_exchange = model_exchange if model_exchange != "" else os.getenv("RABBITMQ_MODEL_EXCHANGE", "model-exchange")
        self.output_exchange = output_exchange if output_exchange != "" else os.getenv("RABBITMQ_OUTPUT_EXCHANGE", "output-exchange")
        self.model_routing_key = model_routing_key if model_routing_key != "" else os.getenv("RABBITMQ_MODEL_ROUTING_KEY", "")
        self.output_routing_key = output_routing_key if output_routing_key != "" else os.getenv("RABBITMQ_OUTPUT_ROUTING_KEY", "input")
        self.prefetch_count = prefetch_count if prefetch_count is not None else int(os.getenv("RABBITMQ_PREFETCH_COUNT", 0))
        self.connection_retry_limit = connection_retry_limit if connection_retry_limit is not None else int(os.getenv("RABBITMQ_CONNECTION_RETRY_LIMIT", 5))
        self.connection_retry_wait = connection_retry_wait if connection_retry_wait is not None else int(os.getenv("RABBITMQ_CONNECTION_RETRY_WAIT", 30))
        self.queue = queue
