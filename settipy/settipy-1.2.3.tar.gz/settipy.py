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
        self.truthy = {"y", "yes", "true", ""}
        self.casters = {
            "str": self._to_str,
            "int": self._to_int,
            "bool": self._truthiness,
            "list": self._to_list,
            "dict": self._to_dict,
        }
        self.list_sep = {}
        self.dict_seps = {}
        self.should_be_set = {}

    def _to_str(self, v, flag):
        return str(v)

    def _to_int(self, v, flag):
        return int(v)

    def _to_list(self, v, flag):
        return v.split(self.list_sep[flag])

    def _to_dict(self, v, flag):
        item_sep, key_sep, sep = self.dict_seps[flag]
        d = {}
        for item in v.split(item_sep):
            key, values = item.split(key_sep)
            d[key] = values.split(sep)
        return d

    def _truthiness(self, v, flag):
        return v in self.truthy

    def _cast(self, v, flag):
        type_ = self.data_type[flag]
        return self.casters[type_](v, flag)

    def _set(self, flag_name, default, message, type_, should):
        self.data[flag_name] = default
        self.data_type[flag_name] = type_
        self.messages[flag_name] = message
        if should:
            self.should_be_set[flag_name] = default

    def set(self, flag_name, default, message, type_="str", should=False):
        self._set(flag_name, default, message, type_, should)

    def set_int(self, flag_name, default, message, should=False):
        self._set(flag_name, default, message, "int", should)

    def set_bool(self, flag_name, default, message, should=False):
        self._set(flag_name, default, message, "bool", should)

    def set_list(self, flag_name, default, message, sep=",", should=False):
        self.list_sep[flag_name] = sep
        self._set(flag_name, default, message, "list", should)

    def set_dict(self, flag_name, default, message, sep=",", key_sep=":", item_sep=";", should=False):
        self.dict_seps[flag_name] = item_sep, key_sep, sep
        self._set(flag_name, default, message, "dict", should)

    def get(self, k):
        return self.data[k]

    def get_int(self, k):
        return self.data[k]

    def get_bool(self, k):
        return self.data[k]

    def get_list(self, k):
        return self.data[k]

    def get_dict(self, k):
        return self.data[k]

    def _get_env_var(self, flag):
        return os.environ.get(flag), flag in os.environ

    def _parse_cli(self, pos):
        pos += 1
        result = sys.argv[pos] if len(sys.argv) > pos else ""
        if result[:1] == "-" or result[:2] == "--":
            result = ""
        return result

    def _get_cli_var(self, flag):
        if "-" + flag in sys.argv:
            pos = sys.argv.index("-" + flag)
            return self._parse_cli(pos), True

        if "--" + flag in sys.argv:
            pos = sys.argv.index("--" + flag)
            return self._parse_cli(pos), True

        return None, False

    def _handle_env_vars(self):
        for flag in self.data.keys():
            value, found = self._get_env_var(flag)
            if found:
                self.should_be_set.pop(flag, None)
                self.data[flag] = self._cast(value, flag)

    def _handle_cli_vars(self):
        for flag in self.data.keys():
            value, found = self._get_cli_var(flag)
            if found:
                self.should_be_set.pop(flag, None)
                self.data[flag] = self._cast(value, flag)

    def _handle_help(self):
        if "--help" in sys.argv:
            print(f"usage of {sys.argv[0]}")
            for flag, default in self.data.items():
                type_, message = self.data_type[flag], self.messages[flag]
                print(f"\t-{flag} {type_} - default: {default}")
                print(f"\t\t{message}")
            sys.exit()

    def _handle_should(self):
        if not self.should_be_set:
            return

        for flag, value in self.should_be_set.items():
            message = self.messages[flag]
            print(f"flag: {flag} {message}: should be set")
        sys.exit(1)

    def parse(self):
        self._handle_help()
        self._handle_env_vars()
        self._handle_cli_vars()
        self._handle_should()
        self.parsed = True


settipy = Settipy()
