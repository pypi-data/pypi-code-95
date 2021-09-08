from enum import Enum, unique


class DataSourceLabel(Enum):
    PREDICTION = 'predict'
    TEST = 'test'
    TRAIN = 'train'


class Status(Enum):
    COMPLETED = 'Completed'
    ERROR = 'Error'
    IN_PROGRESS = 'In Progress'
    WAITING = 'Waiting'


@unique
class FileType(Enum):
    CSV = 'text/csv'
    TSV = 'text/tab-separated-values'
    PARQUET = 'application/x-parquet'


@unique
class ClassificationMetrics(Enum):
    ACCURACY = 'accuracy'
    RECALL = 'recall'
    PRECISION = 'precision'
    F1 = 'f1'


@unique
class RegressionMetrics(Enum):
    MEAN_ABSOLUTE_ERROR = 'mean absolute error'
    MEAN_SQUARED_ERROR = 'mean squared error'
