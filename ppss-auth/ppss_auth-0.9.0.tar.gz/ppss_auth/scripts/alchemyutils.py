from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import zope.sqlalchemy

import logging
l = logging.getLogger('ppssauth.scripts')

def get_engine(settings, prefix='sqlalchemy.'):
    url = settings['alembic'][prefix+'url']
    l.info("sql url={}".format(url ))
    return create_engine(settings['alembic'][prefix+'url'])


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession

    #return engine