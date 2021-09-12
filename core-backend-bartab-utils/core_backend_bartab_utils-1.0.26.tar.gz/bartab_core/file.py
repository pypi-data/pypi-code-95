import os
from .string import get_clear_random_value
import csv
import boto3
from .paths import get_relative_path


class File:

    def __init__(self, file_path: str, create_if_not_exists: bool = False):
        if file_path == None:
            raise ValueError("File path cannot be none")

        self.file_path = file_path

        file_split = file_path.split("/")
        self.file_name = file_split[-1]
        self.file_parent_dir = "/".join(file_split[:-1])

        if create_if_not_exists:
            self.get_or_create()

    def is_file_type(self, file_type: str):
        if not self.has_file_extention():
            return False

        return self.get_file_extention().lower() == file_type.lower()

    def exists(self, raise_error_on_non_exists: bool = False):
        try:
            exists = os.path.exists(self.file_path)
        except:
            exists = False

        if not exists and raise_error_on_non_exists:
            raise ValueError(
                f"File at file path {self.file_path} does not exist")

        return exists

    def has_file_extention(self, raise_error_on_invalid: bool = False):
        has_file_extention = "." in self.file_name

        if not has_file_extention and raise_error_on_invalid:
            raise ValueError(
                f"File at file path {self.file_path} is not valid")

        return has_file_extention

    def get_file_extention(self):
        self.has_file_extention(True)

        return self.file_name.split(".")[1]

    def get_file_name_no_extention(self):
        self.has_file_extention(True)

        return self.file_name.split(".")[0]

    def read(self):
        self.exists(True)

        return open(self.file_path, "r")

    def file_contents(self):
        self.exists(True)

        return open(self.file_path, "r").read()

    def replace(self, old: str, new: str, count: int = 0):
        if count > 0:
            self.set_text(self.file_contents().replace(
                old, new, count))
        else:
            self.set_text(self.file_contents().replace(
                old, new))

    def clear(self):
        self.exists(True)

        open(self.file_path, 'w').close()

    def allow_all(self):
        self.exists(True)

        os.chmod(self.file_path, 0o777)

    def delete(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def set_text(self, text: str):
        self.exists(True)

        file = open(self.file_path, "w")
        file.write(str(text))
        file.close()

    def append(self, text: str):
        self.exists(True)

        file = open(self.file_path, "a")
        file.write(text)
        file.close()

    def append_line(self, text: str):
        self.append(f"\n{text}")

    def get_or_create(self):
        if self.exists():
            return self
        else:
            if not os.path.exists(self.file_parent_dir):
                os.makedirs(self.file_parent_dir)

            open(self.file_path, "a")
            return self

    def __str__(self):
        return self.file_path


class RequiredFile(File):

    def __init__(self, file_path):
        super().__init__(file_path)
        if not super().exists():
            raise ValueError(
                f"File at file path {file_path} is not valid")


class FileTypeRequired(File):
    def __init__(self, file_path, file_type):
        super().__init__(file_path)
        if not super().exists() or not super().is_file_type(file_type):
            raise ValueError(
                f"File at file path {file_path} is not valid")


class TmpFile(File):
    def __init__(self, file_type="sh"):
        base_file_path = get_relative_path('../../tmp', __file__)

        file_path = f"{base_file_path}/{get_clear_random_value()}.{file_type}"

        super().__init__(file_path, True)

        self.clear()


class CSVFile(File):
    def __init__(self, file_path, delimiter=',', encoding="utf8", create_if_not_exists=False):
        super().__init__(file_path, create_if_not_exists)

        try:
            self.__rows = list(csv.reader(
                open(file_path, 'rt', encoding=encoding), delimiter=delimiter))
            self.is_valid = True
        except:
            self.is_valid = False

    def rows(self) -> list:
        return [] if not self.is_valid else self.__rows

    def headers(self) -> list:
        return [] if len(self.rows()) < 2 else self.rows()[0]

    def get_value(self, row: int, column: int):
        if not self.is_valid or len(self.rows()) <= row or len(self.rows()[row]) <= column:
            return None
        else:
            return self.rows()[row][column]

    def get_row(self, row: int) -> list:
        if not self.is_valid or len(self.rows()) <= row:
            return None
        else:
            return self.rows()[row]

    def find_row_by_value_in_column(self, column: int, value):
        if not self.is_valid:
            return None
        else:
            for row in self.rows():
                if len(row) > column and row[column] == value:
                    return row
            return None


class S3File(File):

    def __init__(self, bucket_name, bucket_file_path, file_path, raise_exception=False):
        super().__init__(file_path)

        self.bucket_name = bucket_name
        self.bucket_file_path = bucket_file_path
        self.raise_exception = raise_exception

        try:
            boto3.client('s3').download_file(bucket_name,
                                             bucket_file_path, file_path)
        except Exception as e:
            if raise_exception:
                raise ValueError("Error downloading file at file path {0} from bucket {1}".format(
                    bucket_file_path, bucket_name))
            else:
                self.file_path = None
