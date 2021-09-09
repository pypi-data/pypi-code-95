import csv
import json
from os import makedirs, path
from shutil import move

from .dbt_schema import get_all_sources

class PreProcess:
    def __init__(self, data_provider: str, table: str, file_name: str,
                 development_dbt_root: str = None):
        self.data_provider = data_provider
        self.table = table
        self.file_name = file_name

        # In case the column names vary by case, this aligns with the schema
        self.column_name_map = {}

        if development_dbt_root:
            self.project_root = development_dbt_root

            # Will move to a folder in the same location the file is in now
            self.write_folder = "/".join(self.file_name.split("/")[:-1]) or "."
            self.archive_folder = self.write_folder + "/before_pre_process"

            self.file_name = self.file_name.split("/")[-1]

        else:
            self.project_root = "/".join(["", "dbfs", "mnt", "dbt"])

            # Move to the correct container location
            self.write_folder = "/" + "/".join([
                "dbfs", "mnt", "archive", self.data_provider, self.table])
            self.archive_folder = "/" + "/".join([
                "dbfs", "mnt", "archive", self.data_provider, self.table, "before_pre_process"])

        all_sources = get_all_sources(self.project_root)
        self.table_details = all_sources[data_provider]["tables"][table]

        # https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.DataFrameReader.csv.html
        # https://docs.python.org/3/library/csv.html#csv-fmt-params
        spark_to_csv = {
            "sep": "delimiter",
            "escape": "escapechar",
            "lineSep": "lineterminator",
            "quote": "quotechar"
        }
        self.csv_fmt_params = {
            spark_to_csv[name]: value
            for name, value in self.table_details.get("file_details", {}).items()
            if name in spark_to_csv
        }

        if not path.exists(self.archive_folder):
            makedirs(self.archive_folder)
        
        if not path.exists(self.get_write_path()) and not path.exists(self.get_raw_path()):
            raise Exception(
                f"Unable to find file at {self.get_write_path()} or {self.get_raw_path()} to process!"
            )

        if not path.exists(self.get_raw_path()):
            move(self.get_write_path(), self.get_raw_path())
        

    def get_raw_path(self):
        return self.archive_folder + "/" + self.file_name

    def get_write_path(self, new_file_name=None):
        if new_file_name:
            return self.write_folder + "/" + new_file_name
        else:
            return self.write_folder + "/" + self.file_name

    def get_filename_no_extension(self):
        return ".".join(self.file_name.split(".")[:-1])

    def get_raw_file(self):
        with open(self.get_raw_path(), "r") as raw_file:
            return raw_file.read()

    def get_raw_file_by_line(self):
        with open(self.get_raw_path(), "r") as raw_file:
            for line in raw_file.readlines():
                yield line

    def get_file_as_json(self):
        with open(self.get_raw_path(), "r") as jsonfile:
            return json.load(jsonfile)

    def read_csv_as_json(self):
        with open(self.get_raw_path(), "r") as raw_file:
            for row in csv.DictReader(raw_file, **self.csv_fmt_params):
                yield row

    def get_expected_table_fields(self):
        return [c["name"].strip("`") 
                for c in self.table_details["columns"]]

    def get_json_list_fields(self, json_list):
        known_columns = set()
        for ind_json in json_list:
            known_columns.update(ind_json.keys())
        return known_columns

    def check_table_fields(self, file_fields, expected_fields=None):
        expected_fields = expected_fields or self.get_expected_table_fields()
        schema_column_map = {
            c.lower(): c for c in expected_fields
        }
        missing_columns = [
            f for f in file_fields 
            if f not in expected_fields and f.lower() not in schema_column_map
        ]
        if missing_columns:
            raise Exception(
                f"Columns in file not in schema! {missing_columns}. "
                f"Schema columns: {expected_fields}, "
                f"file columns: {file_fields}")

        self.column_name_map = {
            f: schema_column_map[f.lower()]
            for f in file_fields 
            if f != schema_column_map[f.lower()]
        }


    def write_json_to_csv(self, json_to_write, new_file_name=None,
                          write_header=True, **kwargs):
        field_names = self.get_expected_table_fields()
        self.check_table_fields(
            self.get_json_list_fields(json_to_write), field_names)
        with open(self.get_write_path(new_file_name), "w") as result:

            writer = csv.DictWriter(result, fieldnames=field_names, 
                                    **self.csv_fmt_params, **kwargs)

            if write_header:
                writer.writeheader()

            for entry in json_to_write:
                writer.writerow({
                    self.column_name_map.get(k, k): v
                    for k, v in entry.items()
                })
  
    def write_json(self, json_to_write, new_file_name=None, **kwargs):
        with open(self.get_write_path(new_file_name), "w") as result:
            for ind_json in json_to_write:
                json.dump(ind_json, result, **kwargs)
                result.write("\n")
