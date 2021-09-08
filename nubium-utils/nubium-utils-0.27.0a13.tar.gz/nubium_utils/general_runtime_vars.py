# runtime environment variables used by both confluent-kafka and faust implementations

from os import environ
from .env_var_generator import env_vars_creator


def default_env_vars():
    """
    Environment variables that have defaults if not specified.
    """

    return {
        'LOGLEVEL': environ.get('LOGLEVEL', 'INFO'),

        # Bifrost schema registry
        'SCHEMA_REGISTRY_SSL_CA_LOCATION': environ.get('SCHEMA_REGISTRY_SSL_CA_LOCATION', environ.get('REQUESTS_CA_BUNDLE', '')),

        # RHOSAK authentication
        'NUBIUM_CANONS': environ.get('NUBIUM_CANONS', ''),
        'NUBIUM_INTEGRATIONS': environ.get('NUBIUM_INTEGRATIONS', ''),
        'NUBIUM_TRANSFORMATIONS': environ.get('NUBIUM_TRANSFORMATIONS', ''),
        'USE_SASL': environ.get('USE_SASL', 'true'),
        'SASL_USERNAME': environ.get('SASL_USERNAME', ''),
        'SASL_PASSWORD': environ.get('SASL_PASSWORD', ''),
        'SCHEMA_REGISTRY_USERNAME': environ.get('SCHEMA_REGISTRY_USERNAME', ''),
        'SCHEMA_REGISTRY_PASSWORD': environ.get('SCHEMA_REGISTRY_PASSWORD', ''),

        # Metrics Manager
        'DO_METRICS_PUSHING': environ.get('DO_METRICS_PUSHING', 'true'),
        'METRICS_PUSH_RATE': environ.get('METRICS_PUSH_RATE', '10'),
        'METRICS_SERVICE_NAME': environ.get('METRICS_SERVICE_NAME', f'bifrost-metrics-cache-headless.{environ.get("MP_PROJECT", "")}.svc.cluster.local'),
        'METRICS_SERVICE_PORT': environ.get('METRICS_SERVICE_PORT', '8080'),
        'METRICS_POD_PORT': environ.get('METRICS_POD_PORT', '9091'),

        'CONSUMER_HEARTBEAT_TIMEOUT_SECONDS': '90'}


def required_env_vars():
    """
    Environment variables that require a value (aka no default specified).
    """
    return {
        'HOSTNAME': environ['HOSTNAME'],  # NOTE: Every Openshift pod has a default HOSTNAME (its own pod name).
        'APP_NAME': environ['APP_NAME'],
        'MP_PROJECT': environ['MP_PROJECT'],
        'SCHEMA_REGISTRY_URL': environ['SCHEMA_REGISTRY_URL'],
    }


def derived_env_vars():
    """
    Environment variables with logic surrounding how they are generated.
    """
    if default_env_vars().get('SCHEMA_REGISTRY_USERNAME'):
        schema_registry_server = f"{environ['SCHEMA_REGISTRY_USERNAME']}:{environ['SCHEMA_REGISTRY_PASSWORD']}@{environ['SCHEMA_REGISTRY_URL']}"
    else:
        schema_registry_server = f"{required_env_vars()['SCHEMA_REGISTRY_URL']}"

    return {
        'SCHEMA_REGISTRY_SERVER': schema_registry_server
    }


def all_env_vars():
    return {
        **default_env_vars(),
        **required_env_vars(),
        **derived_env_vars(),
    }


env_vars = env_vars_creator(all_env_vars)
