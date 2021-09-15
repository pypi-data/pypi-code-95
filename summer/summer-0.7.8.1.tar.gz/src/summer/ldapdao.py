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

"""Provides LDAP *DAO* support.  Analogy to :py:mod:`summer.dao` module.

Base :py:class:`LdapDao` provides access to important properties:

#. :py:meth:`LdapDao.connection` property referencing
   :py:class:`ldap3.Connection`

#. :py:meth:`LdapDao.base` property referencing
   :py:class:`summer.lsf.LdapSessionFactory.base` dn value (useful for creating LDAP
   queries)
"""

import logging
import typing

import ldap3

from .lsf import LdapSessionFactory

logger = logging.getLogger(__name__)


class LdapDao(object):
    """Base *DAO* class.  Analogy to :py:class:`summer.dao.Dao` class.

    Provides safe access to thread bound session/connection through
    :py:meth:`session` property and base LDAP dn value through
    :py:meth:`base` property.
    """

    def __init__(self, ldap_session_factory: LdapSessionFactory):
        """Creates :py:class:`LdapDao` instance.

        Args:

            ldap_session_factory (LdapSessionFactory): ldap session factory
                                                       to use
        """
        self.ldap_session_factory = ldap_session_factory

    @property
    def connection(self) -> ldap3.Connection:
        """Delegates to :py:meth:`summer.lsf.LdapSessionFactory.connection`."""
        return self.ldap_session_factory.connection

    @property
    def session(self) -> ldap3.Connection:
        """Compatibility alias for :py:attr:`LdapDao.connection`"""
        return self.connection

    @property
    def base(self) -> str:
        """Delegates to :py:meth:`summer.lsf.LdapSessionFactory.base`."""
        return self.ldap_session_factory.base


class LdapEntityDao(LdapDao):
    """Base *DAO* class for persistent classes subclassed from
    :py:class:`summer.domain.LdapEntity`."""

    def __init__(self, ldap_session_factory: LdapSessionFactory, clazz: typing.Type):
        """Creates :py:class:`LdapEntityDao`.

        Args:

            ldap_session_factory (LdapSessionFactory): ldap session factory
                                                       to use

            clazz (type): reference to class type
        """
        LdapDao.__init__(self, ldap_session_factory)
        self._clazz = clazz

    @property
    def clazz(self) -> typing.Type:
        """Get class type for this dao.

        Returns:

            type: class for this :py:class:`EntityDao`
        """
        return self._clazz
