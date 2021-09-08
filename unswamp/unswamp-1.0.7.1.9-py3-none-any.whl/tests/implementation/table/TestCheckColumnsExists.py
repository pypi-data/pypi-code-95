from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnsExists


class TestCheckColumnsExists(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        columns = ["Year"]
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_pass_single = CheckColumnsExists(
            key, columns, active, meta_data)
        columns = ["AColumn"]
        self.check_fail_single = CheckColumnsExists(
            key, columns, active, meta_data)

        columns = ["Year", "Grade", "Level 2 #"]
        self.check_pass_multiple = CheckColumnsExists(
            key, columns, active, meta_data)
        columns = ["Year", "Grade", "Level 2 #", "AColumn"]
        self.check_fail_multiple = CheckColumnsExists(
            key, columns, active, meta_data)

    def test_run_pass_single(self):
        check = self.check_pass_single
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_single(self):
        check = self.check_fail_single
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_pass_multiple(self):
        check = self.check_pass_multiple
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_multiple(self):
        check = self.check_fail_multiple
        expectation = False
        TestHelpers.test_run(self, check, expectation)
