import logging
import os
import unittest

from kfai_env.env import Environment
from kfai_env.test.utils.set_env import set_env

logger = logging.getLogger(__name__)


class TestEnvUnittest(unittest.TestCase):

    def test_load_env_local(self):
        with set_env():
            e = Environment('kfai_env/test')
            e.load_env()
            assert os.getenv("TEST_ENV") == "hello world_local"

    def test_load_env_test(self):
        with set_env(ENV="TEST"):
            e = Environment('kfai_env/test')
            e.register_environment("TEST")
            e.load_env()
            assert os.getenv("TEST_ENV") == "hello world_test"

    def test_casing_on_test(self):
        with set_env(ENV="TEST"):
            e = Environment('kfai_env/test')
            e.register_environment("test")
            e.load_env()
            assert os.getenv("TEST_ENV") == "hello world_test"
