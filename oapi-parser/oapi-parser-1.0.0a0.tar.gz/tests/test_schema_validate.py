import os
import unittest


from oapi_parse.schema_validate.schema_validator import SchemaValidate
from oapi_parse.reader.oapijson import OpenApiJsonReader
from oapi_parse.reader.oapiyml import OpenApiYamlReader


class TestSchemaValidator(unittest.TestCase):
    """
    Test cases for schema validation
    """
    schema_path = "oapi_parse/schemas/{version}/{file_name}"
    schema_validate = SchemaValidate()

    def test_abs_path_with_default_inputs_positive(self):
        """
        test get absolute path method
        """
        actual_value = self.schema_validate._get_schema_abs_path()
        expected_value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      os.path.normpath(self.schema_path.format(version=3.0, file_name="schema.json")))
        self.assertEqual(actual_value, expected_value)

    def test_abs_path_with_diff_inputs_positive(self):
        """

        """
        schema_validate_obj = SchemaValidate("2.0")
        actual_value = schema_validate_obj._get_schema_abs_path(file_name="sample.yaml")
        expected_value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      os.path.normpath(self.schema_path.format(version="2.0", file_name="sample.yaml")))
        self.assertEqual(actual_value, expected_value)

    def test_abs_path_with_wrong_inputs_negative(self):
        """

        """
        schema_validate_obj = SchemaValidate("2.0")
        actual_value = schema_validate_obj._get_schema_abs_path(file_name="sample.yaml")
        expected_value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      os.path.normpath(self.schema_path.format(version="3.0", file_name="schema.json")))
        self.assertNotEqual(actual_value, expected_value)

    def test_load_schema_file_not_found(self):
        """

        """
        with self.assertRaises(FileNotFoundError):
            schema_validate_obj = SchemaValidate("1.0")
            schema_validate_obj._load_schema()

    def test_load_schema_check_key_in_resp_positive(self):
        """

        """
        schema = self.schema_validate._load_schema()
        expected_value = ["openapi", "info", "paths"]
        actual_value = schema["required"]
        self.assertEqual(actual_value, expected_value)

    def test_validate_json_schema_with_proper_data(self):
        """

        """
        instance_file_path = os.path.join(os.path.dirname(__file__), os.path.normpath("data\pet_store_30.json"))
        json_reader_obj = OpenApiJsonReader(instance_file_path)
        data = json_reader_obj.read_open_api()
        status, message = self.schema_validate.validate_schema(data)
        self.assertTrue(status)

    def test_validate_yaml_schema_with_proper_data(self):
        """

        """
        instance_file_path = os.path.join(os.path.dirname(__file__), os.path.normpath("data\pet_store_30.yaml"))
        yaml_reader_obj = OpenApiYamlReader(instance_file_path)
        data = yaml_reader_obj.read_open_api()
        status, message = self.schema_validate.validate_schema(data)
        self.assertTrue(status)

    def test_validate_yaml_schema_with_wrong_data(self):
        """

        """
        instance_file_path = os.path.join(os.path.dirname(__file__), os.path.normpath("data\pet_store_wrong_data.yaml"))
        yaml_reader_obj = OpenApiYamlReader(instance_file_path)
        data = yaml_reader_obj.read_open_api()
        status, message = self.schema_validate.validate_schema(data)
        self.assertFalse(status)

    def test_validate_json_schema_with_wrong_data(self):
        """

        """
        instance_file_path = os.path.join(os.path.dirname(__file__), os.path.normpath("data\pet_store_wrong_data.json"))
        json_reader_obj = OpenApiJsonReader(instance_file_path)
        data = json_reader_obj.read_open_api()
        status, message = self.schema_validate.validate_schema(data)
        self.assertFalse(status)

    def test_validate_json_schema_with_wrong_file(self):
        """

        """
        instance_file_path = os.path.join(os.path.dirname(__file__), os.path.normpath("data\pet_store_wrong_file_format.yaml"))
        yaml_reader_obj = OpenApiYamlReader(instance_file_path)
        data = yaml_reader_obj.read_open_api()
        status, message = self.schema_validate.validate_schema(data)


if __name__ == '__main__':
    unittest.main()
