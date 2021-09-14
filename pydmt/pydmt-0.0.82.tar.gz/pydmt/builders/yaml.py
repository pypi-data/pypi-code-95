import yaml

from pydmt.utils.filesystem import mkdir_touch

from pydmt.builders.one_source_one_target import OneSourceOneTarget


class YamlValidate(OneSourceOneTarget):
    def build(self):
        with open(self.source, "rt") as input_handle:
            yaml.load(input_handle, yaml.SafeLoader)
        mkdir_touch(self.target)
