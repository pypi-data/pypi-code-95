# Boltlight - a LN node wrapper
#
# Copyright (C) 2021 boltlight contributors
# Copyright (C) 2018 inbitcoin s.r.l.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For a full list of contributors, please see the AUTHORS.md file.
"""Boltlight's DB migration module."""

from logging import getLogger
from os import path

from alembic import command

from . import settings as sett
from .utils.db import get_alembic_cfg, init_db

LOGGER = getLogger(__name__)


def migrate():
    """Handle DB migration using alembic."""
    if not path.exists(sett.DB_PATH):
        return
    alembic_cfg = get_alembic_cfg(False)
    init_db(alembic_cfg=alembic_cfg)
    # importing this top level would import None
    from .utils.db import ENGINE  # pylint: disable=import-outside-toplevel
    with ENGINE.begin() as connection:
        # pylint: disable=unsupported-assignment-operation
        alembic_cfg.attributes['connection'] = connection
        # pylint: enable=unsupported-assignment-operation
        command.upgrade(alembic_cfg, 'head')
