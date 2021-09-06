"""This module defines global instances created when importing Terality.

Importing the terality module should have as few side-effects as possible, and they should not
occur outside of the module.
"""
import atexit
import os
import sys

import requests

from common_client_scheduler.exceptions import TeralityError

from terality.version import __version__
from .client import (
    TeralityClient,
    client_from_config,
    UnreadableTeralityConfigError,
    unconfigured_client,
)
from .constants import ENV_PROD, ENV_TESTS, ENV_UNKNOWN
from .utils import logger, TeralityConfig
from .utils.config import TeralityCredentials
from .sentry import set_up_sentry


def _latest_version_from_pypi() -> str:
    root_package_name = __name__.split(".")[0]
    r = requests.get(f"https://pypi.org/pypi/{root_package_name}/json")
    r.raise_for_status()
    return r.json()["info"]["version"]


def _print_warning_if_not_latest_version() -> None:
    try:
        # Don't perform useless network requests during tests
        if "PYTEST_CURRENT_TEST" in os.environ:
            return
        latest = _latest_version_from_pypi()
        if latest != __version__:
            logger.warning(
                f"You are using version {__version__} of the Terality client, but version {latest} is available. "
                "Consider upgrading your version to get the latest fixes and features."
            )
    except Exception:  # pylint:disable=broad-except  # nosec
        # If any error occurs, don't write a stack trace, just swallow the exception.
        pass


def _atexit_delete_session():
    """Try to close the current global session, using a best effort policy. Swallow any Terality exception."""
    try:
        global_client().close_session()
    except TeralityError:
        pass  # nosec: B110 (try_except_pass)


def global_client() -> TeralityClient:
    """Return a preconfigured Terality client.

    If no configuration is available on the system running Terality code, then this client may not be configured.
    In that case, any attempt to call a method on the client will raise an exception.

    This global Terality client is defined in order to hide the existence of a TeralityClient class to
    the user.

    Code in the Terality module can also manually instantiate a TeralityClient with a different
    configuration when required. For instance, an anonymous client (without credentials) can be useful
    for some requests. The `terality._terality.client` moduule contains several helpers to do
    just that.
    """
    return _GLOBAL_CLIENT


def _init_sentry():
    config = TeralityConfig().load(fallback_to_defaults=True)
    environment = ENV_PROD if config.is_production else ENV_UNKNOWN
    # If the pytest module has already been loaded, we assume we're running in some kind of tests
    # environment, to avoid sending events to Sentry.
    # This is not fool-proof, but there is not great heuristic here.
    # (alternative: test if sys.argv[0] == "pytest", but this may not work for pytest wrappers).
    if "pytest" in sys.modules:
        environment = ENV_TESTS
    try:
        creds = TeralityCredentials().load()
        user_id = creds.user_id
    except Exception:  # pylint: disable=broad-except
        # TODO: less broad exception type
        user_id = None

    set_up_sentry(environment=environment, release=__version__, user_id=user_id)


# Importing the Terality module has some side-effects, defined below.
# This is a consequence of sticking to the pandas API: we can't require the user to manually instantiate a
# "client" class or similar.


_init_sentry()
_print_warning_if_not_latest_version()
try:
    # Try to get a client from configuration files.
    _GLOBAL_CLIENT = client_from_config()
    atexit.register(_atexit_delete_session)
except UnreadableTeralityConfigError:
    # If this fails, default to a client that will warn the user on requests.
    # It's important not to log anything at this point, as the Terality module may be imported in places
    # where not having such a configuration is expected.
    _GLOBAL_CLIENT = unconfigured_client()
