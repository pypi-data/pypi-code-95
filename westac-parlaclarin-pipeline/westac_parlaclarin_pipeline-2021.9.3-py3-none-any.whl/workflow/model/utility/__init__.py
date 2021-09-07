# type: ignore

import importlib.resources as pkg_resources
import logging
from importlib import import_module
from io import StringIO
from typing import Any, Union

import yaml

from .persistent_dict import PersistentDict
from .utils import (  # source_basenames,; target_filenames,
    data_path_ts,
    deprecated,
    dict_get_by_path,
    dotdict,
    download_url,
    ensure_path,
    flatten,
    hasattr_path,
    load_dict,
    load_token_set,
    lookup,
    norm_join,
    path_add_date,
    path_add_sequence,
    path_add_suffix,
    path_add_timestamp,
    store_dict,
    store_token_set,
    strip_extensions,
    strip_path_and_add_counter,
    strip_path_and_extension,
    strip_paths,
    sync_delta_names,
    temporary_file,
    touch,
    ts_data_path,
    unlink,
)


def setup_logger() -> logging.Logger:

    log_format = '%(asctime)s, %(name)s, %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'

    logging.basicConfig(
        format=log_format, datefmt=log_format, level=logging.INFO, filename='parla_clarin_pipeline.log', filemode='w'
    )

    formatter = logging.Formatter(log_format)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    _logger = logging.getLogger("parla_clarin_pipeline")
    _logger.addHandler(console)
    _logger.setLevel(logging.WARNING)

    return _logger


logger: logging.Logger = setup_logger()
