import dataclasses
import logging
from typing import Dict

import dacite
from racetrack_client.log.context_error import wrap_context
from racetrack_client.client_config.io import load_client_config, save_client_config
from racetrack_client.client_config.client_config import Credentials, ClientConfig
from racetrack_client.utils.url import trim_url


def set_credentials(repo_url: str, username: str, token_password: str):
    client_config = load_client_config()
    client_config.git_credentials[repo_url] = Credentials(username=username, password=token_password)
    logging.info(f'git credentials added for repo: {repo_url}')
    save_client_config(client_config)


def set_config_setting(setting_name: str, setting_value: str):
    client_config = load_client_config()
    config_dict: Dict = dataclasses.asdict(client_config)

    assert setting_name in config_dict, f'client config doesn\'t have setting named {setting_name}'
    config_dict[setting_name] = setting_value
    with wrap_context('converting setting to target data type'):
        client_config = dacite.from_dict(
            data_class=ClientConfig,
            data=config_dict,
            config=dacite.Config(cast=[]),
        )

    logging.info(f'Client setting {setting_name} set to: {setting_value}')
    save_client_config(client_config)


def set_config_url_alias(alias: str, lifecycle_url: str):
    """Set up an alias for Lifecycle URL"""
    client_config = load_client_config()
    lifecycle_url = trim_url(lifecycle_url)
    client_config.lifecycle_url_aliases[alias] = lifecycle_url
    logging.info(f'Alias "{alias}" set to Racetrack URL {lifecycle_url}')
    save_client_config(client_config)
