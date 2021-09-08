from unswamp.objects.checks.base.FunctionCheck import FunctionCheck


class ColumnFunctionCheck(FunctionCheck):

    def __init__(self, id, function_key, expectation_key, arguments, active=True, meta_data=None):
        level = "column"
        FunctionCheck.__init__(
            self, id, function_key, expectation_key, arguments, active, level, meta_data)
