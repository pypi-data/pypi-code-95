from alembic import config
from alembic import script
from alembic.runtime import migration
import sqlalchemy

#import exceptions
import os
from pathlib import Path
import configparser

from ppss_auth import __path__


import logging
l = logging.getLogger('ppssauth')
    

def checkDBRevision(engine=None, session=None):
  if engine is None:
        engine = session.get_bind()
  path = Path(__file__).resolve().parents[2]
  #here = os.path.join(str(__path__[0]),"..")
  config_uri = os.path.join(path,"ppss_auth/alembic/alembic.ini")
  l.debug("loading conf from {}".format(config_uri))
  iniconfig = configparser.ConfigParser()
  iniconfig.read(config_uri)
  iniconfig["alembic"]["here"] = str(path)
  l.info("checkDBRevision: path:{}".format(path))
  #engine = sqlalchemy.create_engine(DATABASE_URL)
  alembic_cfg = config.Config(config_uri)
  script_ = script.ScriptDirectory.from_config(alembic_cfg)
  with engine.begin() as conn:
      context = migration.MigrationContext.configure(conn,opts={"version_table":"ppss_auth_alembic_version"}) #the migration on db
      dbversion = context.get_current_revision()
      migrationversion = script_.get_current_head()
      if dbversion != migrationversion:
          message = 'Current DB version:{}. HEAD migration version:{}\nUpgrade the database using\nppss_auth_upgrade_db <your pyramid ini file>.ini\n'.format(dbversion,migrationversion)
          raise Exception(message)



import re
from ppss_auth.models import Base
def exclude_ppss_auth_tables(config=None,sectionname='alembic:exclude',asadict=True,merge=True):

  def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        for pattern in exclude_tables:
            if pattern.match(name):
                l.warning("excluded {}({}) because matches pattern {}".format(name, type_,pattern) )
                return False
    l.info("{}({}) passed all patterns".format(name,type_))
    return True

  exclude_tables = []
  if config is not None:
    config_ = config.get_section(sectionname)
    tables_ = config_.get("pattern", None)
    l.info("building exclusions")
    if tables_ is not None:
        l.debug("tables_:{}".format(tables_))
        tables = list(
            map(lambda x: re.compile("^" + x.strip().replace("*","(.*)") + "$")
                ,str.splitlines(tables_)
            ) 
        )
        
    exclude_tables += tables
  if (config is None) or merge:
    tables = []
    for table in Base.metadata.tables:
      l.debug("adding name {}".format(table))
      tables.append (re.compile("^" + table + "$") )
    #for table in Base.__subclasses__():
    #  l.debug("adding name {}".format(table.__tablename__))
    #  tables.append (re.compile("^" + table.__tablename__ + "$") )
    tables.append(re.compile("^ppss_auth_alembic_version$"))
    exclude_tables += tables
  l.info("excluded tables:{}".format(exclude_tables))
  
  if asadict:
    return {"include_object":include_object}

  return include_object



