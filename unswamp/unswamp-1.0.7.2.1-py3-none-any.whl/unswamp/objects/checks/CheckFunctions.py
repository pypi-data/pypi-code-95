from string import Formatter
import inspect


class CheckFunctions():
    functions = {
        "table_check_columns_match_list_ordered": lambda dataset, columns: list(dataset.columns)[list(dataset.columns).index(columns[0]):list(dataset.columns).index(columns[0])+len(columns)],
        "table_check_columns_missing": lambda dataset, columns: set(columns).difference(set(dataset.columns)),
        "table_check_columns_count": lambda dataset: dataset.shape[1],
        "table_check_rows_count": lambda dataset: dataset.shape[0],
        "column_check_values_unique": lambda dataset, column: dataset[column].is_unique,
        "column_check_values_null_count": lambda dataset, column: dataset[column].isna().sum(),
        "column_check_values_all_null": lambda dataset, column: dataset[column].isna().sum() == dataset.shape[0],
        "column_check_values_distinct_count": lambda dataset, column: dataset[column].nunique(),
        "column_check_values_distinct_set": lambda dataset, column: set(dataset[column].unique()),
        "column_check_values_min_max_tuple": lambda dataset, column: (dataset[column].min(), dataset[column].max()),
        "column_check_values_increasing": lambda dataset, column: (dataset[column].is_monotonic_increasing) and (dataset[column].nunique() != 1),
        "column_check_values_decreasing": lambda dataset, column: (dataset[column].is_monotonic_decreasing) and (dataset[column].nunique() != 1),
        "column_check_string_length_min_max_tuple": lambda dataset, column: (min(dataset[column].str.len()), max(dataset[column].str.len())),
    }

    function_descriptions = {
        "table_check_columns_match_list_ordered": "The check tries to extract the provided columns '{columns}' as an ordered list from the columns of a dataframe. The function expression looks like '{function}'.",
        "table_check_columns_missing": "The check compares the provided columns '{columns}' against the columns of a dataframe to identify missing columns. The function expression looks like '{function}'.",
        "table_check_columns_count": "The check counts the number of columns of a dataframe. The function expression looks like '{function}'.",
        "table_check_rows_count": "The check counts the number of rows of a dataframe. The function expression looks like '{function}'.",
        "column_check_values_unique": "The check determines if the values in column '{column}' of a dataframe are unique. The function expression looks like '{function}'.",
        "column_check_values_null_count": "The check counts the number of null values in column '{column}' of a dataframe. The function expression looks like '{function}'.",
        "column_check_values_all_null": "The check determines if all values in column '{column}' of a dataframe are null. The function expression looks like '{function}'.",
        "column_check_values_distinct_count": "The check counts the number of distinct values in column '{column}' of a dataframe. The function expression looks like '{function}'.",
        "column_check_values_distinct_set": "The check gets all distinct values in column '{column}' of a dataframe as a set. The function expression looks like '{function}'.",
        "column_check_values_min_max_tuple": "The check gets the min and max value of column '{column}' of a dataframe as a tuple. The function expression looks like '{function}'.",
        "column_check_values_increasing": "The check determines if the values of column '{column}' are increasing. The function expression looks like '{function}'.",
        "column_check_values_decreasing": "The check determines if the values of column '{column}' are decreasing. The function expression looks like '{function}'.",
        "column_check_string_length_min_max_tuple": "The check gets the min and max string length of column '{column}' of a dataframe as a tuple. The function expression looks like '{function}'.",
    }

    expectations = {
        "result_eq_expectation": lambda result, expectation: result == expectation,
        "result_ge_expectation": lambda result, expectation: result >= expectation,
        "result_le_expectation": lambda result, expectation: result <= expectation,
        "result_gt_expectation": lambda result, expectation: result > expectation,
        "result_lt_expectation": lambda result, expectation: result < expectation,
        "result_between_inclusive_expectations": lambda result, expectation_min, expectation_max: result >= expectation_min and result <= expectation_max,
        "result_between_exclusive_expectations": lambda result, expectation_min, expectation_max: result > expectation_min and result < expectation_max,
        "result_len_eq_expectation": lambda result, expectation: len(result) == expectation,
        "result_set_not_in_expectation_set": lambda result, expectation: set(expectation) - result == set(expectation),
        "result_tuple_between_inclusive_expectations": lambda result, expectation_min, expectation_max: min(result) <= expectation_min and max(result) >= expectation_max,
        "result_tuple_between_exclusive_expectations": lambda result, expectation_min, expectation_max: min(result) < expectation_min and max(result) > expectation_max,
        "result_is_subset_expectation": lambda result, expectation: result.issubset(set(expectation)) == True,
    }

    expectation_descriptions = {
        "result_eq_expectation": "The expectation is that {result} == '{expectation}'. The expectation expression looks like '{function}'.",
        "result_ge_expectation": "The expectation is that {result} >= '{expectation}'. The expectation expression looks like '{function}'.",
        "result_le_expectation": "The expectation is that {result} <= '{expectation}'. The expectation expression looks like '{function}'.",
        "result_gt_expectation": "The expectation is that {result} > '{expectation}'. The expectation expression looks like '{function}'.",
        "result_lt_expectation": "The expectation is that {result} < '{expectation}'. The expectation expression looks like '{function}'.",
        "result_between_inclusive_expectations": "The expectation is {result} >= '{expectation_min}' and {result} <= '{expectation_max}'. The expectation expression looks like '{function}'.",
        "result_between_exclusive_expectations": "The expectation is {result} > '{expectation_min}' and {result} < '{expectation_max}'. The expectation expression looks like '{function}'.",
        "result_len_eq_expectation": "The expectation is len({result}) == '{expectation}'. The expectation expression looks like '{function}'.",
        "result_set_not_in_expectation_set": "The expectation is that the {result} set does not contain '{expectation}'. The expectation expression looks like '{function}'.",
        "result_tuple_between_inclusive_expectations": "The expectation is min({result}) >= '{expectation_min}' and max({result}) <= '{expectation_max}'. The expectation expression looks like '{function}'.",
        "result_tuple_between_exclusive_expectations": "The expectation is min({result}) > '{expectation_min}' and max({result}) < '{expectation_max}'. The expectation expression looks like '{function}'.",
        "result_is_subset_expectation": "The expectation is that the {result} is a subset of '{expectation}'. The expectation expression looks like '{function}'.",
    }

    """
    success_messages = {
        "CheckColumnsExists":"",
        "CheckColumnsMatchOrderedList":"",
        "CheckColumnsCountExact":"",
        "CheckColumnsCountBetween":"",
        "CheckRowsCountExact":"",
        "CheckRowsCountBetween":"",
        "CheckColumnValuesUnique":"",
        "CheckColumnValuesNotNull":"",
        "CheckColumnValuesAllNull":"",
        "CheckColumnValuesAllSame":"",
        "CheckColumnValuesInSet":"",
        "CheckColumnValuesNotInSet":"",
        "CheckColumnValuesBetween":"",
        "CheckColumnValuesIncreasing":"",
        "CheckColumnValuesDecreasing":"",
    }
    """

    @staticmethod
    def get_function_string(function, lambda_only = True):
        lambda_part = "lambda "
        desc = inspect.getsource(function)
        desc = desc.strip()
        if lambda_part in desc:
            start_pos = desc.find(lambda_part)
            desc = desc[start_pos:]
        return desc

    @staticmethod
    def get_function_vars(function):
        fx_vars = set(function.__code__.co_varnames)
        return fx_vars
        

    @staticmethod
    def get_function_args(arguments, function):
        fx_args = {}
        for key in CheckFunctions.get_function_vars(function):
            fx_args[key] = arguments[key]
        return fx_args

    @staticmethod
    def get_string_vars(description):
        desc_vars = [fname for _, fname, _,
                     _ in Formatter().parse(description) if fname]
        return desc_vars

    @staticmethod
    def get_string_args(arguments, description):
        desc_args = {}
        for key in CheckFunctions.get_string_vars(description):
            desc_args[key] = arguments[key]
        return desc_args

    @staticmethod
    def check_expectation_keys(expectation_key):
        if expectation_key not in CheckFunctions.expectations:
            raise ValueError(
                f"CheckFunctions.expectations has no key '{expectation_key}'!")
        if expectation_key not in CheckFunctions.expectation_descriptions:
            raise ValueError(
                f"CheckFunctions.expectation_descriptions has no key '{expectation_key}'!")

    @staticmethod
    def check_function_keys(function_key):
        if function_key not in CheckFunctions.functions:
            raise ValueError(
                f"CheckFunctions.functions has no key '{function_key}'!")
        if function_key not in CheckFunctions.function_descriptions:
            raise ValueError(
                f"CheckFunctions.function_descriptions has no key '{function_key}'!")

    #@staticmethod
    #def get_result_message(check, passed):
    #    return CheckFunctions.success_messages[check.name]

