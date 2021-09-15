from terality_serde import SerializableEnum


# This class needs to be common to client / scheduler / worker.
class IndexType(str, SerializableEnum):
    """
    Technical types names of supported index sub classes.
    """

    INDEX = "index"
    MULTI_INDEX = "multi_index"
    DATETIME_INDEX = "datetime_index"
    INT64_INDEX = "int64_index"
    FLOAT64_INDEX = "float64_index"


class StructType(str, SerializableEnum):
    """
    Technical types names of pandas supported structures, excluding index.
    """

    DATAFRAME = "dataframe"
    SERIES = "series"
    DATAFRAME_GROUPBY = "dataframe_groupby"
    SERIES_GROUPBY = "series_groupby"
    NDARRAY = "ndarray"
    TOP_LEVEL = "top_level"
