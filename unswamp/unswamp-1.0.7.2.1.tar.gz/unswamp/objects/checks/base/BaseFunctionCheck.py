from copy import copy
from unswamp.objects.checks.base.BaseCheck import BaseCheck
from unswamp.objects.checks.base.BaseArgumentsCheck import BaseArgumentsCheck
from unswamp.objects.checks.CheckFunctions import CheckFunctions


class BaseFunctionCheck(BaseCheck):
    function_key = None

    def __init__(self, id, function_key, active, level, meta_data):
        BaseCheck.__init__(self, id, active, level, meta_data)
        CheckFunctions.check_function_keys(function_key)
        self.function_key = function_key

    @staticmethod
    def _check(obj):
        BaseCheck._check(obj)
        if isinstance(obj, BaseFunctionCheck):
            if obj.function_key is None:
                raise ValueError(
                    f"function_key should not be None!")
            if obj.function is None:
                raise ValueError(
                    f"function should not be None!")
            if obj.function_description is None:
                raise ValueError(
                    f"function_description should not be None!")
        else:
            raise TypeError(
                f"object of type '{type(obj)}' is not of type '{type(BaseFunctionCheck)}'!"
            )

    @property
    def function_description(self):
        if not isinstance(self, BaseArgumentsCheck):
            raise TypeError(
                f"object of type '{type(self)}' is not of type '{type(BaseArgumentsCheck)}'")

        function_description = CheckFunctions.function_descriptions[self.function_key]
        curr_args = copy(self.arguments)
        curr_args["function"] = CheckFunctions.get_function_string(
            self.function)
        args = CheckFunctions.get_string_args(curr_args, function_description)
        function_description = function_description.format(**args)
        return function_description

    @property
    def function(self):
        function = CheckFunctions.functions[self.function_key]
        return function
