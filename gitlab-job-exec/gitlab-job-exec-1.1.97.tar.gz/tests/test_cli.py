# pylint: disable=line-too-long
# pylint: disable=protected-access

# Standard library imports
import unittest

# Local application/library specific imports
import gitlab_job_exec.cli


class TestParseOptions(unittest.TestCase):
    def test_variables(self):
        with self.subTest(name="empty"):
            expected_result = {"VAR1": ""}
            result = gitlab_job_exec.cli.parse_options(["--extra-vars", "VAR1=", "job"]).extra_vars
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="simple"):
            expected_result = {"VAR1": "var1"}
            result = gitlab_job_exec.cli.parse_options(["--extra-vars", "VAR1=var1", "job"]).extra_vars
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="multiple_in_one"):
            expected_result = {"VAR1": "var1",
                               "VAR2": "var2",
                               }
            result = gitlab_job_exec.cli.parse_options(["--extra-vars", "VAR1=var1 VAR2=var2", "job"]).extra_vars
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="multiple_in_two"):
            expected_result = {"VAR1": "var1",
                               "VAR2": "var2",
                               }
            result = gitlab_job_exec.cli.parse_options(["--extra-vars", "VAR1=var1", "--extra-vars", "VAR2=var2", "job"]).extra_vars
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="equal_sign"):
            expected_result = {"EQUAL": "before=after"}
            result = gitlab_job_exec.cli.parse_options(["--extra-vars", "EQUAL=before=after", "job"]).extra_vars
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="file"):
            expected_result = {"VAR1": "var1",
                               "VAR2": "var2",
                               "EQUAL": "before=after",
                               }
            result = gitlab_job_exec.cli.parse_options(["--extra-vars", "@tests/resources/cli.env", "job"]).extra_vars
            self.assertDictEqual(expected_result, result)
