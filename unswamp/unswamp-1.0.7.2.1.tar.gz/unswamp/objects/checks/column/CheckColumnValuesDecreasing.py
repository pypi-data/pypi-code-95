from unswamp.objects.checks.column.ColumnFunctionCheck import ColumnFunctionCheck


class CheckColumnValuesDecreasing(ColumnFunctionCheck):
    def __init__(self, id, column, active=True, meta_data=None):
        function_key = "column_check_values_decreasing"
        expectation_key = "result_eq_expectation"
        arguments = {"column": column, "expectation": True}

        ColumnFunctionCheck.__init__(
            self, id, function_key, expectation_key, arguments, active, meta_data)
