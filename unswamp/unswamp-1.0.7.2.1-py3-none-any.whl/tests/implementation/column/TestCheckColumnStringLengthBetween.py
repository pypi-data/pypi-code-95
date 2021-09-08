from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnStringLengthBetween


class TestCheckColumnStringLengthBetween(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        column = "Grade"
        value_min = 1
        value_max = 10
        inclusive = True
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_inclusive_pass = CheckColumnStringLengthBetween(
            key, column, value_min, value_max, inclusive, active, meta_data)
        self.check_inclusive_fail_lower = CheckColumnStringLengthBetween(
            key, column, value_min - 10, value_max, inclusive, active, meta_data)
        self.check_inclusive_fail_upper = CheckColumnStringLengthBetween(
            key, column, value_min, value_max + 10, inclusive, active, meta_data)

        value_min = 2
        value_max = 9
        inclusive = False
        self.check_exclusive_pass = CheckColumnStringLengthBetween(
            key, column, value_min, value_max, inclusive, active, meta_data)
        self.check_exclusive_fail_lower = CheckColumnStringLengthBetween(
            key, column, value_min - 10, value_max, inclusive, active, meta_data)
        self.check_exclusive_fail_upper = CheckColumnStringLengthBetween(
            key, column, value_min, value_max + 10, inclusive, active, meta_data)

    def test_run_inclusive_pass(self):
        check = self.check_inclusive_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_inclusive_fail_lower(self):
        check = self.check_inclusive_fail_lower
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_inclusive_fail_upper(self):
        check = self.check_inclusive_fail_upper
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_exclusive_pass(self):
        check = self.check_exclusive_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_exclusive_fail_lower(self):
        check = self.check_exclusive_fail_lower
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_exclusive_fail_upper(self):
        check = self.check_exclusive_fail_upper
        expectation = False
        TestHelpers.test_run(self, check, expectation)
