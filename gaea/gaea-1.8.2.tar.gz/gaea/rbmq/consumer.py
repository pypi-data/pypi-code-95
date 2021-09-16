import pika

from gaea.log import logger

from .base import RBMQClient


class RBMQConsumer(RBMQClient):
    def __init__(
        self,
        handlers,
        queue,
        exchange=None,
        connection_manager=None,
        dead_letter_exchange=None,
    ):
        super().__init__(
            exchange=exchange,
            connection_manager=connection_manager,
            dead_letter_exchange=dead_letter_exchange,
        )
        self.handlers = handlers
        self.queue = queue

    def setup(self, channel):
        self.declare_queue(channel=channel)
        self.bind_queues(channel=channel)

    def declare_queue(self, channel):
        channel.queue_declare(
            queue=self.queue,
            durable=True,
            arguments={"x-dead-letter-exchange": self.dead_letter_exchange},
        )
        channel.queue_declare(queue=f"{self.queue}-dead-letter", durable=True)

    def bind_queues(self, channel):
        for routing_key in self.handlers:
            channel.queue_bind(
                queue=self.queue, exchange=self.exchange, routing_key=routing_key
            )
            channel.queue_bind(
                queue=f"{self.queue}-dead-letter",
                exchange=self.dead_letter_exchange,
                routing_key=routing_key,
            )

    def consume(self):
        while True:
            logger.info("Starting consuming...", queue=self.queue)
            try:
                with self.connection_manager as channel:
                    self.setup(channel)
                    channel.basic_consume(
                        queue=self.queue, on_message_callback=self.process
                    )
                    channel.start_consuming()
            except KeyboardInterrupt:
                logger.info("Goodbye")
                self.connection_manager.close()
                return
            except pika.exceptions.StreamLostError:
                logger.warning(
                    "RBMQ connection stream has been lost. Trying to reconnect"
                )
                continue
            except:
                logger.exception("Critical error on consumer")
                self.connection_manager.close()
                raise

    def process(self, channel, method, properties, body):
        log_details = dict(
            properties=properties, body=body, routing_key=method.routing_key
        )
        logger.info(f"New message received {method.routing_key}", **log_details)

        handler = self.handlers.get(method.routing_key)
        if handler is None:
            logger.warning("Unknown routing key", **log_details)
            channel.basic_nack(method.delivery_tag, requeue=False)
            return

        try:
            success = handler(properties, body)
            if success:
                channel.basic_ack(method.delivery_tag)
            else:
                channel.basic_nack(method.delivery_tag, requeue=False)
        except:  # pylint: disable=bare-except
            logger.exception("Critical error when handling rbmq message", **log_details)
            channel.basic_nack(method.delivery_tag, requeue=False)
