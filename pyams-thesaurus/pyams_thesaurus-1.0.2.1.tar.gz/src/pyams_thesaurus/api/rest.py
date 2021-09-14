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

"""PyAMS_thesaurus.api.rest module

Thesaurus REST API module.
"""

import sys

from colander import MappingSchema, SchemaNode, SequenceSchema, String, drop
from cornice import Service
from cornice.validators import colander_querystring_validator
from hypatia.text import ParseError
from pyramid.httpexceptions import HTTPOk

from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_thesaurus.interfaces import REST_TERMS_SEARCH_ROUTE


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _
from pyams_thesaurus.interfaces.term import STATUS_ARCHIVED
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_utils.list import unique
from pyams_utils.registry import query_utility


TEST_MODE = sys.argv[-1].endswith('/test')


class ThesaurusTermsSearchQuerySchema(MappingSchema):
    """Thesaurus terms search schema"""
    thesaurus_name = SchemaNode(String(),
                                description=_("Selected thesaurus name"))
    extract_name = SchemaNode(String(),
                              description=_("Selected extract name"),
                              missing=drop)
    term = SchemaNode(String(),
                      description=_("Terms search string"))


class ThesaurusTermResultSchema(MappingSchema):
    """Thesaurus term result schema"""
    id = SchemaNode(String(),
                    description=_("Term ID"))
    text = SchemaNode(String(),
                      description=_("Term label"))


class ThesaurusSearchResults(SequenceSchema):
    """Thesaurus search results interface"""
    result = ThesaurusTermResultSchema()


class ThesaurusSearchResultsSchema(MappingSchema):
    """Thesaurus search results schema"""
    results = ThesaurusSearchResults(description=_("Results list"))


search_response = {
    HTTPOk.code: ThesaurusSearchResultsSchema(description=_("Search results"))
}
if TEST_MODE:
    service_params = {}
else:
    service_params = {
        'response_schemas': search_response
    }


service = Service(name=REST_TERMS_SEARCH_ROUTE,
                  pyramid_route=REST_TERMS_SEARCH_ROUTE,
                  description="Thesaurus terms management")


@service.get(permission=VIEW_SYSTEM_PERMISSION,
             schema=ThesaurusTermsSearchQuerySchema(),
             validators=(colander_querystring_validator,),
             **service_params)
def get_terms(request):
    """Returns list of terms matching given query"""
    if TEST_MODE:
        thesaurus_name = request.params.get('thesaurus_name')
        extract_name = request.params.get('extract_name')
        query = request.params.get('term')
    else:
        thesaurus_name = request.validated.get('thesaurus_name')
        extract_name = request.validated.get('extract_name')
        query = request.validated.get('term')
    if not (thesaurus_name or query):
        return {}
    thesaurus = query_utility(IThesaurus, name=thesaurus_name)
    if thesaurus is None:
        return {}
    try:
        return {
            'results': [
                {
                    'id': term.label,
                    'text': term.label
                }
                for term in unique(thesaurus.find_terms(query, extract_name,
                                                        exact=True, stemmed=True))
                if term.status != STATUS_ARCHIVED
            ]
        }
    except ParseError:
        return []
