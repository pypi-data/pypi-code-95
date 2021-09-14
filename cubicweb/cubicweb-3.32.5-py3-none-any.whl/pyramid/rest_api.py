# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2014-2016 UNLISH S.A.S. (Montpellier, FRANCE), all rights reserved.
#
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <https://www.gnu.org/licenses/>.

"""Experimental REST API for CubicWeb using Pyramid."""

import rdflib

from pyramid.view import view_config
from pyramid.response import Response

from cubicweb import rdf
from cubicweb.pyramid.resources import rdf_context_from_eid, RDFResource


@view_config(
    route_name="one_entity",
    context=RDFResource,
)
@view_config(
    route_name="one_entity_eid",
    context=RDFResource,
)
def view_entity_as_rdf(context, request):
    graph = rdflib.ConjunctiveGraph()
    rdf.add_entity_to_graph(graph, context.entity)
    rdf_format = rdf.RDF_MIMETYPE_TO_FORMAT[context.mime_type]
    response = Response(graph.serialize(format=rdf_format))
    response.content_type = context.mime_type
    return response


def includeme(config):
    config.include(".predicates")
    config.add_route(
        "one_entity",
        "/{etype}/{eid}",
        factory=rdf_context_from_eid,
        match_is_etype_and_eid=("etype", "eid"),
    )
    config.add_route(
        "one_entity_eid", "/{eid}", factory=rdf_context_from_eid, match_is_eid="eid"
    )
    config.scan(__name__)
