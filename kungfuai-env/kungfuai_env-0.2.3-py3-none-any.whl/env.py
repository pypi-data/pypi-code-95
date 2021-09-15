import logging
import os
from os.path import exists
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Environment:
    _possible_environments = {'local': [".local.env", ".local.env.local"]}

    def __init__(self, env_base_path: str = "./"):
        self._env_base_path = env_base_path

    def register_environment(self, env_name: str):
        env_name = env_name.lower()

        # does this env exist?
        if env_name in self._possible_environments:
            logger.warning(
                f"The env_name {env_name} is already registered. Did you mistakenly call "
                f"`register_environment` again?"
            )
            return

        self._possible_environments[env_name] = [
            f".{env_name.lower()}.env",
            f".{env_name.lower()}.env.local",
        ]

    def environments(self):
        return self._possible_environments

    def load_env(self):
        env = self.get_env()
        logger.info(f"Loading env {env}")
        did_load_occur = False
        for env_file_name in self._possible_environments[env]:
            intended_path_to_load = Path(self._env_base_path, env_file_name)
            logger.info(intended_path_to_load)
            if exists(intended_path_to_load):
                did_load_occur = True
                load_dotenv(dotenv_path=intended_path_to_load, verbose=True, override=False)

        assert did_load_occur, \
            "ERROR: No environments were loaded. " \
            "PLEASE READ: Did you appropriately set the path in your Environment() constructor? " \
            "Usually, we set it to Environment('src/env') where the class is constructed at the " \
            "`src` level, and there are env files located in the `src/env directory"

    def get_env(self):
        return os.getenv("ENV", "local").lower()

    def get_env_file(self):
        env = self.get_env()
        env_file_name = self._possible_environments[env][0]
        return Path(self._env_base_path, env_file_name)
