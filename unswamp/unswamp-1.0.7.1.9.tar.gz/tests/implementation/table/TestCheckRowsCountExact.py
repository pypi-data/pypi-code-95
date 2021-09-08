from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckRowsCountExact


class TestCheckRowsCountExact(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        number_of_rows = 168
        self.check_pass = CheckRowsCountExact(
            key, number_of_rows, active, meta_data)
        self.check_fail_smaller = CheckRowsCountExact(
            key, number_of_rows - 10, active, meta_data)
        self.check_fail_higher = CheckRowsCountExact(
            key, number_of_rows + 10, active, meta_data)

    def test_run_pass(self):
        check = self.check_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_smaller(self):
        check = self.check_fail_smaller
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_higher(self):
        check = self.check_fail_higher
        expectation = False
        TestHelpers.test_run(self, check, expectation)
