import yaml

from pydmt.utils.filesystem import touch

from pydmt.builders.one_source_one_target import OneSourceOneTarget


class YamlValidate(OneSourceOneTarget):
    def build(self):
        with open(self.source, "rt") as input_handle:
            yaml.load(input_handle, yaml.SafeLoader)
        touch(self.target)
