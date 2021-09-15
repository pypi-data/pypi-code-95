# Copyright (C) 2009-2020 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Module ``sf`` defines :py:class:`SessionFactory` class which is central
point for your ORM mapping and *SQL database* access providing connections
to database.

"""

import logging
import threading
import typing
import sys
import sqlalchemy.engine
import sqlalchemy.orm.session
import sqlalchemy.ext.declarative.api

from .ex import SummerConfigurationException
from .ex import NotImplementedException

logger = logging.getLogger(__name__)


class SessionProvider(object):
    """Class to be used as based for providing *SqlAlchemy* session.

    See default implementation in
    :py:class:`summer.sf.DefaultSessionProvider`.
    """

    def __init__(self):
        pass

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        """Get *SqlAlchemy* engine implementation.

        Returns:

            sqlalchemy.engine.Engine: *SqlAlchemy* engine implementation
        """
        raise NotImplementedException()

    @property
    def metadata(self) -> sqlalchemy.MetaData:
        """Get *SqlAlchemy* metadata.

        Returns:

            sqlalchemy.Metadata: *SqlAlchemy* metadata
        """
        raise NotImplementedException()

    @property
    def sessionmaker(self) -> sqlalchemy.orm.sessionmaker:
        """Get *SqlAlchemy* session factory class.

        Returns:

            sqlalchemy.orm.sessionmaker: *SqlAlchemy* session factory class
        """
        raise NotImplementedException()

    @property
    def declarative_base_class(self) -> type:
        """Get *SqlAlchemy* declarative_base type.  Mixing classical and declarative approaches is possible,
        if declarative_base type uses the same metadata and engine with classical approach.  Creating single instance
        of single :py:class:`summer.sf.SessionProvider` ensures it is the same.

        Returns:

            type: *SqlAlchemy* declarative_base type to be used as base class for entities.
        """
        raise NotImplementedException()


class DefaultSessionProvider(SessionProvider):
    """Default implementation of :py:class:`summer.sf.SessionProvider`. Provides access to *SqlAlchemy* internal objectssession.

    See default implementation in
    :py:class:`summer.sf.DefaultSessionProvider`.
    """
    lock = threading.RLock()

    def __init__(self, uri: str, autocommit: bool = False, **engine_kwargs):
        """
        Args:

            uri (str): *SqlAlchemy*'s uri (ie. connection string)

            autocommit (bool): *SqlAlchemy*'s autocommit

            pool_recycle (int): *SqlAlchemy*'s pool recycling timeout
        """
        super().__init__()
        self._uri = uri
        self._autocommit = autocommit
        self._engine_kwargs = engine_kwargs
        self._engine: sqlalchemy.engine.Engine = None
        self._metadata: sqlalchemy.MetaData = None
        self._sessionmaker: sqlalchemy.orm.sessionmaker = None
        self._declarative_base_class: type = None

    @property
    def uri(self):
        return self._uri

    @property
    def autocommit(self):
        return self._autocommit

    @property
    def engine_kwargs(self) -> typing.Dict[str, object]:
        return self._engine_kwargs

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        if self._engine is None:
            with DefaultSessionProvider.lock:
                if not self._engine:
                    self._engine = sqlalchemy.engine.create_engine(self.uri, **self._engine_kwargs)
        return self._engine

    @property
    def metadata(self) -> sqlalchemy.MetaData:
        if self._metadata is None:
            with DefaultSessionProvider.lock:
                self._metadata = sqlalchemy.MetaData(self.engine)
        return self._metadata

    @property
    def sessionmaker(self) -> sqlalchemy.orm.sessionmaker:
        if self._sessionmaker is None:
            with DefaultSessionProvider.lock:
                if not self._sessionmaker:
                    self._sessionmaker = \
                        sqlalchemy.orm.session.sessionmaker(self.engine, autocommit=self.autocommit)
        return self._sessionmaker

    @property
    def declarative_base_class(self) -> type:
        if self._declarative_base_class is None:
            with DefaultSessionProvider.lock:
                if not self._declarative_base_class:
                    self._declarative_base_class = \
                        sqlalchemy.ext.declarative.declarative_base(self.engine, self.metadata)
        return self._declarative_base_class


class SessionFactory(object):
    """Thread safe *SqlAlchemy* session provider."""

    class Local(threading.local):

        """Thread local session & connection wrapper."""

        def __init__(self, sessionmaker: sqlalchemy.orm.session.sessionmaker):
            super().__init__()
            self._sessionmaker = sessionmaker
            self._sqlalchemy_session = None
            self._nested_counter = 0  # increment and/or decrement for each begin()/commit() invocation

        def __del__(self):
            self.close()

        @property
        def sqlalchemy_session(self) -> sqlalchemy.orm.Session:
            """Get current *SqlAlchemy* session.

            Returns:

                sqlalchemy.orm.Session: existing of just created *SqlAlchemy* session.
            """
            if self._sqlalchemy_session:
                logger.debug("accessing session = %s", self._sqlalchemy_session)
            else:
                self._sqlalchemy_session = self._sessionmaker()
                logger.debug("new thread local session created, session = %s", self._sqlalchemy_session)
            return self._sqlalchemy_session

        @property
        def autocommit(self) -> bool:
            """Delegates to :py:meth:`sqlalchemy_session.autocommit`."""
            return self.sqlalchemy_session.autocommit

        @property
        def connection(self) -> sqlalchemy.engine.Connection:
            """Use :py:attr:`connection.connection` to obtain *Python* DB API
            connection.

            Returns:

                sqlalchemy.engine.Connection: current thread-bound *SqlAclhemy* connection object corresponding to
                current session's transactional state.

            """
            return self.sqlalchemy_session.connection()

        @property
        def active(self) -> bool:
            """Get status of current *SqlAlchemy* transaction.

            Returns:

                bool: `True` if transaction is in progress, `False` otherwise.
            """
            return self._nested_counter > 0

        def close(self):
            """Close the SQLAlchemy session and release it (delete it, so the next access will produce new session)."""
            # NOTE martin 2016-09-17 -- direct access to attributes, not through properties
            if self._sqlalchemy_session is not None:
                if self._sqlalchemy_session.is_active:
                    self._sqlalchemy_session.close()
                del self._sqlalchemy_session
                self._sqlalchemy_session = None
            self._nested_counter = 0

        def begin(self):
            if self.autocommit:
                logger.debug("begin in autocommit mode has no effect")
                return
            self._nested_counter += 1
            if self._nested_counter == 1 and self.sqlalchemy_session.transaction is None:
                self.sqlalchemy_session.begin()
                logger.debug("no transaction active, tx started")
            else:
                logger.debug("nested begin call, another transaction is active, continuing in existing tx")

        def commit(self):
            if self.autocommit:
                logger.debug("commit in autocommit mode has no effect")
                return
            self._nested_counter -= 1
            if self._nested_counter == 0:
                self.sqlalchemy_session.commit()
                logger.debug("top-level commit in transaction, tx committed")
            else:
                logger.debug("nested commit call, another transaction is active, continuing in existing tx")

        def rollback(self):
            if self.autocommit:
                logger.debug("rollback in autocommit mode has no effect")
                return
            self._nested_counter = 0
            self.sqlalchemy_session.rollback()
            logger.debug("tx rollback")

    def __init__(self, session_provider: SessionProvider):
        """Creates :py:class:`SessionFactory` instance.

        Args:

            uri (str): *SqlAlchemy* connection string (including username
                       and password)

        """
        self._session_provider = session_provider
        self._session = SessionFactory.Local(self._session_provider.sessionmaker)
        self._table_definitions = None
        self._class_mappings = None

    @property
    def metadata(self) -> sqlalchemy.MetaData:
        return self._session_provider.metadata

    @property
    def table_definitions(self) -> 'AbstractTableDefinitions':
        """Get current table definitions.

        Returns:

            TableDefinitions: current :py:class:`TableDefinitions` instance
        """
        return self._table_definitions

    @table_definitions.setter
    def table_definitions(self, table_definitions: 'AbstractTableDefinitions'):
        """Set table definitons.

        See :py:meth:`summer.context.Context.orm_init` method.

        """
        self._table_definitions = table_definitions
        self._table_definitions.define_tables(self)
        logger.info("table definitions registered: %s", self._session_provider.metadata.tables)

    @property
    def class_mappings(self) -> 'AbstractClassMappings':
        """Get current class mappings.

        Returns:

            ClassMappings: current :py:class:`ClassMappings` instance
        """
        return self._class_mappings

    @class_mappings.setter
    def class_mappings(self, class_mappings: 'AbstractClassMappings'):
        """Set class mappings.

        See :py:meth:`summer.context.Context.orm_init` method.

        """
        if self.table_definitions is None:
            msg = "unable to register mappings -- set table definitions first"
            raise SummerConfigurationException(msg)
        self._class_mappings = class_mappings
        self._class_mappings.create_mappings(self)
        logger.info("class mappings registered")

    @property
    def session(self) -> Local:
        """Get current thread-local *SqlAlchemy session* wrapper (creating one, if
        non-exististent).

        Returns:

            SessionFactory.Local: existing or just created *SqlAlchemy session* wrapper
        """
        return self._session

    @property
    def sqlalchemy_session(self) -> sqlalchemy.orm.Session:
        """Delegates to :py:meth:`SessionFactory.Local.sqlalchemy_session`."""
        return self.session.sqlalchemy_session

    @property
    def connection(self) -> sqlalchemy.engine.Connection:
        """Delegates to :py:meth:`SessionFactory.Local.connection`."""
        return self.session.connection

    @property
    def dialect(self) -> sqlalchemy.engine.Dialect:
        """Get *SqlAlchemy* dialect.

        Returns:

            sqlalchemy.engine.Dialect: current *SqlAlchemy* dialect
        """
        return self._session_provider.engine.dialect

    @property
    def sqlite_dialect(self) -> bool:
        """*SQLite* is great database for testing or local access, but not designed
        for multi-threaded/-process applications.  Sometimes it is handy to
        know you are using it to bypass its limitations.

        Returns:

            bool: `True` if running over sqlite, `False` otherwise.

        """
        import sqlalchemy.dialects.sqlite
        return isinstance(self.dialect, sqlalchemy.dialects.sqlite.dialect)

    def create_schema(self):
        """Create database schema using *SqlAlchemy*.  Call once
        :py:attr:`table_definitions` are set.

        Use with caution -- will destroy all your data!
        """
        if self.table_definitions is None:
            msg = "unable to create schema -- set table definitions first"
            raise SummerConfigurationException(msg)
        # delegate call to ORM layer
        self.metadata.drop_all()
        self.metadata.create_all()


class AbstractTableDefinitions(object):
    """
    Container for *SqlAlchemy* table definitions.  Registers itself at
    session factory.  A callback class -- use to provide table definitions
    to ORM.

    See :py:meth:`summer.context.Context.orm_init` method.
    """

    def define_tables(self, session_factory: SessionFactory):
        """Override in subclasses to define database tables."""
        pass


class AbstractClassMappings(object):
    """Container for *SqlAlchemy* mappings.  Registers itself at session
    factory.  A callback class -- use to provide class mappings to ORM.

    See :py:meth:`summer.context.Context.orm_init` method.
    """

    def create_mappings(self, session_factory: SessionFactory):
        """Override in subclasses to define mappings (tables to ORM classes --
        entities).
        """
        pass
