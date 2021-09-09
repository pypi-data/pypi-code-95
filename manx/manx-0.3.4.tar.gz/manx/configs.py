import logging
from collections import OrderedDict
from typing import Dict

from manx.files import MigrationFile, get_python_files

log = logging.getLogger("manx.configs")


async def get_config(migration_package: str) -> Dict:
    log.debug(f"Get latest config for package {migration_package}")
    all_configs = await get_all_configs(migration_package)
    try:
        _, value = all_configs.popitem()
        return value
    except KeyError:
        return {}


async def get_all_configs(
    migration_package: str, last_applied: MigrationFile = None
) -> OrderedDict:
    log.debug(f"Get all configs for package {migration_package}")
    py_migrations = get_python_files(migration_package)
    all_configs = OrderedDict()
    config: Dict = {}

    for migration in py_migrations:
        if last_applied and last_applied.stamp == migration.stamp:
            config = last_applied.config
        else:
            config = await migration.module.configuration(config)
        all_configs[migration.stamp] = config
    return all_configs
