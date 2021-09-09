# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from unittest import mock
import unittest

import upt
from upt_pypi.upt_pypi import PyPIFrontend


class TestPyPIFrontend(unittest.TestCase):
    def setUp(self):
        self.parser = PyPIFrontend()

    def test_get_name(self):
        json = {'info': {'name': 'WTForms'}}
        self.assertEqual(self.parser.get_name(json), 'WTForms')


class TestRequirements(unittest.TestCase):
    def setUp(self):
        self.frontend = PyPIFrontend()

    def test_string_req_to_upt_req(self):
        out = self.frontend._string_req_to_upt_pkg_req('cryptography')
        expected = upt.PackageRequirement('cryptography', '')
        self.assertEqual(out, expected)

        out = self.frontend._string_req_to_upt_pkg_req('six (>=1.3.4)')
        expected = upt.PackageRequirement('six', '>=1.3.4')
        self.assertEqual(out, expected)

    def test_string_req_list_to_upt_req_list(self):
        out = self.frontend._string_req_list_to_upt_pkg_req_list([])
        expected = []
        self.assertListEqual(out, expected)

        reqs = ['foo (>1.0)', 'bar']
        out = self.frontend._string_req_list_to_upt_pkg_req_list(reqs)
        expected = [
            upt.PackageRequirement('foo', '>1.0'),
            upt.PackageRequirement('bar', '')
        ]
        self.assertListEqual(out, expected)

    def test_parse_requires_dist(self):
        alembic_1_7_1_requires_dist = [
            'SQLAlchemy (>=1.3.0)',
            'Mako',
            'importlib-metadata ; python_version < "3.8"',
            'importlib-resources ; python_version < "3.9"',
            "python-dateutil ; extra == 'tz'"
        ]
        expected = ([
            upt.PackageRequirement('SQLAlchemy', '>=1.3.0'),
            upt.PackageRequirement('Mako', '')
        ], [])
        out = self.frontend.parse_requires_dist(alembic_1_7_1_requires_dist)
        self.assertEqual(out, expected)

        upt_rubygems_0_4_1 = [
            'requests',
            'semver',
            'upt (>=0.11)',
            "requests-mock ; extra == 'test'"
        ]
        expected = ([
            upt.PackageRequirement('requests', ''),
            upt.PackageRequirement('semver', ''),
            upt.PackageRequirement('upt', '>=0.11'),
        ], [
            upt.PackageRequirement('requests-mock', '')
        ])
        out = self.frontend.parse_requires_dist(upt_rubygems_0_4_1)
        self.assertEqual(out, expected)

    def test_compute_requirement_from_pypi_json(self):
        # No json, for some reason
        out = self.frontend.compute_requirements_from_pypi_json({})
        self.assertDictEqual(out, {})

        # Useless json
        json = {'info': {}}
        out = self.frontend.compute_requirements_from_pypi_json(json)
        self.assertDictEqual(out, {})

        # The interesting field is empty
        json = {
            'info': {
                'requires_dist': []
            }
        }
        out = self.frontend.compute_requirements_from_pypi_json(json)
        self.assertDictEqual(out, {})

        # What we actually expected
        json = {
            'info': {
                'requires_dist': [
                    'Jinja2',
                    "requests-mock ; extra == 'test'",
                ],
            }
        }
        expected = {
            'run': [upt.PackageRequirement('Jinja2', '')],
            'test': [upt.PackageRequirement('requests-mock', '')],
        }
        out = self.frontend.compute_requirements_from_pypi_json(json)
        self.assertDictEqual(out, expected)

    @mock.patch('urllib.request.urlretrieve')
    def test_compute_requirement_from_wheel(self, m_urlretrieve):
        m_urlretrieve.return_value = [('foo', None)]
        with mock.patch('pkginfo.Wheel') as m:
            fake_wheel = mock.Mock()
            m.return_value = fake_wheel
            fake_wheel.requires_dist = []
            out = self.frontend.compute_requirements_from_wheel('url')
            self.assertDictEqual(out, {})

            # Only runtime requirements
            fake_wheel.requires_dist = ['requests']
            out = self.frontend.compute_requirements_from_wheel('url')
            expected = {
                'run': [upt.PackageRequirement('requests', '')],
            }
            self.assertDictEqual(out, expected)

            # Runtime and test requirements
            fake_wheel.requires_dist = [
                'requests', "requests-mock ; extra == 'test'"
            ]
            out = self.frontend.compute_requirements_from_wheel('url')
            expected = {
                'run': [upt.PackageRequirement('requests', '')],
                'test': [upt.PackageRequirement('requests-mock', '')],
            }
            self.assertDictEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_pypi_json')
    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_wheel')
    @mock.patch.object(PyPIFrontend, 'get_wheel_url')
    def test_compute_requirements(self, m_wheel_url, m_wheel, m_json):
        self.frontend.json = {
            'info': {
                'version': '1.2.3'
            },
            'releases': {
                '1.2.3': 'fake'
            },
        }
        m_wheel_url.return_value = 'fake-url'

        # Scenario: compute_requirements_from_pypi_json is enough
        m_json.return_value = {'run': []}
        out = self.frontend.compute_requirements()
        self.assertEqual(out, {'run': []})

        # Scenario: compute_requirements_from_pypi_json is not enough
        m_json.return_value = {}
        m_wheel.return_value = {'run': []}
        out = self.frontend.compute_requirements()
        self.assertEqual(out, {'run': []})

        # Scenario: The World Is Not Enough
        m_json.return_value = {}
        m_wheel.return_value = {}
        out = self.frontend.compute_requirements()
        self.assertEqual(out, {})

        # Scenario: There is no wheel
        m_json.return_value = {}
        m_wheel_url.side_effect = ValueError
        out = self.frontend.compute_requirements()
        self.assertEqual(out, {})


class TestArchiveMethods(unittest.TestCase):
    def setUp(self):
        self.frontend = PyPIFrontend()
        self.release = [{
            'url': 'http://example.com/source.tar.gz',
            'packagetype': 'sdist',
            'size': 123,
            'digests': {
                'md5': 'md5',
                'sha256': 'sha256',
            }
        }, {
            'url': 'http://example.com/wheel.whl',
            'packagetype': 'bdist_wheel',
            'size': 321,
            'digests': {
                'md5': 'md5-wheel',
                'sha256': 'sha256-wheel',
            }
        }]

    def test_get_archive_info_bad_type(self):
        with self.assertRaises(ValueError):
            self.frontend.get_archive_info(self.release, 'bad-argument')

    def test_get_archive_sdist(self):
        self.assertEqual(self.frontend.get_sdist_archive_url(self.release),
                         self.release[0]['url'])

    def test_get_archive_bdist(self):
        self.assertEqual(self.frontend.get_wheel_url(self.release),
                         self.release[1]['url'])

    def test_get_archives(self):
        out = self.frontend.get_archives(self.release)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].url, 'http://example.com/source.tar.gz')
        self.assertEqual(out[0].size, 123)
        self.assertEqual(out[0].md5, 'md5')
        self.assertEqual(out[0].sha256, 'sha256')


if __name__ == '__main__':
    unittest.main()
