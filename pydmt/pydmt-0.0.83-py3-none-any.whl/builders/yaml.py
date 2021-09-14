import yaml

from jsonschema import validate

from pydmt.utils.filesystem import mkdir_touch

from pydmt.builders.one_source_one_target import OneSourceOneTarget

METADATA = "metadata"
SCHEMA_FILE = "schema_file"


class YamlValidate(OneSourceOneTarget):
    def build(self):
        with open(self.source, "rt") as input_handle:
            data = yaml.load(input_handle, yaml.SafeLoader)
            if METADATA in data:
                schema_file = data[METADATA][SCHEMA_FILE]
                schema = yaml.load(schema_file, Loader=yaml.SafeLoader)
                validate(data, schema)
        mkdir_touch(self.target)
