from unswamp.objects.checks.base.BaseCheck import BaseCheck


class BaseArgumentsCheck(BaseCheck):
    arguments = set()
    __internal_keys = set({"result", "dataset"})

    def __init__(self, id, arguments, active, level, meta_data):
        BaseCheck.__init__(self, id, active, level, meta_data)
        self.arguments = arguments

    def _args_check(self, fx_vars):
        keys = set(self.arguments.keys())
        keys.update(self.__internal_keys)

        if fx_vars != keys:
            missing = fx_vars.difference(keys)
            raise ValueError(
                f"the following keys are missing in args dict '{missing}'")

    @staticmethod
    def _check(obj):
        BaseCheck._check(obj)
        if isinstance(obj, BaseArgumentsCheck):
            if obj.arguments is None:
                raise ValueError(
                    f"arguments should not be None!")
        else:
            raise TypeError(
                f"object of type '{type(obj)}' is not of type '{type(BaseArgumentsCheck)}'!"
            )

