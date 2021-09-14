from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_eac import testutils


class TernaryRelationDeletionHookTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.arecord1_eid = testutils.authority_record(cnx, u"T-01", u"alice").eid
            self.arecord2_eid = testutils.authority_record(cnx, u"T-02", u"bob").eid
            self.arecord3_eid = testutils.authority_record(cnx, u"T-03", u"charles").eid
            cnx.create_entity(
                "AssociationRelation",
                entry=u"alice and bob are friends",
                association_from=self.arecord1_eid,
                association_to=self.arecord2_eid,
            )
            cnx.create_entity(
                "AssociationRelation",
                entry=u"bob knows charles",
                association_from=self.arecord2_eid,
                association_to=self.arecord3_eid,
            )
            cnx.create_entity(
                "ChronologicalRelation",
                entry=u"alice is bob's mother",
                chronological_predecessor=self.arecord1_eid,
                chronological_successor=self.arecord2_eid,
            )
            cnx.commit()

    def test(self):
        with self.admin_access.cnx() as cnx:
            with self.assertLogs("cubicweb.hook", level="INFO") as cm:
                cnx.execute(
                    "DELETE AuthorityRecord X WHERE X eid %(x)s",
                    {"x": self.arecord2_eid},
                )
            expected_msgs = [
                'deleting "alice and bob are friends" as association_to-object is being deleted',
                'deleting "bob knows charles" as association_from-object is being deleted',
                'deleting "alice is bob\'s mother" as chronological_successor-object is being deleted',  # noqa: E501
            ]
            self.assertCountEqual([r.message for r in cm.records], expected_msgs)
            cnx.commit()
            rset = cnx.find("AssociationRelation")
            self.assertFalse(rset)

    def test_unauthorized(self):
        with self.admin_access.cnx() as cnx:
            with self.temporary_permissions(
                AssociationRelation={"delete": ()}, ChronologicalRelation={"delete": ()}
            ):
                with self.assertRaises(ValidationError) as cm:
                    cnx.execute(
                        "DELETE AuthorityRecord X WHERE X eid %(x)s",
                        {"x": self.arecord2_eid},
                    )
        errors = str(cm.exception).splitlines()[1:]  # first line contain entity's eid.
        expected_msgs = [
            '* chronological_successor: "alice is bob\'s mother" would need to be deleted alongside the AuthorityRecord but this is disallowed',  # noqa: E501
            '* association_to: "alice and bob are friends" would need to be deleted alongside the AuthorityRecord but this is disallowed',  # noqa: E501
            '* association_from: "bob knows charles" would need to be deleted alongside the AuthorityRecord but this is disallowed',  # noqa: E501
        ]
        self.assertCountEqual(errors, expected_msgs)


if __name__ == "__main__":
    import unittest

    unittest.main()
