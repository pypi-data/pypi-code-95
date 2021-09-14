# coding: utf-8
# copyright 2021-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from rdflib.term import Literal

from cubicweb.predicates import is_instance
from cubicweb.entities.adapters import EntityRDFAdapter
from cubicweb.uilib import remove_html_tags


class AuthorityRecordRDFAdapter(EntityRDFAdapter):
    __select__ = EntityRDFAdapter.__select__ & is_instance("AuthorityRecord")

    def names_triples(self):
        SCHEMA = self._use_namespace("schema")
        entity = self.entity
        for name_entry in entity.reverse_name_entry_for:
            if name_entry.parts:
                yield (self.uri, SCHEMA.name, Literal(name_entry.parts))

    def person_triples(self):
        SCHEMA = self._use_namespace("schema")
        RDF = self._use_namespace("rdf")
        entity = self.entity
        yield (self.uri, RDF.type, SCHEMA.Person)
        if entity.start_date:
            yield (
                self.uri,
                SCHEMA.birthDate,
                Literal(entity.start_date.strftime("%Y-%m-%d")),
            )
        if entity.end_date:
            yield (
                self.uri,
                SCHEMA.deathDate,
                Literal(entity.end_date.strftime("%Y-%m-%d")),
            )
        if entity.reverse_occupation_agent:
            yield (
                self.uri,
                SCHEMA.hasOccupation,
                Literal(entity.reverse_occupation_agent[0].term),
            )
        if entity.reverse_history_agent:
            yield (
                self.uri,
                SCHEMA.description,
                Literal(remove_html_tags(entity.reverse_history_agent[0].text)),
            )
        for family_member in entity.reverse_family_from:
            yield (self.uri, SCHEMA.relatedTo, Literal(family_member.entry))

    def organization_triples(self):
        SCHEMA = self._use_namespace("schema")
        RDF = self._use_namespace("rdf")
        entity = self.entity
        yield (self.uri, RDF.type, SCHEMA.Organization)
        if entity.start_date:
            yield (
                self.uri,
                SCHEMA.foundingDate,
                Literal(entity.start_date.strftime("%Y-%m-%d")),
            )
        if entity.end_date:
            yield (
                self.uri,
                SCHEMA.dissolutionDate,
                Literal(entity.end_date.strftime("%Y-%m-%d")),
            )

        for parent_of_relation in entity.reverse_hierarchical_parent:
            yield (
                self.uri,
                SCHEMA.subOrganization,
                Literal(parent_of_relation.hierarchical_child[0].dc_title()),
            )

        for child_of_relation in entity.reverse_hierarchical_child:
            yield (
                self.uri,
                SCHEMA.parentOrganization,
                Literal(child_of_relation.hierarchical_parent[0].dc_title()),
            )

    def triples(self):
        SCHEMA = self._use_namespace("schema")
        entity = self.entity
        yield (self.uri, SCHEMA.url, Literal(self.uri))
        yield from self.names_triples()

        for identity_relation in entity.reverse_identity_from:
            same_as_entity = identity_relation.identity_to[0]
            if same_as_entity.cw_etype == "ExternalUri":
                yield (self.uri, SCHEMA.sameAs, Literal(same_as_entity.uri))
            else:
                same_as_uri = same_as_entity.cw_adapt_to("rdf").uri
                yield (self.uri, SCHEMA.sameAs, Literal(same_as_uri))
        if entity.agent_kind:
            if entity.agent_kind[0].name == "person":
                yield from self.person_triples()
            else:
                yield from self.organization_triples()
