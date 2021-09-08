from unswamp.objects.checks.column.ColumnFunctionCheck import ColumnFunctionCheck


class CheckColumnValuesAllSame(ColumnFunctionCheck):
    def __init__(self, id, column, active=True, meta_data=None):
        function_key = "column_check_values_distinct_count"
        expectation_key = "result_eq_expectation"
        arguments = {"column": column, "expectation": 1}

        ColumnFunctionCheck.__init__(
            self, id, function_key, expectation_key, arguments, active, meta_data)
