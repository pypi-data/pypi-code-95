import unittest
from oapi_parse.reader.oapijson import OpenApiJsonReader
from oapi_parse.reader.oapiyml import OpenApiYamlReader
import os

class TestReaders(unittest.TestCase):
    def test_json_reader(self):
        """
        Tests the Simple Json reader of Open API
        :return:
        """
        oapi_reader=OpenApiJsonReader(os.getcwd()+"/data/json_read_sample.json")
        json_dict=oapi_reader.read_open_api()
        self.assertEqual(json_dict["info"]["title"], "Sample test data")

    def test_yaml_reader(self):
        """
        Tests the Simple Yaml reader of Open API
        :return:
        """
        oapi_yaml_reader=OpenApiYamlReader(os.getcwd()+"/data/yaml_read_sample.yml")
        json_dict=oapi_yaml_reader.read_open_api()
        self.assertEqual(json_dict["info"]["title"], "Sample yaml data")

if __name__ == '__main__':
    unittest.main()
