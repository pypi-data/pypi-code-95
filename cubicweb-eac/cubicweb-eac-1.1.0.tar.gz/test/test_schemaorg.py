# copyright 2015-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-eac test for views."""

import datetime
import unittest

from rdflib import ConjunctiveGraph, Graph
from rdflib.compare import graph_diff

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.rdf import add_entity_to_graph

from cubicweb_eac import testutils


class AuthorityRecordRdfTC(CubicWebTC):
    def compare_graphs(self, graph, eid, target_ttl_file_name):
        with open(self.datapath(target_ttl_file_name), "r") as f:
            target_graph = Graph().parse(
                data=f.read().replace("{{eid}}", str(eid)), format="ttl"
            )
            common, tested_only, target_only = graph_diff(graph, target_graph)
            self.assertEqual(len(tested_only), 0)
            self.assertEqual(len(target_only), 0)

    def test_person_authority(self):
        with self.admin_access.repo_cnx() as cnx:
            copain = testutils.authority_record(cnx, u"B123", "Toto")
            copine = testutils.authority_record(cnx, u"B243", "Titi")
            entity = testutils.authority_record(
                cnx,
                u"A123",
                u"Jean Jacques",
                kind=u"person",
                start_date=datetime.date(2010, 1, 1),
                end_date=datetime.date(2050, 5, 2),
                reverse_occupation_agent=cnx.create_entity(
                    "Occupation", term="fan de poules"
                ),
                reverse_history_agent=cnx.create_entity(
                    "History", text="<p>loutre gentille<p>", text_format="text/html"
                ),
                reverse_family_from=(
                    cnx.create_entity("FamilyRelation", family_to=copain, entry="Toto"),
                    cnx.create_entity("FamilyRelation", family_to=copine, entry="Titi"),
                ),
            )
            cnx.commit()
            graph = ConjunctiveGraph()
            add_entity_to_graph(graph, entity)
            self.compare_graphs(graph, entity.eid, "person_rdf.ttl")

    def test_organization_authority(self):
        with self.admin_access.repo_cnx() as cnx:
            parent_organization = testutils.authority_record(
                cnx, u"B123", "Toto Cie", kind="authority"
            )
            child_organization = testutils.authority_record(
                cnx, u"B243", "Titi Cie", kind="authority"
            )
            entity = testutils.authority_record(
                cnx,
                u"A123",
                u"Entreprise",
                kind=u"authority",
                start_date=datetime.date(2010, 1, 1),
                end_date=datetime.date(2050, 5, 2),
            )
            cnx.create_entity(
                "HierarchicalRelation",
                hierarchical_child=(child_organization),
                hierarchical_parent=(entity),
                entry="Titi Cie",
            )
            cnx.create_entity(
                "HierarchicalRelation",
                hierarchical_child=(entity),
                hierarchical_parent=(parent_organization),
                entry="Titi Cie",
            )
            cnx.commit()
            graph = ConjunctiveGraph()
            add_entity_to_graph(graph, entity)
            self.compare_graphs(graph, entity.eid, "organization_rdf.ttl")


if __name__ == "__main__":
    unittest.main()
