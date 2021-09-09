import logging
from .confluent_runtime_vars import env_vars
from nubium_utils.custom_exceptions import IncompatibleEnvironmentError, ProducerTimeoutFailure

LOGGER = logging.getLogger(__name__)


def success_headers(headers):
    """
    Updates headers for a message when a process succeeds

    Resets the kafka_retry_count to 0,
    or adds if it didn't originally exist
    """

    try:
        headers = dict(headers)
    except TypeError:
        headers = {}

    headers['kafka_retry_count'] = '0'
    return headers


def produce_message_callback(error, message):
    """
    Logs the returned message from the Broker after producing
    NOTE: Headers not supported on the message for callback for some reason.
    NOTE: Callback requires these args
    """
    LOGGER.debug('Producer Callback...')
    if error:
        LOGGER.critical(error)
    else:
        LOGGER.debug('Producer Callback - Message produced successfully')


def consume_message_callback(error, partitions):
    """
    Logs the info returned when a successful commit is performed
    NOTE: Callback requires these args
    """
    LOGGER.debug('Consumer Callback...')
    if error:
        LOGGER.critical(error)
    else:
        LOGGER.debug('Consumer Callback - Message consumption committed successfully')


def confirm_produce(producers, attempts=3, timeout=20):
    """
    Ensure that messages are actually produced by forcing synchronous processing. Must manually check the events queue
    and see if it's truly empty since flushing timeouts do not actually raise an exception for some reason.

    NOTE: Only used for synchronous producing, which is dramatically slower than asychnronous.
    """
    if isinstance(producers, dict):
        producers = producers.values()
    else:
        producers = [producers]
    for producer in producers:
        attempt = 1
        while producer.__len__() > 0:
            if attempt <= attempts:
                LOGGER.debug(f"Produce flush attempt: {attempt} of {attempts}")
                producer.flush(timeout=timeout)
                attempt += 1
            else:
                raise ProducerTimeoutFailure


def synchronous_message_handling(producers=None, consumer=None):
    """
    Force the producer/consumer to acknowledge any outstanding, uncommitted messages.
    """
    if env_vars()['CONSUMER_ENABLE_AUTO_COMMIT'].lower() == 'true':
        raise IncompatibleEnvironmentError('CONSUMER_ENABLE_AUTO_COMMIT', 'true')
    if producers:
        LOGGER.debug('Waiting for produce to finish...')
        confirm_produce(producers)
    if consumer:
        LOGGER.debug('Waiting for commits to finalize...')
        consumer.commit(asynchronous=False)


def handle_no_messages(no_msg_exception=None, producers=None):
    """
    Since producer.poll() is typically called within the NU produce_message method, we want to acknowledge
    any outstanding produce attempts while the app has nothing to consume (and thus not actively producing/polling).
    """
    if no_msg_exception:
        LOGGER.debug(no_msg_exception)
    if producers:
        LOGGER.debug('flushing remaining producer queues')
        confirm_produce(producers)


def shutdown_cleanup(producers=None, consumer=None):
    """
    As part of shutdown, make sure all queued up produce messages are flushed, gracefully kill the consumer.
    """
    LOGGER.info('Performing graceful teardown of producer and/or consumer...')
    if consumer:
        LOGGER.debug("Shutting down consumer; no further commits can be queued or finalized.")
        consumer.close()
    if producers:
        LOGGER.debug("Sending/confirming the leftover messages in producer message queue")
        confirm_produce(producers, timeout=30)
