from unittest import TestCase
from nubium_utils.env_var_generator import env_vars_creator

class TestEnvVarGenerator(TestCase):
    def setUp(self):
        self.dict_out = {
            "test_env_field": "test_env_value"
        }
        self.env_vars = env_vars_creator(self.dict_func)

    def dict_func(self):
        return self.dict_out

    def test_it_works(self):
        self.assertDictEqual(self.env_vars(), self.dict_out)

    def test_returns_same_python_object_each_call(self):
        self.assertEqual(id(self.env_vars()), id(self.env_vars()))  # also ensures subsequent calls work!
