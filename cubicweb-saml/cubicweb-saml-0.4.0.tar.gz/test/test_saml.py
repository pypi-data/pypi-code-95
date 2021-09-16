# copyright 2019-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from mock import patch
from pyramid import testing

from cubicweb import ValidationError, NoResultError
from cubicweb.devtools import testlib

from cubicweb_saml.utils import (build_base_url,
                                 execute_rql,
                                 find_group_by_name,
                                 find_user_by_login,
                                 generate_hash,
                                 get_user,
                                 register_user,
                                 register_user_into_db)


class _SAMLCommonTC(testlib.CubicWebTC):

    def setUp(self):
        super(_SAMLCommonTC, self).setUp()

        self.request = testing.DummyRequest(post={'SAMLResponse': ''})
        self.request.registry['cubicweb.config'] = self.config
        self.request.registry['cubicweb.repository'] = self.repo


class SAMLUtilsTC(_SAMLCommonTC):

    def test_build_base_url(self):
        config = self.vreg.config

        self.assertEqual(
            build_base_url(config), 'http://testing.fr/cubicweb/')

        config['base-url'] = 'http://url.without.backslash'

        self.assertEqual(
            build_base_url(config), 'http://url.without.backslash/')

    def test_generate_hash(self):
        self.assertNotEqual(generate_hash('example'),
                            generate_hash('example'))

        self.assertIsNotNone(generate_hash('example', 'with', 'arguments'))


class SAMLDatabaseTC(_SAMLCommonTC):

    def test_execute_rql(self):
        with self.admin_access.repo_cnx() as cnx:
            self.assertIsNone(execute_rql(
                cnx,
                "Any U WHERE U is CWUser, U login %(login)s",
                login="CubicWeb"))

            rset = execute_rql(cnx, "Any U WHERE U is CWUser, U login 'admin'")
            self.assertIsInstance(rset, int)
            self.assertEqual(rset, 6)

    def test_find_user_by_login(self):
        with self.admin_access.repo_cnx() as cnx:
            user_eid = register_user_into_db(cnx, "test", "managers", "psswd")

            find_eid = find_user_by_login(cnx, "test")
            self.assertEqual(user_eid, find_eid)

    def test_find_group_by_name(self):
        with self.admin_access.repo_cnx() as cnx:
            self.assertIsNotNone(find_group_by_name(cnx, "managers"))
            self.assertIsNotNone(find_group_by_name(cnx, "users"))
            self.assertIsNone(find_group_by_name(cnx, "watchmen"))

    def test_register_an_user_into_db(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(NoResultError):
                cnx.execute("Any U WHERE U is CWUser, U login 'test'").one()

            user_eid = register_user_into_db(cnx, "test", "managers", "psswd")
            self.assertIsInstance(user_eid, int)

            user = cnx.entity_from_eid(user_eid)
            self.assertEqual(user.login, "test")
            self.assertIn("managers", user.groups)


class SAMLResponseTC(_SAMLCommonTC):

    def test_get_an_unknown_user(self):
        with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                   return_value=('unknown_user', {})):

            self.assertIsNone(get_user(self.request))

    def test_get_an_existing_user(self):
        with self.admin_access.repo_cnx() as cnx:
            user = self.create_user(cnx, 'saml_user')

            with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                       return_value=('saml_user', {})):

                userid = get_user(self.request)

                self.assertEqual(userid, user.eid)

    def test_register_a_new_user(self):
        with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                   return_value=('saml_user', {})):

            self.assertIsNone(get_user(self.request))

            userid = register_user(self.request)

            self.assertIsNotNone(userid)
            self.assertEqual(get_user(self.request), userid)

    def test_register_an_existing_user(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, 'saml_user')

            with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                       return_value=('saml_user', {})):

                self.assertIsNotNone(get_user(self.request))

                with self.assertRaises(ValidationError):
                    register_user(self.request)


if __name__ == '__main__':
    from unittest import main
    main()
