from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnValuesIncreasing


class TestCheckColumnValuesIncreasing(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        column = "LineNumber"
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_pass = CheckColumnValuesIncreasing(
            key, column, active, meta_data)

        column = "LineNumberInverse"
        self.check_fail_decreasing = CheckColumnValuesIncreasing(
            key, column, active, meta_data)

        column = "RandomNumber"
        self.check_fail_random = CheckColumnValuesIncreasing(
            key, column, active, meta_data)

        column = "ConstantNumber"
        self.check_fail_constant = CheckColumnValuesIncreasing(
            key, column, active, meta_data)

    def test_run_pass(self):
        check = self.check_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_decreasing(self):
        check = self.check_fail_decreasing
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_random(self):
        check = self.check_fail_random
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_constant(self):
        check = self.check_fail_constant
        expectation = False
        TestHelpers.test_run(self, check, expectation)
