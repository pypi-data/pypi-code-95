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

"""Module ``lsf`` defines :py:class:`LdapSessionFactory` class which is
central point for your *LDAP database* access.

Analogy to :py:mod:`summer.sf`.

"""

import ldap3
import logging
import threading

logger = logging.getLogger(__name__)


class LdapConnectionProvider(object):
    """Class to be used as based for providing LDAP session.

    See default implementation in
    :py:class:`summer.lsf.DefaultLdapConnectionProvider`.
    """

    def __init__(self, base: str):
        self._server = None
        self._base = base
        self._connection = None

    @property
    def server(self) -> ldap3.Server:
        """LDAP server property.

        Returns:

            ldap3.Server: LDAP server instance
        """
        return self._server

    @property
    def base(self) -> str:
        """LDAP base property -- convenience value defining portion of a LDAP
        subtree of interest.

        Returns:

            str: Optional property, can be left empty; LDAP base DN for a
            subtree of interest to be used by queries
        """
        return self._base

    def create_connection(self) -> ldap3.Connection:
        """Each call produces a new connection.

        Returns:

            ldap3.Connection: new instance of LDAP connection
        """
        pass


class DefaultLdapConnectionProvider(LdapConnectionProvider):
    lock = threading.RLock()

    def __init__(self, host: str, port: int, login: str, password: str, base: str):
        """
        Args:

            host (str): LDAP base dn

            port (int): server port

            login (str): server login

            password (str): server password in clear text

            base (str): see :py:meth:`LdapConnectionProvider.base`
        """
        LdapConnectionProvider.__init__(self, base)
        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self._base = base
        self._server = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def login(self) -> str:
        return self._login

    @property
    def password(self) -> str:
        return self._password

    @property
    def server(self) -> ldap3.Server:
        if not self._server:
            with DefaultLdapConnectionProvider.lock:
                if not self._connection:
                    self._server = ldap3.Server(self.host, self.port, get_info=ldap3.ALL)
        return self._server

    def create_connection(self) -> ldap3.Connection:
        return ldap3.Connection(
            self.server,
            user=self.login,
            password=self.password,
            authentication=ldap3.SIMPLE,
            client_strategy=ldap3.SYNC,
            check_names=True)


class LdapSessionFactory(object):
    """Thread safe *ldap3* session provider.  Analogy to
    :py:class:`summer.sf.SessionFactory`.

    """

    class Local(threading.local):
        """Thread local session wrapper.

        There is an active :py:class:`ldap3.Connection` instance in
        :py:attr:`ldap_session` attribute.
        """

        def __init__(self, ldap_connection_provider: LdapConnectionProvider):
            threading.local.__init__(self)
            self._ldap_connection_provider = ldap_connection_provider
            self._connection = None

        def __del__(self):
            self.unbind()

        @property
        def base(self) -> str:
            """Delegates to :py:meth:`LdapConnectionProvider.base`."""
            return self._ldap_connection_provider.base

        @property
        def connection(self) -> ldap3.Connection:
            if self._connection:
                logger.debug("accessing connection = %s", self._connection)
            else:
                self._connection = self._ldap_connection_provider.create_connection()
                logger.debug("new thread local connection created, session = %s", self._connection)
            return self._connection

        def bind(self):
            self.connection.bind()

        def unbind(self):
            # NOTE martin 2016-09-17 -- direct access to attributes, not through properties
            if self._connection:
                self._connection.unbind()
                self._connection = None

    def __init__(self, ldap_connection_provider: LdapConnectionProvider):
        """Creates :py:class:`LdapSessionFactory` instance.

        Args:

            ldap_connection_provider (LdapConnectionProvider): LDAP connection provider

            base (str): LDAP base dn
        """
        self._ldap_connection_provider = ldap_connection_provider
        self._session = LdapSessionFactory.Local(ldap_connection_provider)

    @property
    def base(self) -> str:
        """Delegates to :py:meth:`LdapSessionFactory.Local.base`"""
        return self.session.base

    @property
    def session(self) -> Local:
        """Get current thread-local *ldap3 session* wrapper (creating one, if
        non-existent).

        Returns:

            LdapSessionFactory.Local: existing or just created
            *ldap3 session* wrapper

        """
        return self._session

    @property
    def connection(self) -> ldap3.Connection:
        """Delegates to :py:meth:`LdapSessionFactory.Local.connection`"""
        return self.session.connection
