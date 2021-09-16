from looqbox.objects.tests import ObjTable
from looqbox.objects.tests import LooqObject
import unittest
import json
import numpy as np
import pandas as pd


class TestObjectTable(unittest.TestCase):
    """
    Test looq_table file
    """

    def setUp(self) -> None:
        data = np.array([
            [100, 120, 98, 73, 20, 157, 124, 0, 9999, 100],
            [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
        ]).T

        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        self.looq_object_table = ObjTable(df)

    def test_instance(self):
        looq_object_table = self.looq_object_table

        self.assertIsInstance(looq_object_table, LooqObject)

    def test_json_creation(self):
        looq_object_table = self.looq_object_table

        # Testing JSON keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure).keys())
        self.assertTrue("objectType" in json_table_keys, msg="objectType not found in JSON structure test")
        self.assertTrue("title" in json_table_keys, msg="title not found in JSON structure test")
        self.assertTrue("header" in json_table_keys, msg="header not found in JSON structure test")
        self.assertTrue("body" in json_table_keys, msg="body not found in JSON structure test")
        self.assertTrue("footer" in json_table_keys, msg="footer not found in JSON structure test")
        self.assertTrue("searchable" in json_table_keys, msg="searchable not found in JSON structure test")
        self.assertTrue("searchString" in json_table_keys, msg="searchString not found in JSON structure test")
        self.assertTrue("pagination" in json_table_keys, msg="paginationSize not found in JSON structure test")
        self.assertTrue("framed" in json_table_keys, msg="framed not found in JSON structure test")
        self.assertTrue("framedTitle" in json_table_keys, msg="framedTitle not found in JSON structure test")
        self.assertTrue("stacked" in json_table_keys, msg="stacked not found in JSON structure test")
        self.assertTrue("showBorder" in json_table_keys, msg="showBorder not found in JSON structure test")
        self.assertTrue("showOptionBar" in json_table_keys, msg="showOptionBar not found in JSON structure test")
        self.assertTrue("showHighlight" in json_table_keys, msg="showHighlight not found in JSON structure test")
        self.assertTrue("striped" in json_table_keys, msg="striped not found in JSON structure test")
        self.assertTrue("sortable" in json_table_keys, msg="sortable not found in JSON structure test")
        self.assertTrue("class" in json_table_keys, msg="class not found in JSON structure test")
        self.assertTrue("scroll" in json_table_keys, msg="class not found in JSON structure test")

    def test_header_json_structure(self):
        looq_object_table = self.looq_object_table

        # Testing JSON header keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure)["header"].keys())
        self.assertTrue("content" in json_table_keys, msg="content not found in header JSON structure test")
        self.assertTrue("visible" in json_table_keys, msg="visible not found in header JSON structure test")
        self.assertTrue("group" in json_table_keys, msg="group not found in header JSON structure test")

    def test_body_json_structure(self):
        looq_object_table = self.looq_object_table

        # Testing JSON body keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure)["body"].keys())
        self.assertTrue("content" in json_table_keys, msg="content not found in body JSON structure test")
        self.assertTrue("_lq_column_config" in json_table_keys, msg="_lq_column_config not found in body JSON structure test")

    def test_footer_json_structure(self):
        looq_object_table = self.looq_object_table

        # Testing JSON footer keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure)["footer"].keys())
        self.assertTrue("content" in json_table_keys, msg="content not found in footer JSON structure test")
        self.assertTrue("subtotal" in json_table_keys, msg="subtotal not found in footer JSON structure test")

    def test_subtotal_structure(self):
        looq_object_table = self.looq_object_table
        looq_object_table.subtotal = [{"text": "Subtotal text", "link": "Subtotal link"}]
        json_table = json.loads(looq_object_table.to_json_structure)

        # Testing JSON footer keys
        self.assertTrue(isinstance(json_table["footer"]["subtotal"], list))


if __name__ == '__main__':
    unittest.main()
