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
        self.print_at_startup = False
        self.data = {}
        self.data_type = {}
        self.messages = {}
        self.data_set = set()
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
        self.conditional_should = {}
        self.options = {}
        self.password_fields = {}

        self.test_mode = False

    def __getitem__(self, key):
        return self.data[key]

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

    def _set(self, flag_name, default, message, type_, should, should_if, options, password):
        self.data[flag_name] = default
        self.data_type[flag_name] = type_
        self.messages[flag_name] = message
        if should:
            self.should_be_set[flag_name] = default
        if options:
            self.options[flag_name] = set(options)
        if password:
            self.password_fields[flag_name] = True
        if should_if:
            self.conditional_should[flag_name] = set(should_if)

    def set(self, flag_name, default, message, type_="str", should=False, should_if=tuple(), options=tuple(), password=False):
        self._set(flag_name, default, message, type_, should, should_if, options, password)

    def set_int(self, flag_name, default, message, should=False, should_if=tuple(), options=tuple(), password=False):
        self._set(flag_name, default, message, "int", should, should_if, options, password)

    def set_bool(self, flag_name, default, message, should=False, should_if=tuple(), options=tuple(), password=False):
        self._set(flag_name, default, message, "bool", should, should_if, options, password)

    def set_list(self, flag_name, default, message, sep=",", should=False, should_if=tuple(), options=tuple(), password=False):
        self.list_sep[flag_name] = sep
        self._set(flag_name, default, message, "list", should, should_if, options, password)

    def set_dict(self, flag_name, default, message, sep=",", key_sep=":", item_sep=";", should=False, should_if=tuple(), options=tuple(), password=False):
        self.dict_seps[flag_name] = item_sep, key_sep, sep
        self._set(flag_name, default, message, "dict", should, should_if, options, password)

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
                self.data_set.add(flag)
                self.data[flag] = self._cast(value, flag)

    def _handle_cli_vars(self):
        for flag in self.data.keys():
            value, found = self._get_cli_var(flag)
            if found:
                self.data_set.add(flag)
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
        """If value "should" be set, we expect the value or exit the program with error.
        This will allow devs, admins to handle the issue at startup.
        """

        success = True
        if not self.should_be_set:
            return success

        for flag, value in self.should_be_set.items():
            if flag in self.data_set:
                continue
            success = False
            if not self.test_mode:
                message = self.messages[flag]
                print(f"flag: {flag} {message}: should be set")

        return success

    def _handle_conditional_should(self):
        """If value "should" be set, we expect the value or exit the program with error.
        This will allow devs, admins to handle the issue at startup.
        """
        success = True
        if not self.conditional_should:
            return success

        for flag, value in self.conditional_should.items():
            if flag in self.data_set:
                continue
            if value.issubset(self.data_set):
                success = False
                if not self.test_mode:
                    print(f"flag: {flag} if one of the following flags are set then this flag must be set {value}")
        return success

    def _handle_options(self):
        success = True
        if not self.options:
            return success

        for flag, allowed_options in self.options.items():
            value = self.data[flag]
            if value not in allowed_options:
                success = False
                if not self.test_mode:
                    print(f"flag: {flag} {value}: is not part of allowed options")
        return success

    def _handle_print(self):
        if self.print_at_startup or "--settipy-verbose" in sys.argv:
            print(self.print_at_startup, "--settipy-verbose" in sys.argv)
            print(f"starting {sys.argv[0]} with vars:")
            for flag, default in self.data.items():
                if not self.password_fields.get(flag):
                    print(f"\t-{flag}: {default}")

    def _handle_clean(self):
        self.data_type = None
        self.messages = None
        self.data_set = None
        self.truthy = None
        self.casters = None
        self.list_sep = None
        self.dict_seps = None
        self.should_be_set = None
        self.conditional_should = None
        self.options = None
        self.password_fields = None

    def parse(self, verbose=False):
        if verbose:
            self.print_at_startup = True

        if self.parsed:
            raise Exception("There is a saying... If you're parsed you can't be parsed again")

        self._handle_help()
        self._handle_print()
        self._handle_env_vars()
        self._handle_cli_vars()
        succeded = self._handle_should()
        succeded = succeded and self._handle_conditional_should()
        succeded = succeded and self._handle_options()
        if not succeded:
            if self.test_mode:
                raise Exception
            sys.exit(1)

        self._handle_clean()
        self.parsed = True


settipy = Settipy()
