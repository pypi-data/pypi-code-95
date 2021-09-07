import math
from typing import Any, Dict, List, Optional

import pandas as pd

from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import DepthMeasurementColumn, DepthMeasurementData, DepthMeasurementRow


class MeasurementRows:
    """
    Custom data class for the data collected from surveys, so they can be displayed as dataframes correctly
    """

    def __init__(
        self,
        cdf_id: int,
        external_id: Optional[str],
        columns: List[DepthMeasurementColumn],
        rows: List[DepthMeasurementRow],
    ):
        self.id = cdf_id
        self.external_id = external_id
        self.columns = columns
        self.rows = rows

    @staticmethod
    def from_measurement_data(measurement_data: DepthMeasurementData):
        return MeasurementRows(
            measurement_data.id, measurement_data.external_id, measurement_data.columns, measurement_data.rows
        )

    # Code for dump and to_pandas copied from sequences in cdf
    def dump(self, camel_case: bool = False) -> Dict[str, Any]:
        dumped = {
            "id": self.id,
            "external_id": self.external_id,
            "columns": self.columns,
            "rows": [
                {"rowNumber": r.row_number, "measuredDepth": r.measured_depth, "values": r.values} for r in self.rows
            ],
        }
        if camel_case:
            dumped = {to_camel_case(key): value for key, value in dumped.items()}
        return {key: value for key, value in dumped.items() if value is not None}

    def to_pandas(self, column_names: str = "columnExternalId|measurementType") -> pd.DataFrame:
        """
        Converts the MeasurementList to a pandas DataFrame.

        @param column_names: Changes the format of the column names. Set to
        `columnExternalId`, `measurementType`, or a combination of them
        separated by `|`. Default is `columnExternalId|measurementType`.
        """
        options = ["externalId", "id", "columnExternalId", "measurementType"]
        for column_name in column_names.split("|"):
            if column_name not in options:
                valid_options = ", ".join(options)
                raise ValueError(f"Invalid column_names value, should be one of {valid_options} separated by |.")

        column_names = (
            column_names.replace("columnExternalId", "{columnExternalId}")
            .replace("externalId", "{externalId}")
            .replace("id", "{id}")
            .replace("measurementType", "{measurementType}")
        )
        df_columns = [
            column_names.format(
                id=str(self.id),
                externalId=str(self.external_id),
                columnExternalId=column.external_id,
                measurementType=column.measurement_type.value,
            )
            for column in [column for column in self.columns]
        ]

        row_values = [row.values for row in self.rows]
        index = pd.Float64Index(name="measuredDepth", data=[row.measured_depth for row in self.rows])
        return pd.DataFrame(
            [[x if x is not None else math.nan for x in r] for r in row_values],
            index=index,
            columns=df_columns,
        )

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self.rows[item]

    def __iter__(self):
        return self.rows.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.rows]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.rows.__len__()
