#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

""" the global configuration """

import os
from ast import literal_eval

# pylint: disable=invalid-name
from pathlib import Path
from typing import Union

from ruamel import yaml
from ruamel.yaml import YAMLError

DEFAULT_KAFKA_BOOTSTRAP_SERVER = "10.14.0.23:9092"
DEFAULT_KAFKA_LOG_TOPIC = "titan.logs"
DEFAULT_GRIDMANAGER_ADDRESS = "http://localhost:8080/gridmanager"
DEFAULT_FLOWMANAGER_ADDRESS = "http://localhost:9002/flowmanager"
DEFAULT_PACKAGEMANAGER_ADDRESS = "http://localhost:8087/packagemanager"
DEFAULT_REPOSERVICE_ADDRESS = "http://localhost:8085/object"
DEFAULT_ENDPOINTPROVIDER_ADDRESS = "tcp://127.0.0.1:9021"
VALID_KEY_LENGTHS = (16, 24, 32)


class NotFound:  # pylint: disable=too-few-public-methods
    def __bool__(self):
        return False


NOTFOUND = NotFound()


class Configuration:
    """Current Configuration"""

    def __init__(self):
        self.kafka_bootstrap_servers = DEFAULT_KAFKA_BOOTSTRAP_SERVER
        self.kafka_log_topic = DEFAULT_KAFKA_LOG_TOPIC

        self.no_kafka_today = literal_eval(
            os.getenv("TITAN_METRICS_DISABLED") or os.getenv("TITANFE_WITHOUT_KAFKA") or "False"
        )

        self.gridmanager_address = DEFAULT_GRIDMANAGER_ADDRESS
        self.flowmanager_address = DEFAULT_FLOWMANAGER_ADDRESS
        self.packagemanager_address = DEFAULT_PACKAGEMANAGER_ADDRESS
        self.reposervice_address = DEFAULT_REPOSERVICE_ADDRESS
        self.secret_key = os.getenv("TITAN_SECRET_KEY") or None
        self.endpoint_provider = DEFAULT_ENDPOINTPROVIDER_ADDRESS
        self.IP = None

        self.brick_folder = str(Path.home() / "titanfe/bricks")

    option_aliases = {
        "IP": "IP",
        "gridmanager_address": "GridManager",
        "flowmanager_address": "FlowManager",
        "packagemanager_address": "PackageManager",
        "reposervice_address": "RepositoryService",
        "kafka_bootstrap_servers": "Kafka",
        "kafka_log_topic": "KafkaLogTopic",
        "brick_folder": "BrickFolder",
        "secret_key": "SecretKey",
        "endpoint_provider": "EndpointProvider"
    }

    def update(self, config: Union["Configuration", dict]):
        """update config from dict or other config"""
        for attr, alias in self.option_aliases.items():
            if isinstance(config, Configuration):
                value = getattr(config, attr, NOTFOUND)
            else:
                value = config.get(attr, NOTFOUND) or config.get(alias, NOTFOUND)

            if value is NOTFOUND:
                continue

            setattr(self, attr, value)

    def update_from_yaml(self, file_path):
        """Read and update the configuration from a yaml file"""
        try:
            with open(file_path) as f:
                config = yaml.safe_load(f)
            self.update(config)
        except OSError as error:
            print("Could not read config file", file_path, "-", error)
        except YAMLError as error:
            print("Could not parse config file", file_path, "-", error)


configuration = Configuration()
