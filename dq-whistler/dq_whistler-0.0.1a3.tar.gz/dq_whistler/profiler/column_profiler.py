from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pyspark.sql.dataframe import DataFrame
import pyspark.sql.functions as f
from pyspark.sql.types import StringType, DoubleType, IntegerType
from dq_whistler.constraints.constraint import Constraint
import json


class ColumnProfiler(ABC):
    """
    Base class for column profiler
    """

    _column_data: DataFrame
    _config: Dict[str, Any]
    _constraints: List[Constraint]

    def __init__(self, column_data: DataFrame, config: Dict[str, Any]):
        """
        Creates an instance of :obj:`ColumnProfiler`
        Args:
            column_data (pyspark.sql.DataFrame): Column data as a spark dataframe to execute constraints
            config (Dict[str, Any]): Config containing all the constraints of a column along with expected data types
            Sample Dict::
            {
              "name": "col_name",
              "datatype": "col_data_type(number/string/date)",
              "constraints":[
                 {
                    "name": "gt_eq",
                    "values": 5
                 },
                 {
                    "name": "is_in",
                    "values": [1, 2]
                 }...
              ]
            }
        """
        self._column_data = column_data
        self._config = config
        self._column_name = config.get("name")
        self._data_type = config.get("datatype")
        self._constraints = []

    def prepare_df_for_constraints(self) -> None:
        """
        Prepares a dataframe by doing pre validations
        """
        if self._data_type == "string":
            self._column_data.withColumn(self._column_name, f.col(self._column_name).cast(StringType()))
        elif self._data_type == "number":
            self._column_data.withColumn(self._column_name, f.col(self._column_name).cast(DoubleType()))
        elif self._data_type == "integer":
            self._column_data.withColumn(self._column_name, f.col(self._column_name).cast(IntegerType()))
        else:
            raise NotImplementedError

    def add_constraint(self, constraint: Constraint):
        """
        Adds an instance of :obj:`Constraint` to the the parent list of constraints for this profiler

        Args:
            constraint (dq_whistler.constraints.constraint.Constraint): An instance of :obj:`Constraint` class
        """
        existing = filter(
            lambda c:
            c.constraint_name() == constraint.constraint_name()
            and c.get_column_name() == constraint.get_column_name(), self._constraints)
        if list(existing):
            raise ValueError(f"A similar constraint for the column {constraint.get_column_name()} already exists.")
        self._constraints.append(constraint)

    def get_constraints_config(self) -> List[Dict[str, str]]:
        """
        Returns:
            :obj:`List[Dict[str, str]]`: The array containing the constraints for the column
        """
        return self._config.get("constraints") if self._config.get("constraints") else []

    def get_column_info(self) -> str:
        """
        Returns:
            :obj:`str`: The column info for which the instance has been created
            Sample output::
                str({
                    "fields":[
                        {
                            "metadata":{},
                            "name":"col_name",
                            "nullable":True,
                            "type":"string"
                        }
                    ],
                    "type":"struct"
                })
        """
        return self._column_data.schema.json()

    def get_column_config(self) -> Dict[str, Any]:
        """
        Returns:
            :obj:`Dict[str, Any]`: The data quality config for the column
        """
        return self._config

    def get_null_count(self) -> int:
        """
        Returns:
            :obj:`int`: Count of null values in a column data
        """
        col_name = self._column_name
        return self._column_data.select(
            f.count(
                f.when(
                    f.col(col_name).contains("None") |
                    f.col(col_name).contains("NULL") |
                    (f.col(col_name) == "") |
                    f.col(col_name).isNull() |
                    f.isnan(col_name), col_name
                )
            ).alias("null_count")
        ).first()[0]

    def get_unique_count(self) -> int:
        """
        Returns:
            :obj:`int`: Count of unique values in a column data
        """
        return self._column_data.distinct().count()

    def get_total_count(self) -> int:
        """
        Returns:
            :obj:`int`: Count of total values in a column data
        """
        return self._column_data.count()

    def get_quality_score(self) -> float:
        """
        Returns:
            :obj:`float`: Overall quality score of a column
        """
        return 0.0

    def get_topn(self) -> Dict[str, Any]:
        """
        Returns:
            :obj:`Dict[str, Any]`: Dict containing the top 10 values along with their counts
            Sample Output::
                {
                    "value1": count1,
                    "value2": count2
                }
        """
        col_name = self._column_name
        top_values = dict()
        if self._data_type == "string":
            top_values_rows = self._column_data \
                .filter((f.col(col_name) != "") & (f.col(col_name).isNotNull()) & (f.col(col_name) != "null")) \
                .groupby(col_name) \
                .count() \
                .sort(f.desc("count")) \
                .toJSON() \
                .take(10)
        elif self._data_type == "number":
            top_values_rows = self._column_data \
                .filter(f.col(col_name).isNotNull()) \
                .groupby(col_name) \
                .count() \
                .sort(f.desc("count")) \
                .toJSON() \
                .take(10)
        else:
            raise NotImplementedError

        [
            top_values.update(
                {json.loads(row).get(col_name): json.loads(row)["count"]})
            for row in top_values_rows
        ]
        return top_values

    def get_custom_constraint_check(self) -> List[Dict[str, str]]:
        """
        Returns:
            :obj:`List[Dict[str, str]]`: An array containing the output of each of the constraint for a column
            Sample Output::
                [
                    {
                        "name": "eq",
                        "values", 5,
                        "constraint_status": "failed/success",
                        "invalid_count": 21,
                        "invalid_values": [4, 6, 7, 1]
                    }...
                ]
        """
        constraints_output = []
        for constraint in self._constraints:
            output = constraint.execute_check(self._column_data)
            constraints_output.append(output)
        return constraints_output

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Returns:
            :obj:`Dict[str, Any]`: The final stats of the column containing null count, total count,
            regex count, invalid rows, quality score etc.
        """
        pass
