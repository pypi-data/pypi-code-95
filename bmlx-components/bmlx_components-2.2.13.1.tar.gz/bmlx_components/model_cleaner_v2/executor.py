"""bmlx history model cleaner executor."""
import os
import sys
import logging
import re
from typing import Any, Dict, List, Text
from datetime import datetime

from bmlx.flow import Executor, Artifact
from bmlx.utils import import_utils, artifact_utils, io_utils

MODEL_DIR_PATTERN = "hdfs:[a-zA-Z0-9\.\/\-_]*\/[0-9]{8}$"
MODEL_CKPT_PATTERN = "hdfs:[a-zA-Z0-9\.\/\-_]*\/ckpt-[\.]{10}([\d]+)$"


class CleanerExecutor(Executor):
    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)
        model_uri_base = exec_properties["model_uri_base"]
        model_keep_max_versions = exec_properties["model_keep_max_versions"]

        fs, path = io_utils.resolve_filesystem_and_path(model_uri_base)
        if not fs.exists(path):
            logging.warning("model uri base %s does not exist!", model_uri_base)
            return

        assert fs.isdir(path)
        # 删除 6个小时之前的 ckpt-xxxx 文件
        model_ckpt_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f) and re.match(MODEL_CKPT_PATTERN, f)
        ]
        for f in model_ckpt_list:
            if (
                int(re.match(MODEL_CKPT_PATTERN, f).group(1))
                < int(datetime.now().timestamp()) - 6 * 3600
            ):
                fs.delete(f, recursive=True)

        model_days_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f) and re.match(MODEL_DIR_PATTERN, f)
        ]
        model_hours_list = []
        for model_dir in model_days_list:
            model_hours_list += fs.ls(model_dir)

        model_hours_list.sort()

        delete_model_hours_list = model_hours_list[
            0 : -1 * model_keep_max_versions
        ]

        logging.info(
            "model hours list: %s, try to delete model hour list: %s",
            model_hours_list,
            delete_model_hours_list,
        )
        for model_dir in delete_model_hours_list:
            fs.delete(model_dir, recursive=True)
            assert not fs.exists(model_dir)
            logging.info("clean model dir %s", model_dir)
        # 删除空day 目录
        for model_dir in model_days_list:
            if not fs.ls(model_dir):
                fs.delete(model_dir, recursive=True)
                logging.info("clean model dir %s", model_dir)

        logging.info(
            "left model dir list: %s",
            model_hours_list[-1 * model_keep_max_versions :],
        )
