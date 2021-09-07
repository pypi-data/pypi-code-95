import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def get_session(config):
    quoted = urllib.parse.quote_plus('DRIVER={driver};Server={host};Database={db};UID={user};PWD={password};TDS_Version=7.3;Port=1433;'.format(driver=config.driver, host=config.host, db=config.db, user=config.user, password=config.password))
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

    conn = engine.connect()

    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def get_base():
    return Base