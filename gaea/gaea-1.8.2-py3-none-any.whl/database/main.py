import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from gaea.config import CONFIG
from gaea.helpers.metaclass import Box
from gaea.errors import AlreadyInitialized


def get_engine(url):
    echo_query = CONFIG.LOG_LEVEL <= logging.DEBUG
    engine = create_engine(url, echo=echo_query, pool_size=5, pool_recycle=3600)
    return engine


def get_database_url(dbname=None):
    user = CONFIG.DATABASE_USER
    pswd = CONFIG.DATABASE_PASSWORD
    host = CONFIG.DATABASE_HOST
    port = CONFIG.DATABASE_PORT
    dbnm = dbname or CONFIG.DATABASE_DBNAME

    if any(val is None for val in (user, pswd, host, port, dbnm)):
        raise ValueError("Database configuration is missing")

    return f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{dbnm}"


class db:
    def __init__(self, url=None):
        self.url = url or get_database_url()
        self.engine = get_engine(self.url)
        self.session_factory = sessionmaker(autoflush=False, bind=self.engine)
        self._sessions = []

    def get_session(self):
        return self.session_factory()

    def clear(self):
        self.engine.dispose()

    def __enter__(self):
        session = self.get_session()
        self._sessions.append(session)
        return session

    def __exit__(self, tp, vl, tb):
        session = self._sessions.pop(-1)
        session.rollback()
        session.close()
