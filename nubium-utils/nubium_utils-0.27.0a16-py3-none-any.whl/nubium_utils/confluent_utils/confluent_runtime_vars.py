"""
confluent-kafka runtime environment variables
"""

from os import environ
from nubium_utils import general_runtime_vars
from nubium_utils.env_var_generator import env_vars_creator


def default_env_vars():
    """
    Environment variables that have defaults if not specified.
    """
    return {
        'CONSUMER_POLL_TIMEOUT': environ.get('CONSUMER_POLL_TIMEOUT', '10'),
        'CONSUMER_TIMEOUT_LIMIT_MINUTES': environ.get('CONSUMER_TIMEOUT_LIMIT_MINUTES', '2'),

        # Performance
        'CONSUMER_ENABLE_AUTO_COMMIT': environ.get('CONSUMER_ENABLE_AUTO_COMMIT', 'true'),
        'CONSUMER_AUTO_COMMIT_INTERVAL_SECONDS': str(int(environ.get('CONSUMER_AUTO_COMMIT_INTERVAL_SECONDS', '20'))*1000),
        'MESSAGE_BATCH_MAX_MB': str(int(float(environ.get('MESSAGE_BATCH_MAX_MB', '2')) * 2 ** 20)),
        'MESSAGE_TOTAL_MAX_MB': str(int(float(environ.get('MESSAGE_TOTAL_MAX_MB', '3')) * 2 ** 20)),
        'MESSAGE_QUEUE_MAX_MB': str(int(float(environ.get('MESSAGE_QUEUE_MAX_MB', '10')) * 2 ** 10)),

        # All required below if using "retry" logic
        'CONSUME_TOPICS': environ.get('CONSUME_TOPICS', ''),
        'TIMESTAMP_OFFSET_MINUTES': environ.get('TIMESTAMP_OFFSET_MINUTES', '0'),
        'RETRY_COUNT_MAX': environ.get('RETRY_COUNT_MAX', '0'),
        'PRODUCE_RETRY_TOPICS': environ.get('PRODUCE_RETRY_TOPICS', ''),
        'PRODUCE_FAILURE_TOPICS': environ.get('PRODUCE_FAILURE_TOPICS', '')}


def required_env_vars():
    """
    Environment variables that require a value (aka no default specified).
    """
    return {}


def all_env_vars():
    return {
        **general_runtime_vars.all_env_vars(),
        **default_env_vars(),
        **required_env_vars()
    }


env_vars = env_vars_creator(all_env_vars)
