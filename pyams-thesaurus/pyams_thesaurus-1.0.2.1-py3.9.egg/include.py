#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS thesaurus.include module

This module is used for Pyramid integration.
"""

import re

from pyams_security.interfaces import ADMIN_USER_ID, SYSTEM_ADMIN_ROLE
from pyams_security.interfaces.base import ROLE_ID
from pyams_thesaurus.interfaces import ADMIN_THESAURUS_PERMISSION, CREATE_THESAURUS_PERMISSION, \
    MANAGE_THESAURUS_CONTENT_PERMISSION, MANAGE_THESAURUS_EXTRACT_PERMISSION, \
    REST_TERMS_SEARCH_ROUTE, THESAURUS_ADMIN_ROLE, THESAURUS_EXTRACT_MANAGER_ROLE, \
    THESAURUS_MANAGER_ROLE


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_thesaurus:locales')

    # register permissions
    config.register_permission({
        'id': CREATE_THESAURUS_PERMISSION,
        'title': _("Create thesaurus")
    })
    config.register_permission({
        'id': ADMIN_THESAURUS_PERMISSION,
        'title': _("Manage thesaurus properties")
    })
    config.register_permission({
        'id': MANAGE_THESAURUS_CONTENT_PERMISSION,
        'title': _("Manage thesaurus content")
    })
    config.register_permission({
        'id': MANAGE_THESAURUS_EXTRACT_PERMISSION,
        'title': _("Manage thesaurus extract")
    })

    # upgrade system manager role
    config.upgrade_role(SYSTEM_ADMIN_ROLE,
                        permissions={
                            ADMIN_THESAURUS_PERMISSION,
                            MANAGE_THESAURUS_CONTENT_PERMISSION,
                            MANAGE_THESAURUS_EXTRACT_PERMISSION
                        })

    # register roles
    config.register_role({
        'id': THESAURUS_ADMIN_ROLE,
        'title': _("Thesaurus administrator (role)"),
        'permissions': {
            ADMIN_THESAURUS_PERMISSION,
            MANAGE_THESAURUS_CONTENT_PERMISSION,
            MANAGE_THESAURUS_EXTRACT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': THESAURUS_MANAGER_ROLE,
        'title': _("Thesaurus content manager (role)"),
        'permissions': {
            MANAGE_THESAURUS_CONTENT_PERMISSION,
            MANAGE_THESAURUS_EXTRACT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(THESAURUS_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': THESAURUS_EXTRACT_MANAGER_ROLE,
        'title': _("Thesaurus extract manager (role)"),
        'permissions': {
            MANAGE_THESAURUS_EXTRACT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(THESAURUS_ADMIN_ROLE)
        }
    })

    # register REST API routes
    config.add_route(REST_TERMS_SEARCH_ROUTE,
                     config.registry.settings.get('pyams.thesaurus.rest_terms_route',
                                                  '/api/thesaurus/terms'))

    # test Venusian scans
    ignored = []

    try:
        import pyams_zmi  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        ignored.append(re.compile(r'pyams_thesaurus\..*\.zmi\.?.*').search)
    else:
        if not config.registry.settings.get('pyams_thesaurus.include_tests_features', False):
            ignored.append('pyams_thesaurus.zmi.test')

    config.scan(ignore=ignored)
