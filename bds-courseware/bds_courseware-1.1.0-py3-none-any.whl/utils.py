import tempfile

import gdown
import pandas as pd

from bds_courseware.const import DATASETS


def print_dataset_description(dataset_name):
    pass


def print_module_datasets(module_num):
    pass


def read_drive_dataset(file_id, data_format="csv"):
    if data_format == "tsv":
        return pandas_read_drive_csv(file_id, sep="\t")
    if data_format == "tsv.gz":
        return pandas_read_drive_csv(file_id, sep="\t", compression="gzip")
    if data_format == "csv":
        return pandas_read_drive_csv(file_id, sep=",")
    if data_format == "csv.gz":
        return pandas_read_drive_csv(file_id, sep=",", compression="gzip")
    if data_format == "ssv":
        return pandas_read_drive_csv(file_id, sep=";")
    if data_format == "ssv.gz":
        return pandas_read_drive_csv(file_id, sep=";", compression="gzip")


def pandas_read_drive_csv(file_id, **read_csv_args):
    download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        return pd.read_csv(download_link, low_memory=False, **read_csv_args)
    except pd.errors.ParserError:
        with tempfile.TemporaryFile("w+b") as tmp_file:
            gdown.download(download_link, tmp_file)
            tmp_file.seek(0)
            return pd.read_csv(tmp_file, low_memory=False, **read_csv_args)


def get_stock_data(name):
    """
    Fetch stock data by company `name`
    """
    from ._ids import _stock_parts

    if name in _stock_parts:
        return read_drive_data(_stock_parts[name])
    else:
        raise IndexError(f"Uknown company name. {name} was given.")


def get_dataset(name):
    """
    Fetch dataset by `name`
    """
    from ._ids import _datasets

    if name in _datasets:
        return read_drive_data(*_datasets[name])
    else:
        raise IndexError(
            f"Uknown company name. {name} was given. Available datasets are {_datasets.keys()}"
        )
