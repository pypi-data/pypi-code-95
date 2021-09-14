# pylint: disable=line-too-long
# pylint: disable=protected-access

# Standard library imports
import os
import unittest

# Local application/library specific imports
import gitlab_job_exec


class TestGitlabCI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gitlab_ci = gitlab_job_exec.GitlabCI("tests/resources/full.yml", "file://" + os.getcwd())

    def test_no_invalid_job_name(self):
        for name in ["after_script", "before_script", "cache", "default", "image", "include", "services", "stages", "types", "variables", "workflow"]:
            with self.subTest(name=name):
                self.assertNotIn(name, self.gitlab_ci.jobs)

    def test_simple_jobs(self):
        with self.subTest(name="simple_job_1"):
            expected_result = {'image': "simple_job_1",
                               'script': ["echo \"simple_job_1\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['simple_job_1'])
        with self.subTest(name="simple_job_2"):
            expected_result = {'script': ["echo \"simple_job_2\""]}
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['simple_job_2'])

    def test_included_jobs(self):
        with self.subTest(name="included_job_1"):
            expected_result = {'script': ["echo \"included_job_1\""]}
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['included_job_1'])
        with self.subTest(name="included_job_2"):
            expected_result = {'script': ["echo \"included_job_2\""]}
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['included_job_2'])

    def test_extended_jobs(self):
        with self.subTest(name="extended_job_1"):
            expected_result = {'before_script': ["echo \"before_script extended_job_1\""],
                               'image': "extended_job_1",
                               'script': ["echo \"simple_job_1\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['extended_job_1'])
        with self.subTest(name="extended_job_2"):
            expected_result = {'after_script': ["echo \"after_script extended_job_2\""],
                               'before_script': ["echo \"before_script extended_job_1\""],
                               'image': "extended_job_1",
                               'script': ["echo \"simple_job_1\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['extended_job_2'])
        with self.subTest(name="extended_job_3"):
            expected_result = {'image': "simple_job_1",
                               'script': ["echo \"extended_job_3\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['extended_job_3'])
        with self.subTest(name="extended_job_4"):
            expected_result = {'image': "extended_job_1",
                               'before_script': ["echo \"before_script_extended_job_4\""],
                               'script': ["echo \"simple_job_1\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['extended_job_4'])
        with self.subTest(name="extended_job_5"):
            expected_result = {'after_script': ["echo \"after_script extended_job_5\""],
                               'before_script': ["echo \"before_script extended_job_6\""],
                               'image': "extended_job_6",
                               'script': ["echo \"simple_job_1\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['extended_job_5'])
        with self.subTest(name="extended_job_6"):
            expected_result = {'before_script': ["echo \"before_script extended_job_6\""],
                               'image': "extended_job_6",
                               'script': ["echo \"simple_job_1\""],
                               }
            self.assertDictEqual(expected_result, self.gitlab_ci._detail['extended_job_6'])

    def test_hidden_jobs(self):
        self.assertNotIn(".hidden_job", self.gitlab_ci.jobs)

    def test_get_include(self):
        expected_result = {'included_job_2': {'script': ["echo \"included_job_2\""]}}

        with self.subTest(name="file"):
            result = self.gitlab_ci._get_include({'project': "",
                                                  'file': "/tests/resources/full_included_2.yml",
                                                  },
                                                 )
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="local"):
            result = self.gitlab_ci._get_include({'local': "/tests/resources/full_included_2.yml"})
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="remote"):
            result = self.gitlab_ci._get_include({'remote': "file://"
                                                            + os.getcwd()
                                                            + "/tests/resources/full_included_2.yml",
                                                  },
                                                 )
            self.assertDictEqual(expected_result, result)

    def test_get_include_pattern(self):
        gitlab_ci = gitlab_job_exec.GitlabCI("tests/resources/full.yml",
                                             include_pattern="file://" + os.getcwd() + "/tests/resources/{project}",
                                             )
        expected_result = {'project_a_included_job_2': {'script': ["echo \"project_a_included_job_2\""]}}

        with self.subTest(name="local_1"):
            result = gitlab_ci._get_include({'local': "/tests/resources/project_a/included_2.yml"})
            self.assertDictEqual(expected_result, result)

        with self.subTest(name="local_2"):
            result = gitlab_ci._get_include({'local': "/included_2.yml",
                                             '_included_from': "file://" + os.getcwd() + "/tests/resources/project_a",
                                             },
                                            )
            self.assertDictEqual(expected_result, result)

        with self.subTest(name="file"):
            result = gitlab_ci._get_include({'project': "some_group/project_a",
                                             'file': "/included_2.yml",
                                             },
                                            )
            self.assertDictEqual(expected_result, result)

        with self.subTest(name="subgroup_file"):
            expected_result = {'project_c_included_job': {'script': ["echo \"project_c_included_job\""]}}
            result = gitlab_ci._get_include({'project': "some_group/some_subgroup/project_c",
                                             'file': "/included.yml",
                                             },
                                            )
            self.assertDictEqual(expected_result, result)

    def test_include_pattern(self):
        gitlab_ci = gitlab_job_exec.GitlabCI("tests/resources/include.yml",
                                             include_pattern="file://" + os.getcwd() + "/tests/resources/{project}",
                                             )

        with self.subTest(name="included_job_1"):
            expected_result = {'script': ["echo \"project_a_included_job\""]}
            self.assertDictEqual(expected_result, gitlab_ci._detail['project_a_included_job'])
        with self.subTest(name="included_job_2"):
            expected_result = {'script': ["echo \"project_a_included_job_2\""]}
            self.assertDictEqual(expected_result, gitlab_ci._detail['project_a_included_job_2'])
        with self.subTest(name="included_job_3"):
            expected_result = {'script': ["echo \"project_b_included_job\""]}
            self.assertDictEqual(expected_result, gitlab_ci._detail['project_b_included_job'])
        with self.subTest(name="included_job_4"):
            expected_result = {'script': ["echo \"project_c_included_job\""]}
            self.assertDictEqual(expected_result, gitlab_ci._detail['project_c_included_job'])

        with self.subTest(name="included_job_list_format_1"):
            expected_result = {'script': ["echo \"project_d_included_job\""]}
            self.assertDictEqual(expected_result, gitlab_ci._detail['project_d_included_job'])
        with self.subTest(name="included_job_list_format_2"):
            expected_result = {'script': ["echo \"project_d_included_job_2\""]}
            self.assertDictEqual(expected_result, gitlab_ci._detail['project_d_included_job_2'])


class TestGitlabJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gitlab_ci = gitlab_job_exec.GitlabCI("tests/resources/full.yml", "file://" + os.getcwd())

    def test_unravel_parameter(self):
        with self.subTest(name="empty"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={},
                                                                 global_data={},
                                                                 inherited=True,
                                                                 default="default",
                                                                 )
            self.assertEqual("default", value)
        with self.subTest(name="inherit_false"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={},
                                                                 global_data={'param': "global"},
                                                                 inherited=False,
                                                                 default="default",
                                                                 )
            self.assertEqual("default", value)
        with self.subTest(name="inherit_true"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={},
                                                                 global_data={'param': "global"},
                                                                 inherited=True,
                                                                 default="default",
                                                                 )
            self.assertEqual("global", value)
        with self.subTest(name="inherit_true_with_param"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={'param': "local"},
                                                                 global_data={'param': "global"},
                                                                 inherited=True,
                                                                 default="default",
                                                                 )
            self.assertEqual("local", value)
        with self.subTest(name="inherit_true_without_globals"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={},
                                                                 global_data={},
                                                                 inherited=True,
                                                                 default="default",
                                                                 )
            self.assertEqual("default", value)
        with self.subTest(name="inherit_with_specific"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={},
                                                                 global_data={'param': "global"},
                                                                 inherited=['param'],
                                                                 default="default",
                                                                 )
            self.assertEqual("global", value)
        with self.subTest(name="inherit_without_specific"):
            value = gitlab_job_exec.GitlabJob._unravel_parameter("param",
                                                                 local_data={},
                                                                 global_data={'param': "global"},
                                                                 inherited=['foobar'],
                                                                 default="default",
                                                                 )
            self.assertEqual("default", value)

    def test_variables(self):
        with self.subTest(name="None"):
            self.assertEqual("None", self.gitlab_ci.jobs['simple_job_3'].variables['var4'])

    def test_inherited(self):
        with self.subTest(name="without_inherit"):
            expected_result = {'var1': "value1", 'var2': "value2"}
            result = self.gitlab_ci.jobs['simple_job_1'].variables
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="inherit_false"):
            expected_result = {}
            result = self.gitlab_ci.jobs['inherited_job_1'].variables
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="inherit_var1"):
            expected_result = {'var1': "value1", 'var3': "value3"}
            result = self.gitlab_ci.jobs['inherited_job_2'].variables
            self.assertDictEqual(expected_result, result)
        with self.subTest(name="inherit_overright"):
            expected_result = {'var1': "value1", 'var2': "new_value"}
            result = self.gitlab_ci.jobs['inherited_job_3'].variables
            self.assertDictEqual(expected_result, result)
