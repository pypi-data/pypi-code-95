"""Indicator metadata-related model classes."""

from datetime import date
from typing import Optional
from enum import Enum
from pydantic.main import BaseModel


class Aggregate(str, Enum):
    avg = "avg"
    count = "count"
    max = "max"
    min = "min"
    sum = "sum"


class DataType(str, Enum):
    integer = "integer"
    decimal = "decimal"
    text = "text"
    json = "json"


class Format(str, Enum):
    decimal = "decimal"
    integer = "integer"
    percent = "percent"
    ratio = "ratio"
    currency = "currency"
    date = "date"
    timestamp = "timestamp"
    time = "time"
    usage= "usage"
    text = "text"
    none = ""


class IndicatorMetadata(BaseModel):
    code: str
    name: str
    description: str
    table_name: str
    unit: Optional[str] = None
    format: Format
    coverage: Optional[str] = None
    resolution: Optional[str] = None
    data_source: str
    computed_date: date
    aggregate_fn: Aggregate
    data_type: DataType
    aggregate_weight: str
    factor: float
    immutable: bool
    credits: int
