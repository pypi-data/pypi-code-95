from unittest import TestCase
from datetime import datetime
from tests.TestHelpers import TestHelpers
from unswamp.objects.checks import CheckColumnsMatchOrderedList


class TestCheckColumnsMatchOrderedList(TestCase):
    def setUp(self):
        key = TestHelpers.random_string()
        columns = ["Year", "Category", "Number Tested", "Mean Scale Score"]
        active = TestHelpers.random_bool()
        meta_data = {"Date": datetime.today()}
        self.check_pass = CheckColumnsMatchOrderedList(
            key, columns, active, meta_data)

        columns = ["Year", "Category", "Mean Scale Score"]
        self.check_fail_missing = CheckColumnsMatchOrderedList(
            key, columns, active, meta_data)

        columns = ["Year", "Category", "Number Tested",
                   "AColumn", "Mean Scale Score"]
        self.check_fail_append_between = CheckColumnsMatchOrderedList(
            key, columns, active, meta_data)

        columns = ["Year", "Category", "Number Tested",
                   "Mean Scale Score", "AColumn"]
        self.check_fail_append_end = CheckColumnsMatchOrderedList(
            key, columns, active, meta_data)

        columns = ["AColumn", "Year", "Category",
                   "Number Tested", "Mean Scale Score"]
        self.check_fail_append_start = CheckColumnsMatchOrderedList(
            key, columns, active, meta_data)

    def test_run_pass(self):
        check = self.check_pass
        expectation = True
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_missing(self):
        check = self.check_fail_missing
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_append_between(self):
        check = self.check_fail_append_between
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_append_start(self):
        check = self.check_fail_append_start
        expectation = False
        TestHelpers.test_run(self, check, expectation)

    def test_run_fail_append_end(self):
        check = self.check_fail_append_end
        expectation = False
        TestHelpers.test_run(self, check, expectation)
