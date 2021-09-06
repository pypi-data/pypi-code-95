from typing import Dict, Optional

import pandas as pd

from common_client_scheduler import ExportRequest

from . import ClassMethod, Struct
from ..data_transfers.common import S3


class ClassMethodDF(ClassMethod):
    _class_name: str = "dataframe"
    _pandas_class = pd.DataFrame
    _additional_class_methods = ClassMethod._additional_class_methods | {
        "from_dict",
        "from_records",
    }


class DataFrame(Struct, metaclass=ClassMethodDF):
    _class_name: str = "dataframe"
    _pandas_class_instance = pd.DataFrame()
    _additional_methods = Struct._additional_methods | {
        "to_csv_folder",
        "to_parquet_folder",
    }

    def _on_missing_attribute(self, item: str):
        return self._call_method(None, "df_col_by_attribute_access", item)

    def __iter__(self):
        # Iterating on a `DataFrame` is the same as iterating on its columns.
        return self.columns.__iter__()

    @staticmethod
    def _make_export_request(path: str, storage_options: Optional[Dict] = None) -> ExportRequest:
        if path.startswith("s3://"):
            bucket = path[5:].split("/", maxsplit=1)[0]
            aws_region = S3.client().get_bucket_location(Bucket=bucket)["LocationConstraint"]
        else:
            aws_region = None
        return ExportRequest(path=path, aws_region=aws_region, storage_options=storage_options)

    def to_csv(self, path: str, storage_options: Optional[Dict] = None):
        export_request = self._make_export_request(path, storage_options)
        return self._call_method(None, "to_csv", export_request)

    def to_csv_folder(self, path: str, num_files: int, storage_options: Optional[Dict] = None):
        export_request = self._make_export_request(path, storage_options)
        return self._call_method(None, "to_csv_folder", export_request, num_files)

    def to_parquet(self, path: str, storage_options: Optional[Dict] = None):
        return self._call_method(
            None, "to_parquet", self._make_export_request(path, storage_options)
        )

    def to_parquet_folder(self, path: str, num_files: int, storage_options: Optional[Dict] = None):
        export_request = self._make_export_request(path, storage_options)
        return self._call_method(None, "to_parquet_folder", export_request, num_files)

    def to_dict(self):
        pd_df = self._call_method(None, "to_dict")
        return pd_df.to_dict()
