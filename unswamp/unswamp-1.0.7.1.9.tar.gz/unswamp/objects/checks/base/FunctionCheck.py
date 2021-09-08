from copy import copy
from unswamp.objects.checks.base.BaseFunctionCheck import BaseFunctionCheck
from unswamp.objects.checks.base.BaseExpectationCheck import BaseExpectationCheck
from unswamp.objects.checks.base.BaseArgumentsCheck import BaseArgumentsCheck
from unswamp.objects.checks.CheckFunctions import CheckFunctions


class FunctionCheck(BaseFunctionCheck, BaseExpectationCheck, BaseArgumentsCheck):
    arguments = set()

    def __init__(self, key, function_key, expectation_key, arguments, active=True, level="column", meta_data=None):
        if meta_data is None:
            meta_data = {}

        if arguments is None:
            arguments = set()

        BaseFunctionCheck.__init__(
            self, key, function_key, active, level, meta_data)
        BaseExpectationCheck.__init__(
            self, key, expectation_key, active, level, meta_data)
        BaseArgumentsCheck.__init__(
            self, key, arguments, active, level, meta_data)

        BaseFunctionCheck._check(self)
        BaseExpectationCheck._check(self)
        BaseArgumentsCheck._check(self)

        fx_vars = CheckFunctions.get_function_vars(self.function)
        exp_vars = CheckFunctions.get_function_vars(self.expectation)
        fx_vars.update(exp_vars)

        self._args_check(fx_vars)
        self.description = f"{self.function_description} {self.expectation_description}"

    def _run(self, dataset):
        passed = False
        all_args = copy(self.arguments)
        all_args["dataset"] = dataset
        try:
            fx_args = CheckFunctions.get_function_args(
                all_args, self.function)
            result = self.function(**fx_args)
            all_args["result"] = result
            exp_args = CheckFunctions.get_function_args(
                all_args, self.expectation)
            passed = self.expectation(**exp_args)
        except ValueError as error:
            message = f"The check did end in the following error '{error}'!"
            return False, message, None

        message = f"The result '{result}' did meet the expectation!"
        if not passed:
            message = f"The result '{result}' did not meet the expectation!"
        return passed, message, result
