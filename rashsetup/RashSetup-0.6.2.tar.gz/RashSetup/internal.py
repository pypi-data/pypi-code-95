import importlib
import sys
import subprocess
import sqlite3
import pathlib
import shutil
import logging
import typing

import RashSetup as RashSetup

from .crawlers import *

__all__ = ["ModuleManager", "DBManager"]

__all__.extend(ALL)


class ModulePathManager:
    def __init__(self):
        self.mod = pathlib.Path(__file__).parent / "__RashModules__"
        self.mod.mkdir(exist_ok=True)

        _ = self.mod / "__init__.py"
        None if _.exists() else _.write_text("")

    def check_module(self, name, path=None):
        path = path if path else self.mod
        return all(
            (
                (path / name).exists(),
                (path / name / "__init__.py").exists(),
                (path / name / "settings.json").exists(),
            )
        )

    def uninstall_module(self, name):
        shutil.rmtree(self.mod / name)

    def gen_path(self, name, create=True):
        mod = self.mod / name
        mod.mkdir(exist_ok=True) if create else None
        return self.mod / name

    def settings(self, module):
        return SettingsParser(self.gen_path(module) / "settings.json", True)


class DBManager(ModulePathManager):
    def __init__(self):
        super().__init__()
        self.sql = self.mod.parent / "__RashSQL__.sql"
        self.connector = sqlite3.connect(
            self.mod / "__RashModules__.db", check_same_thread=False
        )

        self.__start()

    def cursor(self):
        return self.connector.cursor()

    def __start(self):
        temp = self.cursor()
        temp.executescript(self.sql.read_text())
        self.connector.commit()
        temp.close()

    def sql_code(self, code, *args) -> tuple:
        return self.execute_one_line(
            *self.execute_one_line(
                "SELECT SQL, Empty FROM Sql WHERE Hash = ?", False, code
            ),
            *args
        )

    def execute_one_line(self, script, all_=False, *args):
        temp = self.cursor()
        temp.execute(script, args)

        return temp.fetchall() if all_ else temp.fetchone()

    def commit(self):
        self.connector.commit()

    def close(self):
        self.connector.close()

    def add(self, name, hosted, version, readme):
        self.sql_code(10, name, hosted, version, readme)

        self.commit()

    def update_settings(self, name, version, readme=None):
        self.sql_code(8, version, name)
        self.sql_code(9, readme, name) if readme else None

        self.commit()


class HeavyModuleManager(DBManager):
    def download(self, name: str, url: typing.Optional[str] = None, _=None):
        url = url if url else self.sql_code(3, name)[0]
        path = str(self.gen_path(name))

        setup = RawSetup(RepoSetup, url, path)
        setup.process.start()
        setup.process.join()

        return setup.parse()

    def grab_readme(self, url):
        setup = RawSetup(READMESetup, url)
        setup.process.start()
        setup.process.join()

        status, result = setup.parse()

        if not status:
            return ""

        return result

    def check_for_update(self, *args, **_):
        pass

    def update_settings(self, settings: SettingsParser, *_) -> None:
        return super().update_settings(
            settings.name(), settings.version(), settings.readme()
        )


class ModuleManager(HeavyModuleManager):
    def __init__(self):
        super().__init__()

    def check(self):
        for module in self.sql_code(1):
            module: str = module[0]

            if self.check_module(module):
                continue

            yield module


if __name__ == "__main__":
    import __RashModules__.Rash.Start as Rash

    Application = Rash.Start()
    Application.start()
