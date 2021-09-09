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
"""Module that invokes the migration engine, based on generated sample."""

from logging import getLogger
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

CFG = context.config

SEC = 'boltlight_log'
env = {}
env['boltlightlogfilename'] = 'boltlight.log'
if CFG.get_section_option(SEC, 'boltlight'):
    env['boltlightlogfilename'] = CFG.get_section_option(SEC, 'boltlight')
env['migrationslogfilename'] = 'migrations.log'
if CFG.get_section_option(SEC, 'migrations'):
    env['migrationslogfilename'] = CFG.get_section_option(SEC, 'migrations')

fileConfig(CFG.config_file_name, disable_existing_loggers=False, defaults=env)

LOGGER = getLogger(__name__)

LOGGER.info('%s DB migration: begin %s', '*' * 25, '*' * 26)

# add your model's MetaData object here for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
TARGET_METADATA = None


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an
    Engine is acceptable here as well. By skipping the Engine creation we don't
    even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    print('Offline mode is not supported')
    import sys
    sys.exit(1)


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    try:
        connectable = CFG.attributes.get('connection', None)
        if connectable is None:
            # only create Engine if we don't have a Connection
            # from the outside
            connectable = engine_from_config(
                CFG.get_section(CFG.config_ini_section),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )
        with connectable.connect() as connection:
            context.configure(connection=connection,
                              TARGET_METADATA=TARGET_METADATA)
            with context.begin_transaction():
                context.run_migrations()
    except Exception:
        LOGGER.error('Error during DB migration')
        import sys
        sys.exit(1)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

LOGGER.info('%s DB migration: end %s', '*' * 25, '*' * 28)
