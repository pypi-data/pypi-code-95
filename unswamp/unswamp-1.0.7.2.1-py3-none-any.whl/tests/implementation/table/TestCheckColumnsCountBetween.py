from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnsCountBetween


class TestCheckColumnsCountBetween(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        number_of_columns_min = 21
        number_of_columns_max = 21
        inclusive = True
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_inclusive_pass = CheckColumnsCountBetween(
            key, number_of_columns_min, number_of_columns_max, inclusive, active, meta_data)
        self.check_inclusive_fail_lower = CheckColumnsCountBetween(
            key, number_of_columns_min + 10, number_of_columns_max, inclusive, active, meta_data)
        self.check_inclusive_fail_upper = CheckColumnsCountBetween(
            key, number_of_columns_min, number_of_columns_max - 10, inclusive, active, meta_data)

        number_of_columns_min = 20
        number_of_columns_max = 22
        inclusive = False
        self.check_exclusive_pass = CheckColumnsCountBetween(
            key, number_of_columns_min, number_of_columns_max, inclusive, active, meta_data)
        self.check_exclusive_fail_lower = CheckColumnsCountBetween(
            key, number_of_columns_min + 10, number_of_columns_max, inclusive, active, meta_data)
        self.check_exclusive_fail_upper = CheckColumnsCountBetween(
            key, number_of_columns_min, number_of_columns_max - 10, inclusive, active, meta_data)

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
