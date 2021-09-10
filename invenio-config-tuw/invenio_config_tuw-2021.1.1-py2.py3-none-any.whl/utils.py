# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions."""

from flask_principal import Identity
from invenio_access import any_user
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts
from invenio_userprofiles.models import UserProfile


def get_user_by_username(username):
    """Get the user identified by the username."""
    profile = UserProfile.query.filter(UserProfile.username == username).one_or_none()

    if profile is not None:
        return profile.user

    return None


def get_user(identifier):
    """Get the user identified by the given ID, email or username."""
    user = current_accounts.datastore.get_user(identifier)
    if user is None:
        get_user_by_username(identifier)

    return user


def get_identity_for_user(user):
    """Get the Identity for the user specified via email, ID or username."""
    identity = None
    if user is not None:
        # note: this seems like the canonical way to go
        #       'as_user' can be either an integer (id) or email address
        u = get_user(user)
        if u is not None:
            identity = get_identity(u)
        else:
            raise LookupError("user not found: %s" % user)

    if identity is None:
        identity = Identity(1)

    identity.provides.add(any_user)
    return identity
