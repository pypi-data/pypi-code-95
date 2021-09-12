"""
base class for converter
"""


class BaseConverter:
    def execute(self, args):
        """execute converting steps by args parsed from cmd"""
        raise NotImplementedError
