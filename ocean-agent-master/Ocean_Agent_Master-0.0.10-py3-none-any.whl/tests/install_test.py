import unittest

from master.install import install


class SetupTest(unittest.TestCase):
    def test_setup(self):
        install()

