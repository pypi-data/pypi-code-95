import unittest
from rodasci.logger import Logger as logger

class TestAbLogger(unittest.TestCase):

    def test_CheckValue(self):
        logger.Init()
        logger.CheckValue(1, [2,3])

if __name__ == '__main__':
    unittest.main()