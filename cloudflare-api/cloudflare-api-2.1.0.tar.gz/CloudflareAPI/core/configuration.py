#!/usr/bin/env python3

from pathlib import Path
from getpass import getpass
from typing import Optional
from configparser import ConfigParser


class Config:
    CONFIG_FILE = "cf-config.ini"
    ROOT_DIR = Path(".").parent.parent.parent

    def __init__(self, file: Optional[str] = None) -> None:
        if file is not None:
            self.CONFIG_FILE = file
        self.__file = (self.ROOT_DIR / self.CONFIG_FILE).resolve()
        self.__config = ConfigParser()
        self.__token: Optional[str] = None

    def __read_token(self) -> str:
        if self.__token is None or not self.__token:
            self.__config.read(self.__file)
            if "Cloudflare" in self.__config:
                if "token" in self.__config["Cloudflare"]:
                    return self.__config["Cloudflare"]["token"]
            self.read_from_user()
        return self.__token

    def __write_token(self, token: str) -> None:
        self.__config["Cloudflare"] = {"token": token}
        with self.__file.open("w") as cf:
            self.__config.write(cf)
        self.__token = token

    def read_from_user(self) -> None:
        token = getpass("Please enter Cloudflare API Token: ")
        self.__write_token(token)
        print("Successfully stored api key")

    @property
    def token(self) -> str:
        return self.__read_token()

    @token.setter
    def token(self, value: str) -> None:
        self.__write_token(value)
