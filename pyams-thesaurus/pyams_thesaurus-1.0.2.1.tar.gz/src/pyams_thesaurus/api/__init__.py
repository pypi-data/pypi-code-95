#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_thesaurus.api main module

This module provides terms search function.
"""

__docformat__ = 'restructuredtext'

from hypatia.text import ParseError
from pyramid.view import view_config

from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_thesaurus.interfaces.term import STATUS_ARCHIVED
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_utils.list import unique
from pyams_utils.registry import query_utility


@view_config(name='find-terms.json',
             permission=VIEW_SYSTEM_PERMISSION,
             renderer='json', xhr=True)
def find_terms(request):
    """Find terms matching given query"""
    thesaurus_name = request.params.get('thesaurus_name')
    thesaurus = query_utility(IThesaurus, name=thesaurus_name)
    if thesaurus is None:
        return []
    query = request.params.get('term')
    extract_name = request.params.get('extract_name')
    try:
        return [
            {
                'id': term.label,
                'text': term.label
            }
            for term in thesaurus.find_terms(query, extract_name, exact=True, stemmed=True)
            if term.status != STATUS_ARCHIVED
        ]
    except ParseError:
        return []
