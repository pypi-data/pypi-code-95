from unswamp.objects.checks.column.ColumnFunctionCheck import ColumnFunctionCheck


class CheckColumnValuesNotInSet(ColumnFunctionCheck):
    def __init__(self, id, column, values, active=True, meta_data=None):
        function_key = "column_check_values_distinct_set"
        expectation_key = "result_set_not_in_expectation_set"
        arguments = {"column": column, "expectation": values}

        ColumnFunctionCheck.__init__(
            self, id, function_key, expectation_key, arguments, active, meta_data)
