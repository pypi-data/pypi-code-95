# pylint: disable=C0325
import os
import unittest
import json


test_dir = os.path.dirname(os.path.abspath(__file__))

class SuiteA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # unittest chokes when import is at module-level
        pass
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_poll_coil_1(self):
        print(os.path.abspath(os.path.curdir))
        print(test_dir)
        with open(os.path.join(test_dir, 'poll-coil-1.json')) as __f:
            config_io = json.loads(__f.read())
            print(json.dumps(config_io, indent=1))
            # validate.check(config_io['channels'])


def main():
    unittest.main()

if __name__ == "__main__":
    main()
