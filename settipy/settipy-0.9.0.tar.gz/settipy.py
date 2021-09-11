import os
import sys


class Settipy():
    """
        >>> type("").__name__
        'str'
        >>> type(1).__name__
        'int'
        >>> type(True).__name__
        'bool'
    """
    def __init__(self):
        self.parsed = False
        self.data = {}
        self.data_type = {}
        self.messages = {}
        self.truthy = {"y", "yes", "true"}
        self.casters = {"str": str, "int": int}

    def truthiness(self, v):
        return v in self.thruthy

    def cast(self, v, flag):
        type_ = self.data_type[flag]
        if type_ == "bool":
            return self.truthiness(v)
        return self.casters[type_](v)

    def set(self, flag_name, default, message, type_="str"):
        self.data[flag_name] = default
        self.data_type[flag_name] = type_
        self.messages[flag_name] = message

    def set_int(self, flag_name, default, message):
        self.data[flag_name] = int(default)
        self.data_type[flag_name] = "int"
        self.messages[flag_name] = message

    def set_bool(self, flag_name, default, message):
        self.data[flag_name] = default
        self.data_type[flag_name] = "bool"
        self.messages[flag_name] = message

    def get(self, k):
        return self.data[k]

    def get_int(self, k):
        return self.data[k]

    def get_bool(self, k):
        return self.data[k]

    def get_env_var(self, flag):
        return os.environ.get(flag), flag in os.environ

    def get_cli_var(self, flag):
        if "-" + flag in sys.argv:
            pos = sys.argv.index("-" + flag)
            return self.cast(sys.argv[pos+1]), True

        if "--" + flag in sys.argv:
            pos = sys.argv.index("--" + flag)
            return sys.argv[pos+1], True
        return None, False

    def handle_env_vars(self):
        for flag in self.data.keys():
            value, found = self.get_env_var(flag)
            if found:
                self.data[flag] = self.cast(value, flag)

    def handle_cli_vars(self):
        for flag in self.data.keys():
            value, found = self.get_cli_var(flag)
            if found:
                self.data[flag] = self.cast(value, flag)

    def handle_help(self):
        if "--help" in sys.argv:
            print(f"usage of {sys.argv[0]}")
            for flag, default in self.data.items():
                type_, message = self.data_type[flag], self.messages[flag]
                print(f"\t-{flag} {type_} - default: {default}")
                print(f"\t\t{message}")
            sys.exit()

    def parse(self):
        self.handle_help()
        self.handle_env_vars()
        self.handle_cli_vars()
        self.parsed = True


settipy = Settipy()
