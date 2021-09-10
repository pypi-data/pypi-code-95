from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from sys import argv
import os

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
import sqlalchemy as sa

from ..ppss_auth_utils import scriptutils


import logging
l = logging.getLogger('ppss_auth')

config = None

def main():

  config = scriptutils.configFromArgv()
  engine = scriptutils.engineFromConfig(config)
  
  try:
    l.info("engine created")
    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)
    l.info("op created")

    op.drop_table('ppssuser_lk_ppssgroup')
    op.drop_table('ppssgroup_lk_ppsspermission')
    op.drop_table('ppss_passwordhistory')
    op.drop_table('ppss_loginhistory')
    op.drop_table('ppss_user')
    op.drop_table('ppss_permission')
    op.drop_table('ppss_group')
    op.drop_table('module_db_version')
    op.drop_table('ppss_auth_alembic_version')
    l.info("tables dropped")
    conn.commit()
    l.info("connection committed")
  except Exception as e:
    l.exception("something went wrong:{}".format(e))
