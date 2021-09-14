import doctest

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_eac import testutils

FLAGS = doctest.REPORT_UDIFF


class EACExportFunctionalTests(CubicWebTC, testutils.XmlTestMixin):
    """Functional tests for EAC-CPF export."""

    def setUp(self):
        super(EACExportFunctionalTests, self).setUp()
        self.globs = globals().copy()
        self.globs["self"] = self

    def _test(self, filename):
        with self.admin_access.cnx() as cnx:
            self.globs["cnx"] = cnx
            failure_count, test_count = doctest.testfile(
                filename, globs=self.globs, optionflags=FLAGS
            )
            if failure_count:
                self.fail(
                    "{} failures of {} in {} (check report)".format(
                        failure_count, test_count, filename
                    )
                )

    def test_simple(self):
        self._test("export-simple.rst")

    def test_roundtrip(self):
        self._test("export-roundtrip.rst")


if __name__ == "__main__":
    import unittest

    unittest.main()
