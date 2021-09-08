from copy import copy
from unswamp.objects.checks.base.BaseCheck import BaseCheck
from unswamp.objects.checks.base.BaseArgumentsCheck import BaseArgumentsCheck
from unswamp.objects.checks.CheckFunctions import CheckFunctions


class BaseExpectationCheck(BaseCheck):
    expectation_key = None

    def __init__(self, id, expectation_key, active, level, meta_data):
        BaseCheck.__init__(self, id, active, level, meta_data)
        CheckFunctions.check_expectation_keys(expectation_key)
        self.expectation_key = expectation_key

    @staticmethod
    def _check(obj):
        BaseCheck._check(obj)
        if isinstance(obj, BaseExpectationCheck):
            if obj.expectation_key is None:
                raise ValueError(
                    f"expectation_key should not be None!")
            if obj.expectation is None:
                raise ValueError(
                    f"expectation should not be None!")
            if obj.expectation_description is None:
                raise ValueError(
                    f"expectation_description should not be None!")
        else:
            raise TypeError(
                f"object of type '{type(obj)}' is not of type '{type(BaseExpectationCheck)}'!"
            )

    def build_expectation_description(self, result):
        if not isinstance(self, BaseArgumentsCheck):
            raise TypeError(
                f"object of type '{type(self)}' is not of type '{type(BaseArgumentsCheck)}'")
        expectation_description = CheckFunctions.expectation_descriptions[self.expectation_key]
        curr_args = copy(self.arguments)
        curr_args["result"] = result
        curr_args["function"] = CheckFunctions.get_function_string(self.expectation)
        args = CheckFunctions.get_string_args(
            curr_args, expectation_description)
        expectation_description = expectation_description.format(**args)
        return expectation_description

    @property
    def expectation_description(self):
        desc = self.build_expectation_description("result")
        return desc


    @property
    def expectation(self):
        expectation = CheckFunctions.expectations[self.expectation_key]
        return expectation
