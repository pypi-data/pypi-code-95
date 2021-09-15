import pathlib

import orjson
import yaml


class File(type(pathlib.Path())):
    def open(self, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        if encoding is None and "b" not in mode:
            encoding = "utf-8"
        return super().open(mode, buffering, encoding, errors, newline)

    def copy(self, target_path):
        File(target_path).write_bytes(self.read_bytes())

    def load_json(self):
        data = orjson.loads(self.read_bytes())
        return data

    def dump_json(self, data):
        self.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    def load_yaml(self):
        with self.open() as f:
            data = yaml.load(f.read(), Loader=yaml.CLoader)
        return data

    def dump_yaml(self, data, *args, **kwargs):
        with self.open(mode="w") as f:
            yaml.dump(
                data, stream=f, Dumper=yaml.CDumper, allow_unicode=True, *args, **kwargs
            )


if __name__ == "__main__":
    pass
