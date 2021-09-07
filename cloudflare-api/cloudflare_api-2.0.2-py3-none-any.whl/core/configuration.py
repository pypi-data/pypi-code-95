from pathlib import Path
from getpass import getpass
from configparser import ConfigParser


DEFAULT_CONFIG_FILE = "cf.ini"


class Config:
    def __init__(self) -> None:
        config_file = Path(DEFAULT_CONFIG_FILE).resolve()
        self.__config = ConfigParser()
        if not config_file.exists():
            self.__write_token(config_file)
        self.__token = self.__read_token(config_file)

    def __read_token(self, config_file: Path) -> str:
        self.__config.read(config_file)
        if "Cloudflare" in self.__config:
            if "token" in self.__config["Cloudflare"]:
                return self.__config["Cloudflare"]["token"]
        raise AttributeError("Invalid configuration file")

    def __write_token(self, config_file: Path) -> None:
        token = getpass("Please enter Cloudflare API Token: ")
        self.__config["Cloudflare"] = {"token": token}
        with config_file.open("w") as cf:
            self.__config.write(cf)
        print("Successfully stored api key")

    def token(self) -> str:
        return self.__token

config = Config()