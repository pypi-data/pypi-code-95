from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnValuesInSet


class TestCheckColumnValuesInSet(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        column = "Year"
        values = set({2006, 2007, 2008, 2009, 2010, 2011})
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_pass = CheckColumnValuesInSet(
            key, column, values, active, meta_data)

        values = set({2006, 2007, 2008, 2009, 2010})
        self.check_fail = CheckColumnValuesInSet(
            key, column, values, active, meta_data)

    def test_run_pass(self):
        check = self.check_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail(self):
        check = self.check_fail
        expectation = False
        TestHelpers.test_run(self, check, expectation)
