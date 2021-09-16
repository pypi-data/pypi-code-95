import contextlib
import uuid

from gaea.database.main import db, get_database_url
from gaea.models.base import Base


@contextlib.contextmanager
def get_temporary_database():
    db_client = db()
    session = db_client.get_session()
    conn = session.connection()

    dbname = "test_" + str(uuid.uuid4()).replace("-", "")
    conn.execute("commit")
    conn.execute(f"CREATE DATABASE {dbname}")
    conn.execute("commit")

    yield get_database_url(dbname)

    conn.execute(f"DROP DATABASE {dbname}")
    conn.execute("commit")

    session.close()
    conn.close()
    db_client.clear()
