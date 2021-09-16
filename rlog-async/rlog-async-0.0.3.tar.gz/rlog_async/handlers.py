# coding: utf-8
import logging
import redis
import threading
try:
    import queue as Queue
except ImportError:
    import Queue


from .formatters import JSONFormatter


class RedisHandler(logging.Handler):
    """
    Publish messages to redis channel.
    """

    def __init__(self, channel, redis_client=None,
                 formatter=JSONFormatter(),
                 level=logging.NOTSET, **redis_kwargs):
        """
        Create a new logger for the given channel and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.channel = channel
        self.redis_client = redis_client or redis.Redis(**redis_kwargs)
        self.formatter = formatter

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        try:
            self.redis_client.publish(self.channel, self.format(record))
        except redis.RedisError:
            pass


class RedisListHandler(logging.Handler):

    def __init__(self, key, max_messages=None, redis_client=None,
                 formatter=JSONFormatter(), ttl=None,
                 level=logging.NOTSET, **redis_kwargs):
        """
        Create a new logger for the given key and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.send_thread = threading.Thread(target=self.work)
        self.send_thread.setName('Redis logger handler %s' % key)
        self.key = key
        self.redis_client = redis_client or redis.Redis(**redis_kwargs)
        self.formatter = formatter
        self.max_messages = max_messages
        self.ttl = ttl
        self.msg_queue = Queue.Queue(maxsize=0 if max_messages is None else max_messages)
        self.send_thread.start()
        
    def work(self):
        """
        Publish record to redis logging list
        """
        while True:
            try:
                msg = self.msg_queue.get()
                if self.max_messages:
                    p = self.redis_client.pipeline()
                    p.rpush(self.key, self.format(msg))
                    p.ltrim(self.key, -self.max_messages, -1)
                    p.execute()
                else:
                    self.redis_client.rpush(self.key, self.format(msg))
                if self.ttl:
                    self.redis_client.expire(self.key, self.ttl)
            except redis.RedisError:
                pass

    def emit(self, record):
        """
        Want to send record to redis logging list
        """
        try:
            self.msg_queue.put_nowait(record)
        except Queue.Full:
            pass
