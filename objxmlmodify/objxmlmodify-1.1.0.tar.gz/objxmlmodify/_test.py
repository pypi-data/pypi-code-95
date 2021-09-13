import objxmlmodify
import unittest


class Test_objxmlmodify(unittest.TestCase):
    def setUp(self):
        self.stuff = objxmlmodify.process_modify_xml(open("_sample.xml").read(), [])

    def test_xml(self):
        self.assertEqual(self.stuff, [123, [1, 8, 7]])
