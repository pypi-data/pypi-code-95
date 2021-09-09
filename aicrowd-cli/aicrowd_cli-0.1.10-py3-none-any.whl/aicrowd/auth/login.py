"""
Login command
"""

import logging
import os

import click

from aicrowd.auth.exceptions import CredentialException
from aicrowd.auth.helpers import verify_api_key
from aicrowd.constants import LoginConstants
from aicrowd.contexts import ConfigContext
from aicrowd.errors import INVALID_CREDENTIALS


def aicrowd_login(api_key: str = None, config_context: ConfigContext = ConfigContext()):
    """
    Log in using AIcrowd API Key

    Args:
        api_key: AIcrowd API Key
        config_context: CLI Config
    """
    config = config_context.config
    log = logging.getLogger()

    # if api_key not provided, check if env variable was declared
    if api_key is None:
        api_key = os.getenv("AICROWD_API_KEY", "")

    log.info("Verifying API Key...")

    if not verify_api_key(api_key):
        log.error("Invalid API Key provided")
        raise CredentialException(
            "Invalid API Key provided", exit_code=INVALID_CREDENTIALS
        )

    log.info("API Key verified")
    click.echo(click.style("API Key valid", fg="green"))

    current_api_key = config.get(LoginConstants.CONFIG_KEY)

    # if not defined or an older value, update
    if current_api_key != api_key:
        log.info("API Key will be (over) written")
        config.set(LoginConstants.CONFIG_KEY, api_key)

    config.write()
    click.echo(click.style("Saved API Key successfully!", fg="green"))
