import json
import yaml

from jsonschema import validate

from pydmt.utils.filesystem import mkdir_touch

from pydmt.builders.one_source_one_target import OneSourceOneTarget

METADATA = "metadata"
SCHEMA_FILE = "schema_file"


class YamlValidate(OneSourceOneTarget):
    def build(self):
        with open(self.source) as yaml_stream:
            data = yaml.load(yaml_stream, yaml.SafeLoader)
            if METADATA in data:
                schema_file = data[METADATA][SCHEMA_FILE]
                with open(schema_file) as schema_stream:
                    schema = json.load(schema_stream)
                    validate(data, schema)
            mkdir_touch(self.target)
