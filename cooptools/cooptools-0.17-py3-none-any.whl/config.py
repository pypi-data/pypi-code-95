from configparser import ConfigParser
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ConfigStateException(Exception):
    def __init__(self, txt: str = None):
        logger.error(txt)
        super().__init__(txt)

class ConfigStateFactory:

    def __init__(self,
                 config_definition_dict: Dict[str, Any],
                 config_file_path: str = None,
                 config_file_header:str = None):

        if config_definition_dict is None:
            raise ConfigStateException(f"config_definition_dict cannot be None")

        if config_file_path is not None and not os.path.isfile(config_file_path):
            raise ConfigStateException(f"config_file_path {config_file_path} does not exist.")

        self.parser = ConfigParser()
        self.current_file_path = config_file_path
        self.current_file_header = config_file_header
        self._config_definition_dict = config_definition_dict

        self.loaded = False

        self._q = type('accessor', (object,), self._config_definition_dict)

        self._try_load_pass(config_file_path, config_file_header)

    def __getitem__(self, item):
        return self.get_config(item)

    def _try_load_pass(self, config_file_path:str, config_file_header: str):
        try:
            self.load_from_file(config_file_path=config_file_path, config_file_header=config_file_header)
        except:
            pass
        finally:
            # set attributes
            for k, v in self._config_definition_dict.items():
                setattr(self, k, self._try_access_parser_default(config_file_header, k, v))

    def _config_file_exists(self):
        return os.path.isfile(self.current_file_path)

    def load_from_file(self, config_file_path: str = None, config_file_header: str = None):
        if config_file_path is not None:
            self.current_file_path = config_file_path

        if config_file_header is not None:
            self.current_file_header = config_file_header

        if not self._config_file_exists():
            issue = f"Unable to load config from directory: \"{self.current_file_path}\" does not exist"
            raise ConfigStateException(issue)

        try:
            self.parser.read(self.current_file_path)
            logger.info(f"Config set from directory: {self.current_file_path}")
            self.loaded = True
        except Exception as e:
            issue = f"Unable to load config from directory: {self.current_file_path}" \
                    f"\n{e}"
            raise ConfigStateException(issue) from e

    def _try_access_parser_default(self, header, name, default):
        if self.loaded:
            try:
                return self.parser.get(header, name)
            except Exception as e:
                raise ConfigStateException(str(e)) from e
        else:
            try:
                return default()
            except:
                return default

    def _get_config(self, header, name):
        if name not in self._config_definition_dict.keys():
            raise ConfigStateException(f"Requested config [\"{name}\"] was not defined")
        default = self._config_definition_dict[name]
        val = self._try_access_parser_default(header, name, default)
        logger.debug(f"Value for {header}|{name}: {val}")
        return val

    def get_config(self, name):
        return self._get_config(self.current_file_header, name)

    @property
    def config_dir(self):
        return os.path.dirname(self.current_file_path)

    @property
    def config_file_path(self):
        return self.current_file_path


if __name__ == "__main__":
    my_dict = {"a": None,
               "b": 2,
               "c": "TRYIT",
               "d": lambda: 123}

    con = ConfigStateFactory(my_dict)

    print(con.get_config("a"), con.get_config("b"), con.get_config("c"))

    print(con.a, con.b, con.c, con.d)
    print(con["b"])

