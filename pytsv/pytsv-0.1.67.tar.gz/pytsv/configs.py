import multiprocessing

from pytconf import ParamCreator, Config

CHECK_NON_ASCII = False
SKIP_COMMENTS = False
VALIDATE_ALL_LINES_SAME_NUMBER_OF_FIELDS = True
USE_ANY_FORMAT = True
SANITIZE = True
CLEAN_EDGES = True
SUB_TRAILING = True
REMOVE_NON_ASCII = True
LOWER_CASE = True
CHECK_NUM_FIELDS = True
CONVERT_TO_STRING = True
DO_GZIP = False
FILENAME_DETECT = True
DEFAULT_ENCODING = 'utf-8'
ATTACH_ENCODER = False


class ConfigInputFiles(Config):
    """
    Parameters to specify input files
    """
    input_files = ParamCreator.create_list_str(
        help_string="input files",
    )


class ConfigNumFields(Config):
    """
    Parameter to config number of fields in a TSV file
    """
    num_fields = ParamCreator.create_int_or_none(
        help_string="how many fields should the tsv have",
        default=None,
    )


class ConfigTsvReader(Config):
    """
    Parameters to configure a TSV reader object
    """
    check_non_ascii = ParamCreator.create_bool(
        help_string="check non ascii",
        default=CHECK_NON_ASCII,
    )
    validate_all_lines_same_number_of_fields = ParamCreator.create_bool(
        help_string="validate all lines same number of fields",
        default=VALIDATE_ALL_LINES_SAME_NUMBER_OF_FIELDS,
    )


class ConfigParallel(Config):
    """
    Parameters to configure how thing should run in parallel
    """
    parallel = ParamCreator.create_bool(
        help_string="do things in parallel?",
        default=False,
    )
    jobs = ParamCreator.create_int(
        help_string="how many jobs to run in parallel",
        default=multiprocessing.cpu_count(),
    )


class ConfigInputFile(Config):
    """
    Parameters to specify input file
    """
    input_file = ParamCreator.create_existing_file(
        help_string="input file",
    )


class ConfigFloatingPoint(Config):
    """
    Parameters to select whether to work with floating
    point or not
    """
    floating_point = ParamCreator.create_bool(
        help_string="work with floating point?",
        default=True,
    )


class ConfigMajority(Config):
    """
    Config the parameters for the majority algorithm
    """
    input_first_column = ParamCreator.create_int(
        help_string="first column",
    )
    input_second_column = ParamCreator.create_int(
        help_string="second column",
    )
    input_multiplication_column = ParamCreator.create_int(
        help_string="multiplication column",
    )


class ConfigProgress(Config):
    """
    Parameters to control progress reporting
    """
    progress = ParamCreator.create_bool(
        help_string="do you want progress report",
        default=True,
    )


class ConfigColumn(Config):
    """
    Parameters to select which column to work on
    """
    column = ParamCreator.create_int(
        help_string="column to use (list of numbers separated by comma)",
    )


class ConfigColumns(Config):
    """
    Parameters to select which columns to use
    """
    columns = ParamCreator.create_list_int(
        help_string="columns to use (list of numbers separated by comma)",
    )


class ConfigAggregateColumns(Config):
    """
    Parameters to select which columns to aggregate
    """
    aggregate_columns = ParamCreator.create_list_int(
        help_string="column to aggregate by (list of numbers separated by comma)",
    )


class ConfigMatchColumns(Config):
    """
    Parameters to select which columns to match by
    """
    match_columns = ParamCreator.create_list_int(
        help_string="column to match by (list of numbers separated by comma)",
    )


class ConfigOutputFile(Config):
    """
    Parameters to configure the output file
    """
    output_file = ParamCreator.create_new_file(
        help_string="output file to generate",
    )


class ConfigTree(Config):
    """
    Parameters to configure the parameters of a tree to show
    """
    roots = ParamCreator.create_list_str(
        help_string="roots to output",
    )
    parent_column = ParamCreator.create_int(
        help_string="parent column",
    )
    child_column = ParamCreator.create_int(
        help_string="child column",
    )


class ConfigCsvToTsv(Config):
    """
    Parameters to control the CSV to TSV conversion process
    """
    set_max = ParamCreator.create_bool(
        help_string="do you want to unset the limit on csv fields (good for large fielded csv files)",
        default=True,
    )
    replace_tabs_with_spaces = ParamCreator.create_bool(
        help_string="do you want to replace tabs with spaces?",
        default=True,
    )
    check_num_fields = ParamCreator.create_bool(
        help_string="check that all lines have the same number of fields?",
        default=CHECK_NUM_FIELDS,
    )


class ConfigBucketNumber(Config):
    """
    Parameters to configure the bucket number for a histogram
    """
    bucket_number = ParamCreator.create_int(
        help_string="what column to histogram",
        default=10,
    )


class ConfigFixTypes(Config):
    """
    Parameters to control which fixes to apply to a TSV file.
    """
    clean_edges = ParamCreator.create_bool(
        help_string="remove space before and after",
        default=CLEAN_EDGES,
    )
    sub_trailing = ParamCreator.create_bool(
        help_string="substitute consecutive white spaces with one single space",
        default=SUB_TRAILING,
    )
    remove_non_ascii = ParamCreator.create_bool(
        help_string="remove non ascii characters",
        default=REMOVE_NON_ASCII,
    )
    lower_case = ParamCreator.create_bool(
        help_string="lower case the field",
        default=LOWER_CASE,
    )


class ConfigCheckUnique(Config):
    """
    Configure whether or not to check a column for uniqueness
    """
    check_unique = ParamCreator.create_bool(
        help_string="check that the value_column has unique values?",
        default=True,
    )


class ConfigSampleSize(Config):
    """
    Configure sample size
    """
    size = ParamCreator.create_int(
        help_string="what sample size do you need?",
    )


class ConfigSampleColumn(Config):
    """
    Configuration options for sampling
    """
    sample_column = ParamCreator.create_int(
        help_string="what column to sample by",
    )


class ConfigReplace(Config):
    """
    Configure whether you want replacements or not
    """
    replace = ParamCreator.create_bool(
        help_string="allow replacements?",
    )


class ConfigSampleByColumnOld(Config):
    """
    Parameters to configure the old sample by column algorithm
    """
    hits_mode = ParamCreator.create_bool(
        help_string="sample size is hits",
    )


class ConfigJoin(Config):
    """
    Parameters to configure a TSV join operation
    """
    hash_file = ParamCreator.create_existing_file(
        help_string="hash file",
    )
    hash_key_column = ParamCreator.create_int(
        help_string="column to match on in the hash file",
    )
    hash_value_column = ParamCreator.create_int(
        help_string="value to get from the hash file",
    )
    input_key_column = ParamCreator.create_int(
        help_string="column to match on in the input file",
    )
    output_insert_column = ParamCreator.create_int(
        help_string="column to insert at in the first file to create the output file",
    )
    output_add_unknown = ParamCreator.create_bool(
        help_string="add UNKNOWN when there is no match or drop",
    )


class ConfigPattern(Config):
    """
    Parameters to configure patterns of files generated
    """
    pattern = ParamCreator.create_str(
        help_string="pattern of intermediate generated files",
        default="{key}_{i:04d}.tsv.gz",
    )
    final_pattern = ParamCreator.create_str(
        help_string="pattern of final generated files",
        default="{key}.tsv.gz",
    )


class ConfigSampleByTwoColumns(Config):
    """
    Parameters for the sample by column command
    """
    group_column = ParamCreator.create_int(
        help_string="what column to determine group by",
    )


class ConfigWeightValue(Config):
    """
    Config weight and Value
    """
    weight_column = ParamCreator.create_int(
        help_string="what column to determine weight by",
    )
    value_column = ParamCreator.create_int(
        help_string="what is the value column",
    )
