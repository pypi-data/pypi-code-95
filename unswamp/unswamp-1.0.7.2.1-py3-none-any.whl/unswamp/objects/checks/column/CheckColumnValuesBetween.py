from unswamp.objects.checks.column.ColumnFunctionCheck import ColumnFunctionCheck


class CheckColumnValuesBetween(ColumnFunctionCheck):
    def __init__(self, id, column, value_min, value_max, inclusive=True, active=True, meta_data=None):
        function_key = "column_check_values_min_max_tuple"
        expectation_key = "result_tuple_between_inclusive_expectations"
        if not inclusive:
            expectation_key = "result_tuple_between_exclusive_expectations"
        arguments = {"column": column,
                     "expectation_min": value_min,
                     "expectation_max": value_max}

        ColumnFunctionCheck.__init__(
            self, id, function_key, expectation_key, arguments, active, meta_data)
