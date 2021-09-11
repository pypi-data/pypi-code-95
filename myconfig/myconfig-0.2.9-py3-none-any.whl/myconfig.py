import argparse
import json
from pathlib import Path
from typing import Any, List

import toml
import yaml

from .const import (
    CODE_EXAMPLE,
    CONFIG_IGNORE,
    CONFIG_REGEXP,
    ENV,
    ENV_ONLY_EXAMPLE,
    FORMATS,
    GITIGNORE,
    SECRETS,
    SETTINGS,
    PathDescriptor,
    Singleton,
    bold,
    green,
    open_file,
    underline,
)


class Store(dict):
    def __getitem__(self, k: str) -> Any:
        return self.get(k, None)

    def __setattr__(self, key: str, value: Any) -> None:
        return super().__setitem__(key, value)

    def __getattr__(self, key: str) -> Any:
        return self.__getitem__(key)


class Parser:
    switcher = {
        "JSON": lambda string: json.load(string),
        "TOML": lambda string: toml.load(string),
        "YAML": lambda string: yaml.load(string),
        "YML": lambda string: yaml.load(string),
    }

    @staticmethod
    def parser(obj: "MyConfig", filenames: List[Path]):
        for file in filenames:
            f = open_file(file)
            _format = str(file).split(".")[-1]
            data = Parser.switcher[_format.upper()](f)
            for key, value in data.items():
                if isinstance(value, dict):
                    value = Store(**value)
                key = key.replace("-", "_")
                store = getattr(obj, key)
                if isinstance(store, Store):
                    store.update(value)
                    continue
                setattr(obj, key, value)
            f.close()

    @staticmethod
    def env_parse(value: Any):
        if value.isdigit():
            return int(value)
        elif value.lower() in ["true", "false", "0", "1", 0, 1]:
            if value.lower() in ["true", "1", 1]:
                return True
            return False
        elif value.startswith("[") and value.endswith("]"):
            value = [x.strip() for x in value[1:-1].split(",")]
            return [Parser.env_parse(var) for var in value]
        elif value == "":
            return None
        return value


class MyConfig(metaclass=Singleton):
    _filenames = PathDescriptor("_filenames")
    _store = Store()

    def __init__(self, filenames: List[str] = None) -> None:
        if filenames:
            self._filenames = filenames
            Parser.parser(self, self._filenames)
        if ENV.exists():
            file = open_file(ENV)
            for line in file:
                key, value = line.strip("\n").split("=", 1)
                value = Parser.env_parse(value)
                setattr(self, key, value)

    def __str__(self) -> str:
        return str(self._store)

    def __getitem__(self, key: str) -> Any:
        return self._store.__getitem__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            return super().__setattr__(key, value)
        return self._store.__setitem__(key, value)

    def __getattr__(self, key: str) -> Any:
        return getattr(self._store, key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            return super().__setattr__(key, value)
        return setattr(self._store, key, value)


def gitignore_file(_format: str, secrets: str):
    if GITIGNORE.exists():
        with open(str(GITIGNORE), "r+", encoding="utf-8") as gitignore:
            lines = gitignore.readlines()
            for i, line in enumerate(lines.copy()):
                if CONFIG_REGEXP.match(line):
                    lines.insert(i + 1, f"{secrets}.{_format}\n")
                    gitignore.seek(0)
                    gitignore.writelines(lines)
                    return True
            nl = ""
            if not lines[-1].endswith("\n"):
                nl += "\n\n"
            else:
                nl += "\n"
            text = nl + CONFIG_IGNORE.format(secrets + "." + _format)
            gitignore.write(text)
            return True
    return False


def init(_format: str, settings: str, secrets: str) -> None:
    print(underline(green("Configuring your Python project environment...\n")))

    file = open(str(Path("settings.py")), "w", encoding="utf-8")
    print(f"File {bold(green('settings.py'))} was created.")

    if _format:
        if _format not in FORMATS:
            raise Exception("Unknown format.")
        for _file in [settings, secrets]:
            open(str(Path("%s.%s" % (_file, _format))), "a", encoding="utf-8").close()
        print(
            f"The {bold(green(settings + '.' +_format))} file was created to hold public settings "
            f"and {bold(green(secrets + '.' + _format))} file was created to hold private settings."
        )
        file.write(
            CODE_EXAMPLE.format(
                "%s.%s" % (settings, _format),
                "%s.%s" % (secrets, _format),
            )
        )
        if gitignore_file(_format, secrets):
            print(
                f"Also {bold(green(secrets + '.' + _format))} was added to .gitignore."
            )
    else:
        file.write(ENV_ONLY_EXAMPLE)
    file.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--init", default=None, type=str, nargs="?")
    parser.add_argument("-s", "--settings", default=SETTINGS, type=str, nargs="?")
    parser.add_argument("-S", "--secrets", default=SECRETS, type=str, nargs="?")
    args = parser.parse_args()
    if args.init:
        args.init.lower()
    return init(args.init, args.settings, args.secrets)


if __name__ == "__main__":
    main()
