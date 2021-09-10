import abc
import threading
from typing import List
from contextlib import contextmanager
from shared_context.domain.model import AggregateRoot, Repository as BaseRepository
from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker, scoped_session


class SessionBuilder:
    _session = None
    _lock = threading.Lock()

    @classmethod
    def build(cls, dsn: str):
        if not cls._session:
            with cls._lock:
                if not cls._session:
                    session_factory = sessionmaker(bind=create_engine(dsn), expire_on_commit=False)
                    cls._session = scoped_session(session_factory)
        return cls._session


@contextmanager
def session_scope(dsn: str):
    Session = SessionBuilder.build(dsn)
    session = Session()

    try:
        yield session
    except Exception:
        raise
    finally:
        session.close()
        Session.remove()


class DbalServiceError(RuntimeError):
    pass


class Repository(BaseRepository):
    def __init__(self, aggregate: AggregateRoot, dsn: str):
        self._aggregate = aggregate
        self._dsn = dsn

    def create_connection(self):
        return create_engine(self._dsn)

    def add(self, aggregate: AggregateRoot) -> None:
        with session_scope(self._dsn) as session:
            session.add(aggregate)
            session.commit()

    def save(self, aggregate: AggregateRoot) -> None:
        with session_scope(self._dsn) as session:
            session.add(aggregate)
            session.commit()

    def find(self, **kwargs) -> AggregateRoot:
        with session_scope(self._dsn) as session:
            result = session.query(self._aggregate).filter_by(**kwargs).first()

        return result

    def find_all(self, **kwargs) -> List[AggregateRoot]:
        with session_scope(self._dsn) as session:
            results = session.query(self._aggregate).filter_by(**kwargs).all()

            return results


class DbalService:
    def __init__(self, dsn: str):
        self._connection = create_engine(dsn)

    def execute(self, sentence: str, **data):
        with self._connection.connect() as connection:
            try:
                return connection.execute(text(sentence), **data)
            except exc.SQLAlchemyError as error:
                raise DbalServiceError(str(error))
            finally:
                connection.close()


class Orm(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        if subclass is not Orm:
            return NotImplemented

        if hasattr(subclass, "start_mappers") and callable(subclass.start_mappers):
            return True

        return NotImplemented

    @abc.abstractmethod
    def start_mappers(self) -> None:
        raise NotImplemented
