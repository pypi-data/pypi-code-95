import os
import configparser
import cachetools
import io


DEFAULT_GROUP = "default"


class BaseStore:
    FILE_NAME = None
    CACHE = cachetools.Cache(maxsize=1)

    @classmethod
    def get_config_dir(cls):
        paths = [os.path.expanduser("~"), "/tmp"]
        for path in paths:
            writable = os.access(path, os.W_OK)
            if writable:
                return path

        return None

    @classmethod
    def get_file_path(cls, *, create=True):
        if cls.FILE_NAME is None:
            raise NotImplementedError(
                "You must implement BaseStore and override FILE_NAME"
            )

        home_path = cls.get_config_dir()
        if home_path is None:
            return None

        base_path = os.path.join(home_path, ".config")
        dir_path = os.path.join(base_path, "alfa")
        if create:
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        return os.path.join(dir_path, cls.FILE_NAME)

    @classmethod
    def get_store(cls):
        path = cls.get_file_path()
        store = configparser.ConfigParser(default_section=DEFAULT_GROUP)

        if path is None:
            confstring = cls.CACHE.get(cls.FILE_NAME, "")
            store.read_string(confstring)
        elif os.path.isfile(path):
            store.read(path)
        return store

    @classmethod
    def get_group(cls, group=DEFAULT_GROUP):
        store = cls.get_store()
        if group in store:
            return store[group]

        return None

    @classmethod
    def purge(cls):
        path = cls.get_file_path()
        if path is None:
            cls.CACHE[cls.FILE_NAME] = None
        elif os.path.isfile(path):
            os.remove(path)

    #

    @classmethod
    def get_value(cls, key, default=None, *, group=DEFAULT_GROUP, is_boolean=False):
        store = cls.get_store()

        if group not in store or key not in store[group]:
            return default

        if is_boolean:
            return store[group].getboolean(key)
        return store[group][key]

    @classmethod
    def set_value(cls, key, value, *, group=DEFAULT_GROUP):
        keyvalues = {}
        keyvalues[key] = value
        cls.set_values(keyvalues, group=group)

    @classmethod
    def set_values(cls, keyvalues, *, group=DEFAULT_GROUP):
        path = cls.get_file_path()
        store = cls.get_store()

        if group not in store:
            store[group] = {}

        for key, value in keyvalues.items():
            if type(value) is bool:
                value = str(value).lower()
            store[group][key] = value

        if path is None:
            file = io.StringIO()
            store.write(file)
            cls.CACHE[cls.FILE_NAME] = file.getvalue()
        else:
            with open(path, "w") as file:
                store.write(file)


class AuthStore(BaseStore):
    FILE_NAME = "credentials"


class ConfigStore(BaseStore):
    FILE_NAME = "config"
