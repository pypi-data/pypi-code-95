# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import warnings
from abc import ABC
from abc import abstractmethod
from collections import OrderedDict

from flask import current_app
from sqlalchemy.exc import IntegrityError

from kadi.ext.db import db
from kadi.lib.utils import get_class_by_name
from kadi.modules.accounts.models import User
from kadi.modules.permissions.core import set_system_role


class AuthProviderBase(ABC):
    """Base class for authentication providers.

    Each provider should override :meth:`register` and :meth:`authenticate` and specify
    its meta attributes in :class:`Meta`. Those methods should return an identity object
    subclassing :class:`.Identity` or a :class:`UserInfo` object respectively. If
    passwords are allowed to be changed by users, :meth:`allow_password_change` and
    :meth:`change_password` need to be overridden as well, returning a boolean value
    indicating whether passwords can be changed and whether the change was successful
    repectively.

    The function :func:`init_auth_providers` needs to be called beforehand to initialize
    the application's configuration for use with the registered authentication
    providers.
    """

    class Meta:
        """Container to store meta class attributes."""

        provider_type = {"type": None, "name": None}
        """The type and full name of a provider."""

        defaults = {}
        """The default configuration values of a provider.

        Each provider should at least specify a ``title`` alongside all other
        provider-specific configuration.
        """

    class UserInfo:
        """Wrapper class to store user information.

        Should be returned by :meth:`authenticate`.

        :param is_authenticated: Flag to indicate if the represented user is
            authenticated or not.
        :param data: (optional) The wrapped user data. This should generally be an
            object-like type representing the user information or the actual user.
        """

        def __init__(self, is_authenticated, data=None):
            self.is_authenticated = is_authenticated
            self.data = data

    @classmethod
    def _create_identity(cls, *, system_role, identity_model, **kwargs):
        user = User.create()

        if not set_system_role(user, system_role):
            return None

        identity = identity_model.create(user=user, **kwargs)

        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return None

        user.identity = identity
        return identity

    @classmethod
    def _set_defaults(cls, app):
        auth_providers = app.config["AUTH_PROVIDERS"]
        config = auth_providers.get(cls.Meta.provider_type["type"])

        for key, value in cls.Meta.defaults.items():
            if key not in config:
                config[key] = value

    @classmethod
    def is_registered(cls):
        """Check if a provider is registered in the application.

        :return: ``True`` if the provider is registered, ``False`` otherwise.
        """
        auth_providers = current_app.config["AUTH_PROVIDERS"]
        return cls.Meta.provider_type["type"] in auth_providers

    @classmethod
    def get_config(cls):
        """Get a provider's config from the current application object.

        :return: The provider's configuration dictionary.
        """
        auth_providers = current_app.config["AUTH_PROVIDERS"]
        return auth_providers.get(cls.Meta.provider_type["type"])

    @classmethod
    def allow_password_change(cls):
        """Check whether a provider supports changing passwords.

        :return: Flag indicating whether the provider supports changing passwords.
        """
        return False

    @classmethod
    @abstractmethod
    def register(cls, **kwargs):
        # pylint: disable=missing-function-docstring
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def authenticate(cls, **kwargs):
        # pylint: disable=missing-function-docstring
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def change_password(cls, username, old_password, new_password):
        """Change a password of an existing user if supported by a provider.

        :param username: The unique username of the user.
        :param old_password: The current password of the user.
        :param new_password: The new password of the user.
        :return: A boolean value indicating whether the password change was successful.
        :raises NotImplementedError: If changing a user's password is not supported by
            the provider.
        """
        raise NotImplementedError


def init_auth_providers(app):
    """Initialize all authentication providers for use in the application.

    Makes use of the ``AUTH_PROVIDER_TYPES`` and ``AUTH_PROVIDERS`` specified in the
    application's configuration. Additionally, the ``AUTH_PROVIDERS`` configuration will
    be modified to use an ordered dictionary instead and will also include references to
    the provider and identity classes as specified in ``AUTH_PROVIDER_TYPES`` for
    convenient access, using the keys ``"provider_class"`` and ``"identity_class"``
    respectively.

    :param app: The application object.
    """
    auth_providers = app.config["AUTH_PROVIDERS"]
    auth_provider_types = app.config["AUTH_PROVIDER_TYPES"]

    # Rebuild the configuration using an ordered dict including additional metadata.
    app.config["AUTH_PROVIDERS"] = OrderedDict()

    for config in auth_providers:
        provider_type = config.get("type")
        if provider_type not in auth_provider_types:
            warnings.warn(f"The provider type '{provider_type}' does not exist.")
            continue

        auth_classes = auth_provider_types.get(provider_type, {})

        provider_class = get_class_by_name(auth_classes.get("provider", ""))
        config["provider_class"] = provider_class
        if provider_class is None:
            continue

        identity_class = get_class_by_name(auth_classes.get("identity", ""))
        config["identity_class"] = identity_class
        if identity_class is None:
            continue

        form_class = get_class_by_name(auth_classes.get("form", ""))
        config["form_class"] = form_class
        if form_class is None:
            continue

        app.config["AUTH_PROVIDERS"][provider_type] = config

        provider_class._set_defaults(app)
