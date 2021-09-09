from pathlib import Path


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PathDescriptor:
    def __init__(self, name):
        self.name = name

    def __set__(self, obj, value):
        value = [Path(path) for path in value]
        for path in value:
            _format = str(path).split(".")[-1].lower()
            if _format not in FORMATS:
                raise Exception("Format error: %s" % _format)
            if not path.exists():
                raise OSError("There is no such file: %s" % str(path.absolute()))
        obj.__dict__[self.name] = value


FORMATS = ["json", "yaml", "yml", "toml"]
SETTINGS = "settings"
SECRETS = ".secrets"

GITIGNORE = Path(".gitignore")
CONFIG_IGNORE = "\n# myconfig\n{}"

ENV = Path(".env")
ENV_ONLY_EXAMPLE = "from myconfig import MyConfig\n\nconfig = MyConfig()\n"
CODE_EXAMPLE = "from myconfig import MyConfig\n\nconfig = MyConfig(['{}', '{}'])\n"

open_file = lambda path: open(str(path), encoding="utf-8")  # noqa: E731
