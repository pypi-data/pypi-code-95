from pprint import pformat
import json
from collections import defaultdict

__all__ = [
    'BaseAttrDict',
    'AttrDict',
]


class BaseAttrDict(dict):
    """
        Attributes-dict bounded structure for paramenters
        -> When a dictionary key is set the corresponding attribute is set
        -> When an attribute is set the corresponding dictionary key is set

        Usage:

            # Create the object
            args = AttrDict()
            
            args.a = 1
            print(args.a) # 1
            print(args['a']) # 1

            args['b'] = 2
            print(args.b) # 2
            print(args['b']) # 2

    """
    def __init__(self, *args, **kwargs):
        super(BaseAttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def repr(self):
        return dict(self)

    def __repr__(self):
        return pformat(self.repr())

    def __str__(self):
        return self.__repr__()

    def update_defaults(self, d):
        for k, v in d.items():
            self.setdefault(k, v)

    def save_json(self, file_name):
        with open(file_name, 'w') as fp:
            json.dump(self.repr(), fp)


class NoDefault(object):
    pass


class AttrDict(BaseAttrDict):
    """
        Attributes-dict bounded structure for paramenters
        -> When a dictionary key is set the corresponding attribute is set
        -> When an attribute is set the corresponding dictionary key is set

        - It provides parameter type checking functionalities
        - It allows passing other custom checks (via functions)
        - It allows passing parameter pre-processing functions (that function is applied to the parameter)

        Usage:

            # Create the object
            args = AttrDict()

            # Set paramenters and/or types
            args.PAR = val
            args.set_type('PAR', [int, float], compulsory = True)

            # Run the pre-processing and checks types
            args.load()

        TODO: Need to be retested after refactoring

    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        for k, v in self.items():
            if isinstance(v, str) and v == 'None':
                self[k] = None
        self.__types = defaultdict(list)
        self.__compulsory = []
        self.__preprocess = {}
        self.__custom_check = {}
        self.__default = {}
        self.__globals = {}

    def repr(self):
        return {k: v for k, v in self.items() if not k.startswith('_AttrDict__')}

    def set_type(self, arg_name, types=[], compulsory=False, check_fun=None, pre_fun=None, default=NoDefault()):
        if compulsory:
            self.__compulsory.append(arg_name)
        if isinstance(types, list):
            for t in types:
                self.__types[arg_name].append(t if (t is not None) else type(None))
        else:
            self.__types[arg_name].append(types)
        if pre_fun is not None:
            self.__preprocess[arg_name] = pre_fun
        if check_fun is not None:
            self.__custom_check[arg_name] = check_fun
        if not isinstance(default, NoDefault):
            self.__default[arg_name] = default

    def load(self, globals_vars=None, check=True):
        self.__set_globals(globals_vars)
        self.__pre_process()
        if check:
            self.__check_types()
        self.__defaults()
        return True

    def assign_arguments(self, hyperargs, args_names):
        for arg_name, value in zip(args_names, hyperargs):
            self[arg_name] = value
        assert self.load()
        return AttrDict(self)

    def __defaults(self):
        for arg_name, default in self.__default.items():
            if arg_name not in self:
                self[arg_name] = default

    def __set_globals(self, globals_vars, prefix="GLOBAL_"):
        if globals_vars is not None:
            for var in self:
                if not var.startswith('_'):
                    if 'GLOBAL_' + var in globals_vars:
                        print(
                            f'ATTENTION: Setting {var} to {globals_vars[prefix + var]} (instead of {self[var]}) because {prefix + var} is set'
                        )
                        self[var] = globals_vars[prefix + var]

    def __check_type(self, arg_name):
        for t in self.__types[arg_name]:
            if isinstance(self[arg_name], t):
                return True
        return False

    def __check_types(self):
        for arg_name in self.__compulsory:
            assert arg_name in self, f"{arg_name} is COMPULSORY!"
        for arg_name in self.__types:
            if arg_name in self:
                assert self.__check_type(arg_name), f"{arg_name} has a NON-ALLOWED TYPE! ({self.__types[arg_name]})"
        for arg_name, fun in self.__custom_check.items():
            if arg_name in self:
                assert fun(self[arg_name]), f"{arg_name} did not pass the CUSTOM CHECK!"

    def __pre_process(self):
        for arg_name, fun in self.__preprocess.items():
            if arg_name in self:
                self[arg_name] = fun(self[arg_name])