# pylint: disable=unused-import
from typing import List

from clicasso import Command

COMMANDS: List[Command] = []
_EXCEPTIONS = (ImportError, ModuleNotFoundError)


try:
    from apparatus.commands import db

    COMMANDS.extend(db.COMMANDS)
except _EXCEPTIONS as exc:
    pass

try:
    from apparatus.commands import config

    COMMANDS.extend(config.COMMANDS)
except _EXCEPTIONS as exc:
    pass


try:
    from apparatus.commands import kube

    COMMANDS.extend(kube.COMMANDS)
except _EXCEPTIONS as exc:
    pass
