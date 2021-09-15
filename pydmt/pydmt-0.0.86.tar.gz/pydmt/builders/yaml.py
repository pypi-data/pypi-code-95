import json
import yaml

from jsonschema import validate

from pydmt.utils.filesystem import mkdir_touch

from pydmt.builders.one_source_one_target import OneSourceOneTarget

METADATA = "metadata"
SCHEMA_FILE_JSON = "schema_file_json"
SCHEMA_FILE_YAML = "schema_file_yaml"


class YamlValidate(OneSourceOneTarget):
    def build(self):
        with open(self.source) as yaml_stream:
            data = yaml.load(yaml_stream, yaml.SafeLoader)
            if METADATA in data:
                metadata = data[METADATA]
                if SCHEMA_FILE_JSON in metadata:
                    schema_file = data[METADATA][SCHEMA_FILE_JSON]
                    with open(schema_file) as schema_stream:
                        schema = json.load(schema_stream)
                        validate(data, schema)
                if SCHEMA_FILE_YAML in metadata:
                    schema_file = data[METADATA][SCHEMA_FILE_YAML]
                    with open(schema_file) as schema_stream:
                        schema = yaml.load(schema_stream, yaml.SafeLoader)
                        validate(data, schema)
            mkdir_touch(self.target)
