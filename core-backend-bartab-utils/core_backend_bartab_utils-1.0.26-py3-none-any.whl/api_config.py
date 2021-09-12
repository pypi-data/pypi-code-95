from .string import dash_case_to_upper_slug
from .paths import get_relative_path
from django.conf import settings
import warnings
import environ

warnings.simplefilter("ignore")
env = environ.Env()
environ.Env.read_env()
warnings.simplefilter("default")


def get_api_key(service_name):
    return env("{}_API_KEY".format(
        dash_case_to_upper_slug(service_name)))


def get_invalid_configuration_error_message(service_name):
    api_key_param_name = "{}_API_KEY".format(
        dash_case_to_upper_slug(service_name))

    try:
        env(api_key_param_name)
        return None
    except:
        if settings.IS_DEVELOPMENT or settings.IS_PRODUCTION or settings.IS_QA:
            return "Missing {0} api key, run eb setenv {1}=<{1}>".format(
                service_name,
                api_key_param_name)
        else:
            return "Missing {0} api key, add {1} to: {2}".format(
                service_name,
                api_key_param_name,
                get_relative_path('.env', __file__))


def get_endpoint(url_prefix,
                 api_version,
                 localhost_port):
    if settings.IS_PRODUCTION:
        return "https://{url_prefix}.{DOMAIN}/{api_version}".format(
            url_prefix=url_prefix,
            DOMAIN=settings.DOMAIN,
            api_version=api_version
        )
    elif settings.IS_QA:
        return "https://qa.{url_prefix}.{DOMAIN}/{api_version}".format(
            url_prefix=url_prefix,
            DOMAIN=settings.DOMAIN,
            api_version=api_version
        )
    elif settings.IS_DEVELOPMENT:
        return "https://dev.{url_prefix}.{DOMAIN}/{api_version}".format(
            url_prefix=url_prefix,
            DOMAIN=settings.DOMAIN,
            api_version=api_version
        )
    else:
        return "http://localhost:{localhost_port}/{api_version}".format(
            localhost_port=localhost_port,
            api_version=api_version
        )
