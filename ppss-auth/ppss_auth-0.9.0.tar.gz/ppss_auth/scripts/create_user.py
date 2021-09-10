from pyramid.paster import (
    get_appsettings,
    setup_logging,
    bootstrap,
    )

import argparse
import transaction
import configparser
import sqlalchemy as sa
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from ..ppss_auth_utils import scriptutils
from . alchemyutils import (
    get_engine,
    get_session_factory,
    get_tm_session
)

from ..models import PPSsuser,PPSsgroup
from ppss_auth.constants import Conf


import logging
l = logging.getLogger('ppssauth.scripts')

def buildargparser():
  parser = argparse.ArgumentParser(description='create user.')
  parser.add_argument('--username','-u', 
                    help='username',required=True)
  parser.add_argument('--password','-p',help='username',required=True)
  parser.add_argument('--groups','-g',default="",help='comma separated list of groups',required=False)
  parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
  
  return parser.parse_args()


def buildargparserupdate():
  parser = argparse.ArgumentParser(description='create user.')
  parser.add_argument('--username','-u', 
                    help='username',required=True)
  parser.add_argument('--password','-p',help='username',required=False)
  parser.add_argument('--groups','-g',default="",help='comma separated list of groups to add',required=False)
  parser.add_argument('--removegroups','-r',default="",help='comma separated list of groups to remove',required=False)
  parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
  
  return parser.parse_args()


def __create_user(dbsession,username,password,groups):
  u = dbsession.query(PPSsuser).filter(PPSsuser.username==username).first()
  if u:
    raise Exception("user '{}' already exists".format(username))
  u = PPSsuser(
    username = username,
  )
  u.setPassword(password)
  for g in groups:
    group = dbsession.query(PPSsgroup).filter(PPSsgroup.name==g).first()
    if group:
      u.groups.append(group)
  dbsession.add(u)


def __update_user(dbsession,username,password=None,groups2add=[],groups2remove=[]):
  u = dbsession.query(PPSsuser).filter(PPSsuser.username==username).first()
  if u is None:
    raise Exception("user '{}' not found".format(username))
  
  #set new password
  if password:
    u.setPassword(password)

  #remove unwanted groups
  for g in groups2remove:
    for index,mygroup in enumerate(u.groups):
      if mygroup.name == g:
        u.groups.pop(index)
        break

  #add new groups
  for g in groups2add:
    group = dbsession.query(PPSsgroup).filter(PPSsgroup.name==g).first()
    if group:
      u.groups.append(group)

  return u
  




def setup():
  config = scriptutils.configFromArgv()
  Conf.setup(config["app:main"])
  engine = scriptutils.engineFromConfig(config)
  session_factory = sessionmaker(bind=engine)
  return session_factory

def create():
  args = buildargparser()

  config = scriptutils.configFromArgv()
  Conf.setup(config["app:main"])
  engine = scriptutils.engineFromConfig(config)
  session_factory = sessionmaker(bind=engine)
  

  try:
    dbsession = session_factory()
    if dbsession:
      
      __create_user(dbsession,args.username,args.password,args.groups.split(","))
      dbsession.commit()
      print("user '{}' created".format(args.username ) )
  except Exception as e:
    print("An error occurred: {}".format(e))
    dbsession.rollback()
    l.exception("oops {}".format(e))


def update():
  args = buildargparserupdate()
  session_factory = setup()


  try:
    dbsession = session_factory()
    if dbsession:
      
      __update_user(dbsession,args.username,args.password,args.groups.split(","),args.removegroups.split(","))
      dbsession.commit()
      print("user '{}' updated".format(args.username ) )
  except Exception as e:
    print("An error occurred: {}".format(e))
    dbsession.rollback()
    l.exception("oops {}".format(e))
