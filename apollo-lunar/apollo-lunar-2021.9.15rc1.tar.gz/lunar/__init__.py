from __future__ import annotations
from typing import Any, List
from enum import Enum

import configparser
import os
from pathlib import Path

from .config import Config
from .lunar_client import LunarError
from .data import BatchClient, DataClient, DatasetClient, QueryClient
from .ml import EDDService, ModelRegistry
from .rec import ChannelClient, ExperimentClient, RecommendationClient


LUNAR_CREDENTIALS_PATH = ".lunar/credentials"

SERVICE_CLIENT_MAP = {
    "channel": {"client": ChannelClient, "api_type": "REC"},
    "experiment": {"client": ExperimentClient, "api_type": "REC"},
    "recommend": {"client": RecommendationClient, "api_type": "REC"},
    "batch": {"client": BatchClient, "api_type": "DATA"},
    "data": {"client": DataClient, "api_type": "DATA"},
    "dataset": {"client": DatasetClient, "api_type": "DATA"},
    "query": {"client": QueryClient, "api_type": "DATA"},
}


class LunarEnv(Enum):
    """
    Lunar environments.
    """

    LOCAL = "LOCAL"
    DEV = "DEV"
    STG = "STG"
    PRD = "PRD"

    @classmethod
    def list_items(cls) -> List[LunarEnv]:
        """
        Return all names of Lunar environments
        """
        return [t for t in cls]

    @classmethod
    def list_values(cls) -> List[str]:
        """
        Return all values of Lunar environments
        """
        return [t.value for t in cls]


def _init_config(env: str = None, apikey: str = None) -> Config:
    env = env or os.getenv("LUNAR_ENV")
    apikey = apikey or os.getenv("LUNAR_APIKEY")

    if not env or not apikey:
        credential_path = Path.home().joinpath(LUNAR_CREDENTIALS_PATH)
        if not os.path.exists(credential_path):
            raise LunarError(code=404, msg="Credential file does not exist")

        config = configparser.ConfigParser()
        config.read(credential_path)

        if env:
            for section in config.values():
                if section.get("env") == env:
                    apikey = section.get("apikey")
                    break

            if not apikey:
                raise LunarError(code=404, msg=f"No profile defined for env `{env}` in the credential file")

        else:
            lunar_profile = os.environ.get("LUNAR_PROFILE") or "default"
            if not config.has_section(lunar_profile):
                raise LunarError(code=404, msg=f"Credential file does not have `{lunar_profile}` section")

            section = config[lunar_profile]
            try:
                apikey = section["apikey"]
                env = section["env"]
            except KeyError as e:
                raise LunarError(code=404, msg=f"Credential file does not have a key `{str(e)}`")

    try:
        config = Config(env=env.upper(), apikey=apikey)
    except AttributeError:
        raise LunarError(code=404, msg=f"`Config` does not exist for env {env}")

    return config


def client(service_name: str = None, env: str = None, apikey: str = None) -> Any:
    """
    Create a client object for lunar API.

    ## Args

    - service_name: (optional) (str) The name of a service for the client
    - env: (optional) (str) The name of a environment for lunar API (`local`|`dev`|`stg`|`prd`)
    - apikey: (optional) (str) The access apikey for lunar API

    ## Example

    ```python
    import lunar

    client = lunar.client("channel")
    ```
    """

    try:
        client_map = SERVICE_CLIENT_MAP[service_name]
    except KeyError:
        raise LunarError(code=404, msg=f"`service_name` {service_name} is not supported.")

    config = _init_config(env=env, apikey=apikey)
    config.__setattr__("URL", config.__dict__[f"LUNAR_{client_map['api_type'].upper()}_URL"])

    return client_map["client"](config)


def model_registry(env: str = None, apikey: str = None) -> ModelRegistry:
    config = _init_config(env=env, apikey=apikey)
    return ModelRegistry(config)


def edd(env: str = None, apikey: str = None) -> EDDService:
    config = _init_config(env=env, apikey=apikey)
    return EDDService(config)
