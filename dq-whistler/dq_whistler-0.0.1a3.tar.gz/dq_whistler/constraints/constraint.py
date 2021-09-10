from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pyspark.sql.dataframe import DataFrame
import json


class Constraint(ABC):
    """Defines the base Constraint class"""

    _name: str
    _values: Any
    _column_name: str
    _constraint: Dict[str, str]

    def __init__(self, constraint: Dict[str, str], column_name: str):
        """
        Creates an instance of Constraint with constraint config and column name

        Args:
            constraint (Dict[str, str]): Dict containing the name of constraint and the value of constraint check
            column_name (str): Column name to perform the constraint checks
        """
        self._name = constraint.get("name")
        self._values = constraint.get("values")
        self._column_name = column_name
        self._constraint = constraint

    def constraint_name(self):
        """
        Returns:
            :obj:`str`: The name of the constraint
        """
        return self._name

    def get_column_name(self):
        """
        Returns:
            :obj:`str`: The name of the column for which the Constraint instance was created
        """
        return self._column_name

    @abstractmethod
    def get_failure_df(self, data_frame: DataFrame) -> DataFrame:
        """
        Args:
            data_frame (:obj:`pyspark.sql.DataFrame`): The data as spark dataframe

        Returns:
            :obj:`pyspark.sql.DataFrame`: The dataframe containing failed cases for a constraint
        """
        return data_frame

    def get_sample_invalid_values(self, data_frame: DataFrame) -> List:
        """
        Args:
            data_frame (:obj:`pyspark.sql.DataFrame`): The data as spark dataframe

        Returns:
            :obj:`list`: A list containing the invalid values as per the given constraint
        """
        sample_invalid_values = [json.loads(row)[self._column_name] for row in data_frame.toJSON().take(10)]
        return sample_invalid_values

    def execute_check(self, data_frame: DataFrame) -> Dict[str, str]:
        """
        Args:
            data_frame (:obj:`pyspark.sql.DataFrame`): The data as spark dataframe

        Returns:
            :obj:`dict[str, str]`: The dict containing the final output for one constraint
            Example Output::
                {
                    "name": "eq",
                    "values", 5,
                    "constraint_status": "failed/success",
                    "invalid_count": 21,
                    "invalid_values": [4, 6, 7, 1]
                }
        """
        unmatched_df = self.get_failure_df(data_frame)
        unmatched_count = unmatched_df.count()
        sample_invalid_values = self.get_sample_invalid_values(unmatched_df)
        return {
            **self._constraint,
            "constraint_status": "failed" if unmatched_count > 0 else "success",
            "invalid_count": unmatched_count,
            "invalid_values": sample_invalid_values
        }
