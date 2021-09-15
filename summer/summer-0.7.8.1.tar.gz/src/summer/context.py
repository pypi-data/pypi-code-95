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

"""Module ``context`` defines an application context (:py:class:`Context`
class)-- a container for (business) objects, that should be available
throughout the application, application layer or module.

"""

import logging
import threading

from . import l10n
from . import lsf
from . import sf
from .ex import (
    NoObjectFoundException,
)

logger = logging.getLogger(__name__)


class Context(object):
    """Context is intelligent container for your business objects, it is a core
    of *summer framework*.

    It is responsible for:

    #. summer framework initialization
    #. instantiating your business classes with their interdependencies
    #. aop configuration

    Emulates mapping type, so you can access business objects by their name
    if required.

    Usually in medium sized applications, you define single global context
    somewhere in main entry point of your program.  Preferred approach is
    to define top level module attribute, see accompanying examples.

    Initialization of context is thread safe.
    """

    lock = threading.RLock()

    def __init__(self, session_provider: sf.SessionProvider = None,
                 ldap_connection_provider: lsf.LdapConnectionProvider = None,
                 localization: l10n.Localization = None):
        """Creates and initializes context instance.  See :py:meth:`init` for more
        information.

        Args:

            session_provider (sf.SessionProvider): object that provides
                                                   SQLAlchemy sessions when
                                                   requested

            ldap_connection_provider (lsf.LdapConnectionProvider): object
                                                                   that
                                                                   provides
                                                                   LDAP
                                                                   connections
                                                                   when
                                                                   requested

            localization (l10n.Localization): localization object
        """

        self._session_provider = session_provider
        self._ldap_connection_provider = ldap_connection_provider
        self._l10n = localization
        self._session_factory = None
        self._ldap_session_factory = None
        self.init()

    def __del__(self):
        """Calls :py:meth:`shutdown` to properly shutdown the context."""
        self.shutdown()
        if self.session_factory is not None:
            self.session_factory.session.close()
        self._session_factory = None
        if self.ldap_session_factory is not None:
            self.ldap_session_factory.session.unbind()
        self._ldap_session_factory = None

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise NoObjectFoundException(object_name=key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    @property
    def session_factory(self) -> sf.SessionFactory:
        """Each context may have up to one instance of session factory -- access to
        your database connections.

        Returns:

            sf.SessionFactory: session factory instance.
        """
        if self._session_factory is None and self._session_provider is not None:
            with Context.lock:
                if not self._session_factory:
                    self._session_factory = sf.SessionFactory(self._session_provider)
        return self._session_factory

    @property
    def ldap_session_factory(self) -> lsf.LdapSessionFactory:
        """Each context may have up to one instance of LDAP session factory --
        access to your LDAP connections.

        Returns:

            lsf.LdapSessionFactory: LDAP session factory instance.
        """
        if self._ldap_session_factory is None and self._ldap_connection_provider is not None:
            with Context.lock:
                if not self._ldap_session_factory:
                    self._ldap_session_factory = lsf.LdapSessionFactory(self._ldap_connection_provider)
        return self._ldap_session_factory

    @property
    def l10n(self) -> l10n.Localization:
        """Each context may have up to one instance of
        :py:class:`l10n.Localization`.  You usually do not need to access
        it.

        Returns:

            l10n.Localization: localization instance.
        """
        return self._l10n

    def init(self):
        """Main context initialization method.

        Context initialization is executed from constructor; it is
        separated into several steps:

        #. call :py:meth:`core_init` (not indended to be overriden) which
           initializes core objects and internal AOP features

        #. call :py:meth:`orm_init` (intended to be overriden) which
           initializes ORM

        #. call :py:meth:`context_init` (intended to be overriden) -- a
           place to define your business beans
        """
        with Context.lock:
            logger.info("initializing core services")
            self.core_init()
            logger.info("core services initialized")

            logger.info("initializing orm")
            self.orm_init()
            logger.info("orm initialized")

            logger.info("custom context initialization started")
            self.context_init()
            logger.info("custom context initialization done")

            logger.info("context initialization done")

    def core_init(self):
        """Initializes core objects."""
        if self.session_factory is not None:
            logger.info("setting session_factory == %s", self.session_factory)
            from . import aop
            aop.__local_session_factory__ = self.session_factory

        if self.ldap_session_factory is not None:
            logger.info("setting ldap_session_factory == %s", self.ldap_session_factory)
            from . import aop
            aop.__local_ldap_session_factory__ = self.ldap_session_factory

        if self.l10n:
            logger.info("initializing l10n == %s", self.l10n)
            self.l10n.init()

    def orm_init(self):
        """Should be overriden by subclasses to initialize ORM managed tables and
        class mappings.

        You should define your custom table definitions based on
        :py:class:`summer.sf.AbstractTableDefinitions` and mappings based
        on :py:class:`summer.sf.AbstractClassMappings`.

        Usually you have just those lines there::

            self.session_factory.table_definitions = MyTableDefinitions()
            self.session_factory.set_class_mappings = MyClassMappings()
        """
        pass

    def context_init(self):
        """Should be overriden by subclasses to initialize custom objects in
        context.

        This is the last stage of context initialization, this method gets called after

        #. :py:meth:`core_init`
        #. :py:meth:`orm_init`

        are called.  You can safely access those properties:

        * :py:attr:`session_factory` (:py:class:`summer.sf.SessionFactory`
          instance) which provides thread-safe access to
          :py:class:`sqlalchemy.session` -- any data aware object (ie. each
          DAO at least) should probably have access to it -- at least those
          derived from :py:class:`dao.Dao` reference it.

        * :py:attr:`ldap_session_factory`
          (:py:class:`summer.lsf.LdapSessionFactory` instance) which
          provides thread-safe access to
          :py:class:`summer.lsf.LdapSessionFactory.Local` instance -- a
          simple wrapper around actual :py:class:`ldap3.Connection`

        * :py:attr:`l10n` (:py:class:`summer.l10n.Localization`) instance,
          not very interesting in itself, but summer's localization module
          installs the famous :py:meth:`_` gettext function into global
          namespace (as normal gettext module does) and configures your
          localization based on whatever you have provided
        """
        pass

    def shutdown(self):
        """Handles context shutdown.  Called from :py:meth:`__del__`.  Can be overriden."""
        pass
