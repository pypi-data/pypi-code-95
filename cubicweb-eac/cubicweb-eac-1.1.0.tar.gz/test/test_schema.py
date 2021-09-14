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
"""cubicweb-eac unit tests for schema"""

import sqlite3
import unittest
from datetime import date
from contextlib import contextmanager

from cubicweb import ValidationError, Unauthorized
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_compound.utils import optional_relations, graph_relations
from cubicweb_eac import testutils, AuthorityRecordGraph


@contextmanager
def assertValidationError(self, cnx):
    with self.assertRaises(ValidationError) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


class SchemaConstraintsTC(CubicWebTC):
    assertValidationError = assertValidationError

    def test_postaladdress_no_required(self):
        """Make sure a PostalAddress can be "empty" (useful in data import
        context).
        """
        with self.admin_access.cnx() as cnx:
            ar = testutils.authority_record(cnx, u"T-04", u"test")
            cnx.create_entity(
                "AgentPlace",
                place_agent=ar,
                place_address=cnx.create_entity("PostalAddress"),
            )
            cnx.commit()
            # No assert, just make sure db integrity checks pass.

    def test_on_create_set_end_date_before_start_date(self):
        """create an entity whose end_date is before start_date.
        ValidationError expected
        """
        with self.admin_access.cnx() as cnx:
            with self.assertValidationError(cnx) as cm:
                testutils.authority_record(
                    cnx,
                    u"T-04",
                    u"Arthur",
                    start_date=date(524, 2, 9),
                    end_date=date(500, 7, 12),
                )
            self.assertIn("must be less than", str(cm.exception))

    def test_on_update_set_end_date_before_start_date(self):
        """create a valid entity and update it with a new end_date set before the start_date.
        ValidationError expected
        """
        if sqlite3.sqlite_version_info < (3, 7, 12):
            # with sqlite earlier than 3.7.12, boundary constraints are not checked by the database,
            # hence the constraint is only triggered on start_date modification
            self.skipTest("unsupported sqlite version")
        with self.admin_access.cnx() as cnx:
            agent = testutils.authority_record(
                cnx,
                u"T-04",
                u"Arthur",
                start_date=date(454, 2, 9),
                end_date=date(475, 4, 12),
            )
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                agent.cw_set(end_date=date(442, 7, 12))
            self.assertIn("must be less than", str(cm.exception))

    def test_on_update_set_start_date_after_end_date(self):
        """create an entity without start_date :
        No constraint on the end_date
        update the entity with a start_date set after the start_date :
        ValidationError expected
        """
        with self.admin_access.cnx() as cnx:
            agent = testutils.authority_record(
                cnx, u"T-04", u"Arthur", end_date=date(476, 2, 9)
            )
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                agent.cw_set(start_date=date(527, 4, 12))
            self.assertIn("must be less than", str(cm.exception))


class AuthorityRecordGraphTC(CubicWebTC):
    def test_graph_structure(self):
        graph = AuthorityRecordGraph(self.schema)
        expected = {
            "AgentFunction": {("function_agent", "subject"): set(["AuthorityRecord"])},
            "AgentPlace": {("place_agent", "subject"): set(["AuthorityRecord"])},
            "Citation": {
                ("has_citation", "object"): set(
                    [
                        "GeneralContext",
                        "Mandate",
                        "Occupation",
                        "AgentFunction",
                        "AgentPlace",
                        "History",
                        "LegalStatus",
                        "Convention",
                        "Structure",
                    ]
                )
            },
            "DateEntity": {
                ("date_relation", "object"): set(
                    [
                        "HistoricalEvent",
                        "AgentFunction",
                        "EACFunctionRelation",
                        "LegalStatus",
                        "Mandate",
                        "NameEntry",
                        "Occupation",
                        "AgentPlace",
                        "EACResourceRelation",
                        "ParallelNames",
                    ]
                )
            },
            "PlaceEntry": {
                ("place_entry_relation", "object"): set(
                    [
                        "HistoricalEvent",
                        "AgentFunction",
                        "EACFunctionRelation",
                        "LegalStatus",
                        "Mandate",
                        "Occupation",
                        "AgentPlace",
                        "EACResourceRelation",
                    ]
                )
            },
            "EACFunctionRelation": {
                ("function_relation_agent", "subject"): set(["AuthorityRecord"])
            },
            "EACOtherRecordId": {
                ("eac_other_record_id_of", "subject"): set(["AuthorityRecord"])
            },
            "EACResourceRelation": {
                ("resource_relation_agent", "subject"): set(["AuthorityRecord"])
            },
            "Convention": {("convention_of", "subject"): set(["AuthorityRecord"])},
            "EACSource": {("source_agent", "subject"): set(["AuthorityRecord"])},
            "HistoricalEvent": {("has_event", "object"): set(["History"])},
            "GeneralContext": {
                ("general_context_of", "subject"): set(["AuthorityRecord"])
            },
            "History": {("history_agent", "subject"): set(["AuthorityRecord"])},
            "LegalStatus": {
                ("legal_status_agent", "subject"): set(["AuthorityRecord"])
            },
            "Mandate": {("mandate_agent", "subject"): set(["AuthorityRecord"])},
            "NameEntry": {
                ("name_entry_for", "subject"): set(["AuthorityRecord"]),
                ("simple_name_relation", "object"): set(["ParallelNames"]),
            },
            "Occupation": {("occupation_agent", "subject"): set(["AuthorityRecord"])},
            "ParallelNames": {
                ("parallel_names_of", "subject"): set(["AuthorityRecord"])
            },
            "PostalAddress": {("place_address", "object"): set(["AgentPlace"])},
            "Structure": {("structure_agent", "subject"): set(["AuthorityRecord"])},
        }
        struct = dict(
            (k, dict((rel, set(targets)) for rel, targets in v.items()))
            for k, v in graph.parent_structure("AuthorityRecord").items()
        )
        self.assertEqual(struct, expected)

    def test_optional_relations(self):
        graph = AuthorityRecordGraph(self.schema)
        structure = graph.parent_structure("AuthorityRecord")
        opts = optional_relations(self.schema, structure)
        expected = {
            "NameEntry": set(
                [("name_entry_for", "subject"), ("simple_name_relation", "object")]
            )
        }
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = AuthorityRecordGraph(self.schema)
        structure = graph.parent_structure("AuthorityRecord")
        structurals, optionals, mandatories = graph_relations(self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)


class SecurityTC(CubicWebTC):
    """Test case for permissions set in the schema"""

    @contextmanager
    def assertUnauthorized(self, cnx):
        with self.assertRaises(Unauthorized) as cm:
            yield cm
            cnx.commit()
        cnx.rollback()

    def test_agentkind_type(self):
        with self.admin_access.cnx() as cnx:
            kind = cnx.find("AgentKind", name=u"person").one()
            # no one can update nor delete a kind
            with self.assertUnauthorized(cnx):
                kind.cw_set(name=u"gloups")
            with self.assertUnauthorized(cnx):
                kind.cw_delete()

        with self.admin_access.cnx() as cnx:
            with self.assertUnauthorized(cnx):
                cnx.create_entity("AgentKind", name=u"new")

    def test_agent_kind_relation(self):
        """Test we can only change kind from unknown to another."""
        with self.admin_access.cnx() as cnx:
            record = testutils.authority_record(
                cnx, u"T-02", u"bob", kind=u"unknown-agent-kind"
            )
            cnx.commit()
            record.cw_set(agent_kind=cnx.find("AgentKind", name=u"person").one())
            cnx.commit()
            with self.assertRaises(Unauthorized):
                record.cw_set(agent_kind=cnx.find("AgentKind", name=u"authority").one())

    def test_authority_record_base(self):
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, login=u"toto", groups=("users", "guests"))
            function = cnx.create_entity("AgentFunction", name=u"director")
            testutils.authority_record(
                cnx, u"T-00", u"admin record", reverse_function_agent=function
            )
            cnx.commit()

        with self.new_access("toto").cnx() as cnx:
            # user can create and modify its own records
            function = cnx.create_entity("AgentFunction", name=u"grouillot")
            record = testutils.authority_record(
                cnx, u"T-02", u"bob", reverse_function_agent=function
            )
            cnx.commit()
            function.cw_set(name=u"grouyo")
            cnx.commit()
            cnx.create_entity(
                "GeneralContext", content=u"plop", general_context_of=record
            )
            cnx.commit()
            # but not modify other's
            record = cnx.find("AuthorityRecord", has_text=u"admin record").one()
            with self.assertUnauthorized(cnx):
                record.cw_set(record_id=u"bobby")
            with self.assertUnauthorized(cnx):
                record.reverse_function_agent[0].cw_set(name=u"grouillot")
            with self.assertUnauthorized(cnx):
                function = cnx.create_entity("AgentFunction", name=u"grouillot")
                record.cw_set(reverse_function_agent=function)


if __name__ == "__main__":
    unittest.main()
