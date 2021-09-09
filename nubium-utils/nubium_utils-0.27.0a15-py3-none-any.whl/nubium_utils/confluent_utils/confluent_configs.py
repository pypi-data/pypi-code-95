import logging
from .message_utils import produce_message_callback, consume_message_callback
from nubium_utils.metrics import start_pushing_metrics
from .confluent_runtime_vars import env_vars
from nubium_utils.custom_exceptions import WrappedSignals
from nubium_topic_configs.clusters import cluster_topic_map

LOGGER = logging.getLogger(__name__)
wrapped_signals = WrappedSignals()  # WrappedSignals needs to be initialized (somewhere) to catch signals


def init_ssl_configs():
    if env_vars()["USE_SASL"].lower() == 'true':
        LOGGER.info('Using SASL-authenticated producers/consumers!')
        return {
            "security.protocol": "sasl_ssl",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": env_vars()["SASL_USERNAME"],
            "sasl.password": env_vars()["SASL_PASSWORD"]
        }
    else:
        LOGGER.info('Authentication/encryption disabled for producers/consumers!')
    return {}


def init_schema_registry_configs():
    """
    Provides the avro schema config
    :return: dict, None
    """
    # RHOSAK registry
    LOGGER.info(f'Using the schema server at {env_vars()["SCHEMA_REGISTRY_URL"]}')
    if env_vars()['SCHEMA_REGISTRY_USERNAME']:
        return {'schema.registry.url': f"https://{env_vars()['SCHEMA_REGISTRY_SERVER']}"}
    # local to Bifrost Nubium
    elif env_vars()['SCHEMA_REGISTRY_SSL_CA_LOCATION']:
        return {
            'schema.registry.url': f"https://{env_vars()['SCHEMA_REGISTRY_SERVER']}",
            'ssl.ca.location': env_vars()['SCHEMA_REGISTRY_SSL_CA_LOCATION'],
        }
    # Bifrost Nubium to Bifrost Nubium, local to local
    else:
        return {'schema.registry.url': f"http://{env_vars()['SCHEMA_REGISTRY_SERVER']}"}


def init_producer_configs(topic, ssl_configs=None, schema_registry_configs=None):
    """
    Sets up a single producer.
    """
    if not ssl_configs:
        ssl_configs = {}
    if not schema_registry_configs:
        schema_registry_configs = {}
    return {
        **ssl_configs,
        **schema_registry_configs,
        "bootstrap.servers": cluster_topic_map()[topic],
        "on_delivery": produce_message_callback,
        "acks": "all"}


def init_consumer_configs(topics, ssl_configs=None, schema_registry_configs=None):
    """
    Assummes topics are all in the same cluster.
    """
    cluster = set([cluster_topic_map()[topic] for topic in topics])
    if len(cluster) == 1:
        cluster = list(cluster)[0]
    else:
        raise ValueError('Cluster count for provided consumer topics did not equal 1. Please confirm your topics are on'
                         f'the same cluster. Topics:\n{topics}')
    if not ssl_configs:
        ssl_configs = {}
    if not schema_registry_configs:
        schema_registry_configs = {}
    max_time_between_consumes_mins = int(env_vars()['CONSUMER_TIMEOUT_LIMIT_MINUTES']) + int(env_vars()['TIMESTAMP_OFFSET_MINUTES'])
    return {
        **ssl_configs,
        **schema_registry_configs,
        "bootstrap.servers": cluster,
        "group.id": env_vars()['APP_NAME'],
        "group.instance.id": env_vars()['HOSTNAME'],
        "on_commit": consume_message_callback,
        "enable.auto.commit": True if env_vars()['CONSUMER_ENABLE_AUTO_COMMIT']=='true' else False,
        "auto.commit.interval.ms": int(env_vars()['CONSUMER_AUTO_COMMIT_INTERVAL_SECONDS']),
        "enable.auto.offset.store": False if env_vars()['CONSUMER_ENABLE_AUTO_COMMIT']=='true' else True,
        "max.poll.interval.ms": 60000 * max_time_between_consumes_mins,
        "session.timeout.ms": int(env_vars()['CONSUMER_HEARTBEAT_TIMEOUT_SECONDS']) * 1000,
        "message.max.bytes": int(env_vars()['MESSAGE_BATCH_MAX_MB']),
        "fetch.max.bytes": int(env_vars()['MESSAGE_TOTAL_MAX_MB']),
        "queued.max.messages.kbytes": int(env_vars()['MESSAGE_QUEUE_MAX_MB'])}


def init_metrics_pushing(metrics_manager):
    if env_vars()['DO_METRICS_PUSHING'].lower() == 'true':
        LOGGER.info('Metric pushing to gateway ENABLED')
        start_pushing_metrics(metrics_manager, int(env_vars()['METRICS_PUSH_RATE']))
    else:
        LOGGER.info('Metric pushing to gateway DISABLED')


def get_kafka_configs():
    return init_ssl_configs(), init_schema_registry_configs()
