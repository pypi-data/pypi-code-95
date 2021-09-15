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

"""Provides summer *AOP* functionality.

You can find here most useful decorators :py:func:`transactional` for SQL
transaction support and :py:func:`ldapaop`.

"""

import functools
import logging
import typing

from .sf import SessionFactory
from .lsf import LdapSessionFactory

logger = logging.getLogger(__name__)

# TODO martin.slouf 2021-02-20 -- remove global variables
__local_session_factory__: typing.Optional[SessionFactory] = None
__local_ldap_session_factory__: typing.Optional[LdapSessionFactory] = None


def session_scoped(method: typing.Callable) -> typing.Callable:
    """Method decorator marking method to be session scoped.

    It starts a `SessionFactory.session` at the beginning and makes sure the session is closed afterwards.

    Utility method to mimic behaviour of automatically closing the session once it is not used.

    Args:

        method: function to be decorated

    Returns:

        (typing.Callable): decorated function

    """
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = method.__name__
    logger.debug("method %s decorated as session_scoped", mame)

    @functools.wraps(method)
    def _session_scoped(*args, **kwargs) -> object:
        assert isinstance(__local_session_factory__, SessionFactory)
        session = __local_session_factory__.session
        try:
            result = method(*args, **kwargs)
        except Exception as ex:
            logger.exception("exception in tx session = %s", session)
            raise ex
        finally:
            session.close()
        return result

    return _session_scoped


def transactional(method: typing.Callable) -> typing.Callable:
    """Method decorator marking method to be transactional.

    Every decorated method behaves as follows:

    * if no transaction is active and database is *not* in autocommit mode,
      start a new transaction, doing commit/rollback at the end

    * if there is a transaction, just simple continue within the
      transaction without doing commit/rollback at the end (that is left to
      the top-most transactional method)

    Args:

        method: function to be decorated

    Returns:

        (typing.Callable): decorated function

    """
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = method.__name__
    logger.debug("method %s decorated as transactional", mame)

    @functools.wraps(method)
    def _transactional(*args, **kwargs) -> object:
        assert isinstance(__local_session_factory__, SessionFactory)
        session = __local_session_factory__.session
        try:
            session.begin()
            result = method(*args, **kwargs)
            session.commit()
        except Exception as ex:
            logger.exception("exception in tx session = %s", session)
            session.rollback()
            raise ex
        # do not close the session, since objects will be 'expired' once the session is closed
        return result

    return _transactional


def ldapaop(method: typing.Callable) -> typing.Callable:
    """Method decorator marking method to be run in LDAP session.  Analogy to
    :py:func:`summer.aop.transactional` with same logic.

    Intended use case for this decorator is to decorate
    :py:class:`summer.ldapdao.LdapEntityDao` methods and then access
    current *ldap3* session/connection by using
    :py:attr:`summer.ldapdao.LdapDao.session` from within the *DAO* method.
    Thus you can access *ldap3* session/connection (and manipulate data),
    and still have the transaction boundaries defined on top of your
    business methods.

    Args:

        method: function to be decorated

    Returns:

        (typing.Callable): decorated function

    """
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = method.__name__
    logger.debug("method %s decorated as ldapaop", mame)

    @functools.wraps(method)
    def _ldapaop(*args, **kwargs) -> object:
        assert isinstance(__local_ldap_session_factory__, LdapSessionFactory)
        session = __local_ldap_session_factory__.session
        try:
            session.bind()
            return method(*args, **kwargs)
        except Exception as ex:
            logger.exception("exception in ldap session %s", session)
            raise ex
        finally:
            session.unbind()

    return _ldapaop
