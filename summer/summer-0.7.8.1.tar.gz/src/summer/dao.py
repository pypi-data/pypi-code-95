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

"""Provides *DAO* support.

Base :py:class:`Dao` class provides access to :py:meth:`Dao.session` and
py:meth:`Dao.connection` properties.

That means that inside any *DAO* object subclassed from :py:class:`Dao` you
can access current (thread-bound) *SqlAlchemy* session simply by accessing
:py:meth:`Dao.session` and direct connection to database by accessing
:py:meth:`Dao.connection`.

Much more interesting is :py:class:`EntityDao` class which is inteded to be
used as a base *DAO* class for your :py:class:`summer.domain.Entity`.
"""

import logging
import typing
import sqlalchemy.engine
import sqlalchemy.orm.exc

from .domain import Entity, CodeEntity, Filter
from .ex import ApplicationException
from .sf import SessionFactory

logger = logging.getLogger(__name__)


class Dao(object):
    """Base *DAO* class.

    Provides safe access to thread bound session through :py:attr:`session`
    attribute.  Alternative is :py:meth:`get_session`.
    """

    def __init__(self, session_factory: SessionFactory):
        """Creates :py:class:`Dao` instance.

        Args:

            session_factory (SessionFactory): session factory to be used
        """
        self.session_factory = session_factory

    @property
    def session(self) -> sqlalchemy.orm.Session:
        """Get current session (bound to current thread).

        Returns:

            Session: current :py:class:`sqlalchemy.orm.Session` instance
        """
        return self.session_factory.sqlalchemy_session

    @property
    def connection(self) -> sqlalchemy.engine.Connection:
        """Get current connection (bound to current thread).

        Use :py:attr:`connection.connection` to obtain
        *Python DB API 2.0 connection* object.

        Returns:

            Connection: current :py:class:`sqlalchemy.engine.Connection` instance
        """
        return self.session_factory.connection


E = typing.TypeVar('E', bound=Entity)


class EntityDao(Dao):
    """Base *DAO* class for persistent classes subclassed from
    :py:class:`summer.domain.Entity`.

    Provides basic persistent operations.

    Defines another property -- :py:meth:`query` -- access to
    generic *SqlAlchemy* query over :py:meth:`clazz`.
    """

    def __init__(self, session_factory: SessionFactory, clazz: typing.Type[E]):
        """Creates :py:class:`EntityDao` instance.

        Args:

            session_factory (SessionFactory): session factory intance to be
                                              passed to superclass
                                              (:py:class:`Dao`)

            clazz (type): reference to class type
        """
        Dao.__init__(self, session_factory)
        self._clazz = clazz

    @property
    def clazz(self) -> type:
        """Get class type for this dao.

        Returns:

            type: class for this :py:class:`EntityDao`
        """
        return self._clazz

    @property
    def query(self) -> sqlalchemy.orm.Query:
        """Get new query instance using :py:meth:`clazz`.

        Returns:

            sqlalchemy.orm.Query: query over :py:meth:`clazz`
        """
        return self.session.query(self.clazz)

    def _check_entity(self, entity: E):
        """Check if entity is correct.

        Args:

            entity (Entity): entity instance to be checked
        """
        if entity is None:
            raise DaoException("entity == None")
        elif not isinstance(entity, self.clazz):
            msg = "entity is not instance of %s" % self.clazz
            raise DaoException(msg, entity_class=entity.__class__)

    def _get_result_list(self, query: sqlalchemy.orm.Query, query_filter: Filter) -> typing.List[E]:
        """Get list of entities with filter offset applied.  Useful for paging.

        Args:

            query (Query): query to be executed

            query_filter (Filter): filter to be used for paging

        Returns:

            list: list of entities using query and paging supplied
        """
        logger.debug("query %s", query)
        logger.debug("query_filter %s", query_filter)
        # apply query_filter limits
        query = query.offset(query_filter.get_offset())
        if query_filter.get_max_results() > 0:
            query = query.limit(query_filter.get_max_results())
        # query
        return query.all()

    def get(self, ident: object) -> typing.Optional[E]:
        """Get entity by :py:attr:`Entity.id` attribute.

        Args:

            ident (object): primary key for :py:class:`Entity`

        Returns:

            Entity: entity instance or raise :py:class:`NoResultFound` if
                    none is found
        """
        return self.query.get(ident)

    def save(self, entity: E) -> E:
        """Save an entity.

        Args:

            entity (Entity): entity to be persisted

        Returns:

            Entity: persisted instance
        """
        self._check_entity(entity)
        self.session.add(entity)
        return entity

    def merge(self, entity: E) -> E:
        """Merge an entity.

        Same as :py:meth:`save`, but entity is associated with current session
        if it is not.  For example if entity comes from another session
        (or thread).

        Args:

            entity (Entity): entity to be merged

        Returns:

            Entity: persisted instance
        """
        self._check_entity(entity)
        return self.session.merge(entity)

    def delete(self, entity_or_id: object) -> E:
        """Delete an entity.

        Args:

            entity_or_id (object): either :py:class:`Entity` or its primary
                                   key

        Returns:

            Entity: just deleted entity instance
        """
        if isinstance(entity_or_id, self.clazz):
            entity = entity_or_id
        else:
            entity = self.get(entity_or_id)
        self._check_entity(entity)
        self.session.delete(entity)
        return entity

    def find(self, query_filter: Filter) -> typing.List[E]:
        """Find collection of entities.

        Args:

            query_filter (Filter): filter with at least paging set

        Returns:

            list: list of entities using query and paging supplied
        """
        return self._get_result_list(self.query, query_filter)

    def get_by_uniq(self, col_name: str, col_value: object) -> E:
        """Get entity by its unique attribute value.

        Args:

            col_name (str): attribute column name

            col_value (object): attribute value


        Returns:

            Entity: entity instance or raise :py:class:`NoResultFound` if
                    none is found.
        """
        assert col_name is not None, "col_name == None"
        assert col_value is not None, "col_value == None"
        kwargs = {col_name: col_value}
        return self.query.filter_by(**kwargs).one()

    def get_by_uniq_or_none(self, col_name: str, col_value: object) -> typing.Optional[E]:
        """Get entity by its unique attribute value.

        Args:

            col_name (str): attribute column name

            col_value (object): attribute value


        Returns:

            Entity: entity instance or ``None`` if none is found.
        """
        try:
            tmp = self.get_by_uniq(col_name, col_value)
            return tmp
        except sqlalchemy.orm.exc.NoResultFound:
            logger.warning("no result found for %s having %s == %s", self.clazz, col_name, col_value)
            return None


T = typing.TypeVar('T', bound=CodeEntity)


class CodeEntityDao(EntityDao):
    """Base *DAO* class for persistent classes subclassed from
    :py:class:`summer.domain.CodeEntity`.

    """

    def __init__(self, session_factory: SessionFactory, clazz: typing.Type[T]):
        """Creates :py:class:`CodeEntityDao` instance.

        Args:

            session_factory (SessionFactory): session factory intance to be
                                              passed to superclass
                                              (:py:class:`Dao`)

            clazz (type): reference to class type
        """
        EntityDao.__init__(self, session_factory, clazz)

    def find_map(self, query_filter: Filter) -> typing.Dict[str, T]:
        """Loads the objects into a map by :py:attr:`CodeEntity.code` attribute
        used as a map key.

            query_filter (Filter): filter with at least paging set

        Returns:

            dict: dictionary of entities using query and paging supplied
        """
        return {i.code: i for i in self.find(query_filter)}


class DaoException(ApplicationException):

    def __init__(self, message: str = None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)
