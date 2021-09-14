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

"""PyAMS_thesaurus.interfaces main module

This module defines permissions, roles and vocabulary names.
"""


CREATE_THESAURUS_PERMISSION = 'pyams_thesaurus.CreateThesaurus'
'''Permission to create thesaurus'''

ADMIN_THESAURUS_PERMISSION = 'pyams_thesaurus.AdminThesaurus'
'''Permission to administer all thesaurus properties'''

MANAGE_THESAURUS_CONTENT_PERMISSION = 'pyams_thesaurus.ManageThesaurusContent'
'''Permission to manage thesaurus contents'''

MANAGE_THESAURUS_EXTRACT_PERMISSION = 'pyams_thesaurus.ManageThesaurusExtract'
'''Permission to manage thesaurus extract contents'''


THESAURUS_ADMIN_ROLE = 'pyams_thesaurus.Admin'
'''Thesaurus admin is allowed to manage all thesaurus properties'''

THESAURUS_MANAGER_ROLE = 'pyams_thesaurus.Manager'
'''Thesaurus manager is allowed to manage thesaurus terms and extracts'''

THESAURUS_EXTRACT_MANAGER_ROLE = 'pyams_thesaurus.ExtractManager'
'''Thesaurus extract manager is allowed to manage content of a thesaurus extract'''


REST_TERMS_SEARCH_ROUTE = 'thesaurus.rest.terms'
'''Thesaurus terms search route'''


THESAURUS_VOCABULARY = 'pyams_thesaurus.thesaurus'
THESAURUS_NAMES_VOCABULARY = 'pyams_thesaurus.thesaurus.names'
THESAURUS_EXTRACTS_VOCABULARY = 'pyams_thesaurus.extracts'
