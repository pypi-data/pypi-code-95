import logging
import time
import datetime
import json
from confluent_kafka.avro import AvroConsumer, loads
from nubium_utils.custom_exceptions import NoMessageError, ConsumeMessageError, IncompatibleEnvironmentError
from nubium_utils.metrics import MetricsManager
from .confluent_runtime_vars import env_vars
from .confluent_configs import get_kafka_configs, init_consumer_configs


LOGGER = logging.getLogger(__name__)


def get_consumer(topics, default_schema=None, auto_subscribe=True):
    if isinstance(topics, str):
        topics = topics.split(',')
    LOGGER.debug('Setting up Kafka Consumer')
    consumer = AvroConsumer(
        init_consumer_configs(topics, *get_kafka_configs()),
        reader_key_schema=loads("""{"type": "string"}"""),
        reader_value_schema=loads(json.dumps(default_schema)) if default_schema else None)
    if auto_subscribe:
        consumer.subscribe(topics)  # in case multiple topics are read from
        LOGGER.info(f'Consumer subscribed to topics:\n{topics}')
    return consumer


def _wait_until_message_time(msg_timestamp, guid):
    """
    Wait until the message's timestamp + the deployments offset before handling
    """
    wait_minutes = int(env_vars()['TIMESTAMP_OFFSET_MINUTES'])
    if wait_minutes:
        message_process_time = (msg_timestamp // 1000) + (wait_minutes * 60)

        wait_time = message_process_time - datetime.datetime.timestamp(datetime.datetime.utcnow())

        if wait_time > 0:
            LOGGER.info(f'Waiting {wait_time} seconds before retry message processing continues; GUID {guid}')
            time.sleep(wait_time)


def poll_for_message(consumer):
    """
    Polls the broker for a message using the given timeout.
    If there are no messages to consume, either because None is returned
    or the message error is the no messages error,
    raises a NoMessageError.
    """
    message = consumer.poll(int(env_vars()['CONSUMER_POLL_TIMEOUT']))
    if message is None:
        raise NoMessageError
    return message


def handle_consumed_message(message, monitor):
    """
    Handles a consumed message to check for errors, handle retry waits, and log the consumption as a metric

    If the message is returned with a breaking error,
    raises a ConsumeMessageError.

    If the message is valid, waits until the message's timestamp plus
    the current process's time offset before handling the message.
    This allows retry deployments to wait in a non-
    blocking fashion
    """
    guid = None
    try:
        guid = [item[1] for item in message.headers() if item[0] == 'guid'][0].decode()
        monitor.set_seconds_behind(round(time.time()) - round(message.timestamp()[1]/1000))
        LOGGER.info(f"Message consumed from topic {message.topic()}; GUID {guid}")
    except AttributeError:
        if "object has no attribute 'headers'" in str(message.error()):
            LOGGER.info("Message consumed. No headers, so no guid is available to log.")
    except TypeError:
        LOGGER.info("Message consumed. Headers are None, so no guid is available to log.")
    except IndexError:
        LOGGER.info("Message consumed. Headers found, but no guid is available to log.")

    # If message is None, it can mean that the poll operation timed out,
    # or that there are no more messages to consume

    if message.error():
        if "Broker: No more messages" in str(message.error()):
            LOGGER.warning("Consumer error: %s", message.error())
            raise NoMessageError(message.error())
        else:
            raise ConsumeMessageError(message.error())

    # Wait until message time if using a retry process
    _wait_until_message_time(message.timestamp()[1], guid)

    # Increment the metric for consumed messages by one
    monitor.inc_messages_consumed(1, message.topic())


def consume_message(consumer, monitor: MetricsManager):
    """
    Consumes a message from the broker while handling errors and waiting if necessary

    If the message is valid, then the message is returned
    """
    message = poll_for_message(consumer)
    handle_consumed_message(message, monitor)
    return message


def enqueue_auto_commits(consumer, messages):
    """
    A convenience method for staging message(s) to be committed automatically.
    """
    if env_vars()['CONSUMER_ENABLE_AUTO_COMMIT'].lower() == 'false':
        raise IncompatibleEnvironmentError('CONSUMER_ENABLE_AUTO_COMMIT', 'false')
    if isinstance(messages, list):
        for message in messages:
            consumer.store_offsets(message)
    else:
        consumer.store_offsets(messages)


def consume_message_batch(consumer, monitor: MetricsManager, count, timeout=30):
    """
    Consume a batch of messages.

    Requires manual deserialization since consumer.poll() is the method that has deserialization built in on it.
    """
    messages = consumer.consume(num_messages=count, timeout=timeout)
    if not messages:
        raise NoMessageError
    for message in messages:  # attempt avro deserialize
        if message.key() is not None:
            try:
                message.set_key(consumer._serializer.decode_message(message.key(), is_key=True))
            except:
                pass
        if message.value() is not None:
            try:
                message.set_value(consumer._serializer.decode_message(message.value(), is_key=False))
            except:
                pass
        handle_consumed_message(message, monitor)
    return messages
