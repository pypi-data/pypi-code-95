import os
import pprint

from pathlib import Path
import json
import base64

import ast
import fk.utils
import logging

logger = logging.getLogger(__name__)

# IMPORTANT!!!!!!
# DO NOT PUT REAL CONFIG HERE, ESPECIALLY PASSWORDS AND OTHER SENSITIVE DATA!!!!
unset = "PLEASE OVERRIDE THIS DEFAULT"
defaults = {
    "DEBUG": False,
    "TESTING": False,
    "SECRET_KEY": base64.b64encode(os.urandom(16)).decode("utf-8"),
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_ECHO": False,
    "SQLALCHEMY_TRACK_MODIFICATIONS": True,
    "batch-filter-root": "/app/fk/batch/filters",
    "cache-dir-name": "_cache",
    "crawler-html-parser": "html5lib",
    "crawler-referer": "https://www.shopify.com/",
    "crawler-socket-timeout": 15,
    "crawler-user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "db-database": "postgres",
    "db-hostname": "localhost",
    "db-password": unset,
    "db-port": "5432",
    "db-username": unset,
    "smtp-hostname": unset,
    "smtp-port": "2525",
    "smtp-user": unset,
    "smtp-password": unset,
    "smtp-headers": unset,
    "influx-dbname": "sales",
    "influx-hostname": "localhost",
    "influx-password": unset,
    "influx-port": "8086",
    "influx-username": unset,
    "n2report-dir-name": "_n2report",
    "n2report-index-name": "index.html",
    "overwatch-password": unset,
    "overwatch-user": unset,
    "preferred-url-scheme": "http",
    "printful-api-endpoint": "https://api.printful.com/",
    "printful-api-key": unset,
    "printful-api-key-base64": unset,
    "screenshots-dir-name": "_screenshots",
    "screenshots-index-name": "screenshots.html",
    "shop-id-generator-batch-size": 200,
    "shop-id-generator-max": 25000000000,  # billions
    "shop-id-generator-min": 0,
    "shop-id-thread-count": 300,
    "shopify-api-key": unset,
    "shopify-api-secret": unset,
    "shopify-api-throttle-limit": 1,
    "shopify-api-throttle-period": 3000,
    "shopify-api-version": "2020-10",
    "shopify-app-domain": unset,
    "shopify-app-author": "The author of this app",
    "shopify-app-author-email": "The email of the author of this app",
    "shopify-app-company-name": "The name of the company behind this app",
    "shopify-app-company-website": "The url fo the company website",
    "shopify-app-description": "The description of this app",
    "shopify-app-name": "The name of this app",
    "shopify-app-preferred-url-scheme": "https",
    "shopify-password": unset,
    "shopify-shared-secret": unset,
    "static-files-root": "/app/shopify_app/static",
    "webdriver-max-windows": 5,
    "webdriver-url": "http://127.0.0.1:4444/wd/hub",
    "webdriver-wait-time-sec": 10,
    # "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
    # SHOPIFY_SHOP_NAME = 'firstkissdesigns'
    # https://flask.palletsprojects.com/en/1.1.x/config/#DEBUG
    # https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
    # SERVER_NAME = "localhost.localdomain:5000"
    # https://flask.palletsprojects.com/en/1.1.x/config/#TESTING
}


class Config(dict):
    def __init__(self):
        super().__init__()
        self.sources = {}

    """Helper to parse boolean from environment variable"""

    def TO_BOOL(str):
        if str.lower() in {"1", "t", "true"}:
            return True
        elif str.lower() in {"0", "f", "false"}:
            return False
        return None

    """Helper to parse unsigned integer from environment variable"""
    # With help from https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except
    def TO_UINT(str):
        if str.isdigit():
            return int(str)
        if str.startswith("+") and str[1:].isdigit():
            return int(str)
        return None

    """Helper to parse signed integer from environment variable"""

    def TO_INT(str):
        if str.isdigit():
            return int(str)
        if str.startswith(("+", "-")) and str[1:].isdigit():
            return int(str)
        return None

    """Helper to convert a string to environment variable name on the form THIS_IS_ENV_VARIABLE"""

    def TO_ENV_KEY(str):
        str = str.strip().upper()
        for i in ["-", " ", "\t"]:
            str = str.replace(i, "_")
        return str

    """Helper to convert a string to a native python type"""

    def TO_GUESS_TYPE(str):
        b = Config.TO_BOOL(str)
        if b is not None:
            return b
        ret = str
        try:
            ret = ast.literal_eval(str)
        except:
            pass
        return ret

    # @property
    # def DATABASE_URI(self):         # Note: all caps
    #    return 'mysql://user@{}/foo'.format(self.DB_SERVER)

    """Helper to load configuration values from environment variables"""

    def apply_environment_variables(self):
        ct = 0
        for key, value in self.items():
            env_key = Config.TO_ENV_KEY(key)
            env_value = os.environ.get(env_key, default=None)
            if env_value:
                self[key] = Config.TO_GUESS_TYPE(env_value)
                self.sources[key] = "environment"
                ct += 1
                # logger.info(f"Value from env '{env_value}' replaced '{value}' for key '{key}'")
            else:
                # logger.warning(f"WARNING: No {env_key} in env, using last value '{key}' = {value}")
                pass
        logger.info(f"Put {ct} values from environment variables into configuration")
        return True

    def apply_dict(self, other, source="dict"):
        ct = 0
        for key, value in self.items():
            file_value = other.get(key, None)
            if file_value:
                self[key] = file_value
                self.sources[key] = source
                ct += 1
                # logger.info(f"Value from file '{file_value}' replaced '{value}' for key '{key}'")
            else:
                # logger.warning(f"WARNING: No {key} in file, using last value '{value}'")
                pass
        return ct

    """Helper to load configuration values from configuration file in json format"""

    def apply_config_file(self, filename, create_if_missing=True):
        file = Path(filename)
        # Create a config file with defaults if none exists
        if not file.is_file():
            if create_if_missing:
                logger.info(f"Config file '{filename}' did not exist, creating")
                with open(filename, "w") as outfile:
                    json.dump(defaults, outfile, ensure_ascii=False, sort_keys=True, indent=3)
            else:
                logger.info(f"Config file '{filename}' did not exist, skipping")
                logger.info(f"NOTE: current dir was: {os.getcwd()}")
                return False
        # Load config from file
        loaded_config = {}
        if not os.path.exists(filename):
            logger.error(f"ERROR: Could not find '{filename}'")
            return False
        with open(filename, "r") as json_file:
            logger.info(f"Loading config from '{filename}'")
            try:
                loaded_config = json.load(json_file)
                ct = self.apply_dict(loaded_config, filename)
                logger.info(f"Put {ct} values from file variables into configuration")
            except Exception as e:
                logger.error(f"\nParsing json from config file '{filename}' failed:\n{e}\n", exc_info=True)
                return False
        return True

    def list_unchanged(self):
        """ List all variables that have not been changed from their default setting"""
        logger.info(f"Unchanged configurations options:")
        for key, value in defaults.items():
            if self.get(key) == value:
                logger.info(f"{key}={value}")

    def members(self):
        ret = {}
        base = self  # .__class__
        for member in [attr for attr in dir(base) if not callable(getattr(base, attr)) and not attr.startswith("__")]:
            val = getattr(base, member)
            ret[member] = val
        return ret

    def redact_key(self, key, val, num=20, source="redact"):
        if source in ["default", "none"]:
            return val
        if any(x in key.lower() for x in ["secret", "pass", "pwd", "key", "psk"]):
            val = fk.utils.redact(val, num)
        return val

    def __repr__(self):
        dict = self.members()
        ret = f"\n########## Configuration options for {self.__class__.__name__}:\n"
        order = {"none": {}, "default": {}}
        for key, val in dict.items():
            if self.sources != val:
                source = self.sources.get(key, "none")
                order[source] = order.get(source, {})
                order[source][key] = val
        for source, items in order.items():
            if len(items) > 0:
                ret += f"[{source}]\n"
                for key, val in items.items():
                    ret += f" + {key} = {self.redact_key(key, val)}\n"
        return ret

    def redacted_dict(self) -> dict:
        out_dict = dict(self.members())
        for key, val in out_dict.items():
            out_dict[key] = self.redact_key(key, val)
        return out_dict

    def attrify(self):
        for key, val in self.items():
            # logger.debug(f" + {key} = {self.redact_key(key, val)}")
            setattr(self.__class__, key, val)


class DefaultConfig(Config):
    """The default base configuration to be extended by actual configurations to be used"""

    def __init__(self):
        super().__init__()
        self.update(defaults)
        self.sources = {k: "default" for k in self.keys()}

    """Helper to check validity of configuration"""

    def verify(self):
        defkey = []
        for key in ["printful-api-key"]:
            if self.get(key, None) == defaults.get(key, None):
                defkey.append(key)
        if defkey:
            logger.warning(f"Config contains default values for the following keys: '{', '.join(defkey)}'\n        If there are any authentication error this might be the culprit.")

        # Printify needs printful-api-key base64 encoded, so do that now b64encode
        pak = self.get("printful-api-key", None)
        if pak:
            self["printful-api-key-base64"] = str(base64.urlsafe_b64encode(pak.encode("utf-8")).strip(), "utf-8")


"""Configuration that combines defaults with whatever environment variables are set"""


class EnvironmentConfig(DefaultConfig):
    def __init__(self):
        super().__init__()


#        self.apply_environment_variables()


if __name__ == "__main__":
    # Change current working dir to that of this script's location
    cwd = os.path.dirname(os.path.realpath(__file__))
    os.chdir(cwd)
    print("Set working dir to " + cwd)
    print("Config ################################################################")
    c = Config()
    print("---------")
    c.attrify()
    print("---------")
    print(f"CONFIG={c}")
    print("DefaultConfig ################################################################")
    dc = DefaultConfig()
    print("---------")
    dc.verify()
    print("---------")
    dc.attrify()
    print("---------")
    print(f"CONFIG={dc}")
    print("EnvironmentConfig ################################################################")
    ec = EnvironmentConfig()
    print("---------")
    ec.verify()
    print("---------")
    ec.attrify()
    print("---------")
    print(f"CONFIG={ec}")
    print("################################################################")
