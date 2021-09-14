class RabbitClientConfiguration:
    def __init__(self,
                 username,
                 password,
                 host,
                 port,
                 exchange,
                 routing_key,
                 queue,
                 prefetch_count=0,
                 retry_limit=5,
                 retry_wait=30):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.exchange = exchange
        self.routing_key = routing_key
        self.prefetch_count = prefetch_count
        self.connection_retry_limit = retry_limit
        self.connection_retry_wait = retry_wait
        self.queue = queue
