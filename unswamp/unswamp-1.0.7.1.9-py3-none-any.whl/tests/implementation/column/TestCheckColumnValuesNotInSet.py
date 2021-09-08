from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnValuesNotInSet


class TestCheckColumnValuesNotInSet(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        column = "Year"
        values = set({2005, 2012})
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_pass = CheckColumnValuesNotInSet(
            key, column, values, active, meta_data)

        values = set({2006, 2012})
        self.check_fail = CheckColumnValuesNotInSet(
            key, column, values, active, meta_data)

    def test_run_pass(self):
        check = self.check_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail(self):
        check = self.check_fail
        expectation = False
        TestHelpers.test_run(self, check, expectation)
