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

import unittest

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web.views.actions import CopyAction

from cubicweb_eac import testutils


class FuncViewsTC(CubicWebTC):
    def test_import_ok(self):
        regid = "eac.import"
        fname = "FRAD033_EAC_00001_simplified.xml"
        with self.admin_access.web_request() as req:
            # simply test the form properly render and is well formed
            self.view(regid, req=req, template=None)
            fields = {"file": (fname, open(self.datapath(fname), "rb"))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            req.view(regid)
            # several authority records are created (the main one + other for relations)
            self.assertTrue(req.find("AuthorityRecord"))

    def test_import_non_unique_isni(self):
        regid = "eac.import"
        fname = "FRAD033_EAC_00001_simplified.xml"
        with self.admin_access.client_cnx() as cnx:
            # ISNI is the same as the agent in EAC file.
            testutils.authority_record(cnx, u"T-02", u"bob", isni=u"22330001300016")
            cnx.commit()
        with self.admin_access.web_request() as req:
            # simply test the form properly render and is well formed
            self.view(regid, req=req, template=None)
            fields = {"file": (fname, open(self.datapath(fname), "rb"))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn("EAC import failed", html)
            # Still only one AuthorityRecord.
            rset = req.find("AuthorityRecord")
            self.assertEqual(len(rset), 1)

    def test_import_invalid_xml(self):
        regid = "eac.import"
        fname = "invalid_xml.xml"
        with self.admin_access.web_request() as req:
            fields = {"file": (fname, open(self.datapath(fname), "rb"))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn("Invalid XML file", html)

    def test_import_missing_tag(self):
        regid = "eac.import"
        fname = "missing_tag.xml"
        with self.admin_access.web_request() as req:
            fields = {"file": (fname, open(self.datapath(fname), "rb"))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn("Missing tag cpfDescription in XML file", html)

    def test_export_filename(self):
        with self.admin_access.web_request() as req:
            cnx = req.cnx
            record = testutils.authority_record(cnx, u"T-07", u"jim")
            for isni, expected_filename in (
                (u"", "EAC_{0}.xml".format(record.eid)),
                (u"ZZZ/4242", "EAC_ZZZ_4242.xml"),
            ):
                record.cw_set(isni=isni)
                view = self.vreg["views"].select("eac.export", req, record.as_rset())
                view.set_request_content_type()
                self.assertEqual(
                    view._cw.headers_out.getRawHeaders("content-disposition"),
                    ['attachment;filename="{0}"'.format(expected_filename)],
                )

    def test_xmlwrap_component(self):
        with self.admin_access.cnx() as cnx:
            bob = testutils.authority_record(cnx, u"T-02", u"bob")
            uri = cnx.create_entity("ExternalUri", uri=u"http://logilab.fr")
            cnx.create_entity(
                "EACResourceRelation",
                resource_relation_agent=bob,
                resource_relation_resource=uri,
                xml_wrap=Binary(b"<plip>plop</plip>"),
            )
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.find("EACResourceRelation")
            component = self.vreg["ctxcomponents"].select(
                "eac.xml_wrap", req, rset=rset
            )
            content = []
            component.render_body(content.append)
        self.assertIn(u"plop", content[0])
        self.assertEqual(content[0].count(u"plip"), 2)


class AuthorityRecordFormsTC(CubicWebTC):
    def test_no_copy_action(self):
        with self.admin_access.cnx() as cnx:
            testutils.authority_record(cnx, u"T-06", u"toto")
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.execute('Any X WHERE N name_entry_for X, N parts "toto"')
            actions = self.pactionsdict(req, rset)
            self.assertNotIn(CopyAction, actions["moreactions"])

    def test_unrelated_authorityrecord(self):
        from cubicweb_eac.views import unrelated_authorityrecord

        with self.admin_access.cnx() as cnx:
            ar1 = testutils.authority_record(cnx, u"T-1", u"1").eid
            ar2 = testutils.authority_record(cnx, u"T-2", u"2").eid
            # ExternalUri should not appear in choices.
            cnx.create_entity("ExternalUri", uri=u"http://no-where")
            cnx.commit()
        with self.admin_access.web_request() as req:
            cls = self.vreg["etypes"].etype_class("HierarchicalRelation")(req)
            form = self.vreg["forms"].select("edition", req, entity=cls)
            field = form.field_by_name("hierarchical_parent", "subject")
            choices = unrelated_authorityrecord("hierarchical_parent", form, field)
            expected = [(u"1", str(ar1)), (u"2", str(ar2))]
            self.assertCountEqual(choices, expected)
        # Now with a __linkto.
        linkto = "hierarchical_parent:{0}:subject".format(ar2)
        with self.admin_access.web_request(__linkto=linkto) as req:
            cls = self.vreg["etypes"].etype_class("HierarchicalRelation")(req)
            form = self.vreg["forms"].select("edition", req, entity=cls)
            field = form.field_by_name("hierarchical_parent", "subject")
            choices = unrelated_authorityrecord("hierarchical_parent", form, field)
            expected = [(u"2", str(ar2))]
            self.assertCountEqual(choices, expected)
            field = form.field_by_name("hierarchical_child", "subject")
            choices = unrelated_authorityrecord("hierarchical_child", form, field)
            expected = [(u"1", str(ar1)), (u"2", str(ar2))]
            self.assertCountEqual(choices, expected)


if __name__ == "__main__":
    unittest.main()
