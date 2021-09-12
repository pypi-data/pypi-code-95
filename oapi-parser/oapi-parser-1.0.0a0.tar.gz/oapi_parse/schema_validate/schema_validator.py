#!/usr/bin/env python
"""
Validate the xml/json against open api version schema.
"""
import os

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from oapi_parse.reader.oapijson import OpenApiJsonReader


class SchemaValidate:
    """
    Class to validate the json instance against open api schemas
    """
    __cwd = os.path.dirname(os.path.dirname(__file__))
    __schema_path_ref = os.path.normpath("schemas/{version}/{file_name}")

    def __init__(self, version_ : str = "3.0"):
        """
        Schema Validate Constructor
        :param version_: schema version
        """
        self.schema_version = version_

    def _get_schema_abs_path(self, file_name="schema.json", version_=None):
        """

        :param file_name: schema file name , default is schema.json
        :param version_: schema version, default value is None
        :return: absolute path of the schema file
        """
        schema_ver = self.schema_version if version_ is None else version_
        schema_path_fmt = self.__schema_path_ref.format(file_name=file_name, version=schema_ver)
        return os.path.join(self.__cwd, schema_path_fmt)

    def _load_schema(self, schema_file_path=None):
        """
        load the schema file as a json object
        :param schema_file_path: absolute file path of the schema file
        :return: schema json object
        """
        if schema_file_path is None:
            schema_file_path = self._get_schema_abs_path("schema.json")
        open_api_json_obj = OpenApiJsonReader(schema_file_path)
        schema_data = open_api_json_obj.read_open_api()
        return schema_data

    def validate_schema(self, instance_ : dict) -> tuple:
        """
        Method to validate the json/yaml instance against the respective schema
        :param instance_: dict:  json/yaml instance
        :return: tuple (boolean, str): validation status, Validation message
        """

        try:
            schema_data = self._load_schema()
            validate(instance=instance_, schema=schema_data)
            return True, "Given Instance Json is valid"
        except ValidationError as error_:
            print("Schema Validation Error: Given Instance json is invalid and error is :" + error_.message)
            return False, error_.message



