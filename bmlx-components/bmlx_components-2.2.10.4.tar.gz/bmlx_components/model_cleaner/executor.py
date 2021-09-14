"""bmlx history model cleaner executor."""
import os
import sys
import logging
import re
from typing import Any, Dict, List, Text
from datetime import datetime, timedelta
from pytz import timezone

from bmlx.flow import Executor, Artifact
from bmlx.utils import import_utils, artifact_utils, io_utils

MODEL_DIR_PATTERN = "hdfs:[a-zA-Z0-9\.\/\-_]*\/[0-9]{8}$"
HOURLY_MODEL_DIR_PATTERN = "hdfs:[a-zA-Z0-9\.\/\-_]*\/[0-9]{8}\/[0-9]{2}$"
MODEL_CKPT_PATTERN = "hdfs:[a-zA-Z0-9\/\-_]*\/ckpt-[\.]{10}([\d]+)$"


class CleanerExecutor(Executor):
    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)
        model_uri_base = exec_properties["model_uri_base"]
        keep_none_before_days = exec_properties["keep_none_before_days"]
        keep_final_before_days = exec_properties["keep_final_before_days"]

        fs, path = io_utils.resolve_filesystem_and_path(model_uri_base)
        if not fs.exists(path):
            logging.warning("model uri base %s does not exist!", model_uri_base)
            return

        assert fs.isdir(path)
        # 删除 6个小时之前的 ckpt-xxxx 文件
        # model_ckpt_list = [
        #     f
        #     for f in fs.ls(path)
        #     if fs.isdir(f) and re.match(MODEL_CKPT_PATTERN, f)
        # ]
        # for f in model_ckpt_list:
        #     if (
        #         int(re.match(MODEL_CKPT_PATTERN, f).group(1))
        #         < int(datetime.now().timestamp()) - 6 * 3600
        #     ):
        #         fs.delete(f, recursive=True)

        def get_latest_model_hour_str():
            daily_model_dirs = [
                f
                for f in fs.ls(path)
                if fs.isdir(f) and re.match(MODEL_DIR_PATTERN, f)
            ]
            if daily_model_dirs:
                latest_daily_model_dir = sorted(daily_model_dirs, reverse=True)[
                    0
                ]
                hourly_model_dirs = [
                    f
                    for f in fs.ls(latest_daily_model_dir)
                    if fs.isdir(f) and re.match(HOURLY_MODEL_DIR_PATTERN, f)
                ]
                if hourly_model_dirs:
                    return sorted(hourly_model_dirs, reverse=True)[0][-11:]
                else:
                    fs.delete(latest_daily_model_dir, recursive=True)
                    return get_latest_model_hour_str()
            else:
                return None

        latest_model_hour_str = get_latest_model_hour_str()
        if not latest_model_hour_str:
            logging.info("No model dir found, skip to clean old model")
            return

        latest_model_hour = datetime.strptime(
            f"{latest_model_hour_str} +0800", "%Y%m%d/%H %z"
        )

        logging.info(
            "get latest model hour %s, convert to datetime: %s",
            latest_model_hour_str,
            latest_model_hour,
        )

        keep_none_day = latest_model_hour - timedelta(
            days=keep_none_before_days
        )
        keep_none_day = keep_none_day.strftime("%Y%m%d")

        keep_none_model_days_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f)
            and re.match(MODEL_DIR_PATTERN, f)
            and f[-8:] <= keep_none_day
        ]
        logging.info(
            "keep_none_day: %s, keep_none_model_days_list: %s",
            keep_none_day,
            keep_none_model_days_list,
        )

        for model_dir in keep_none_model_days_list:
            fs.delete(model_dir, recursive=True)
            logging.info("clean model dir %s", model_dir)

        keep_final_day = latest_model_hour - timedelta(
            days=keep_final_before_days
        )
        keep_final_day = keep_final_day.strftime("%Y%m%d")
        keep_final_model_days_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f)
            and re.match(MODEL_DIR_PATTERN, f)
            and f[-8:] <= keep_final_day
        ]
        logging.info(
            "keep_final_day: %s, keep_final_model_days_list: %s",
            keep_final_day,
            keep_final_model_days_list,
        )

        model_days_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f) and re.match(MODEL_DIR_PATTERN, f)
        ]

        model_hours_list = []
        for model_dir in model_days_list:
            model_hours_list.extend(
                [
                    f
                    for f in fs.ls(model_dir)
                    if fs.isdir(f) and re.match(HOURLY_MODEL_DIR_PATTERN, f)
                ]
            )

        if len(model_hours_list) < 3:
            logging.info(
                "Too few model versions %d, skip to delete",
                len(model_hours_list),
            )
            return

        for model_dir in keep_final_model_days_list:
            for hour in range(0, 23):
                path = os.path.join(model_dir, "{:02d}".format(hour))
                if fs.exists(path):
                    fs.delete(path, recursive=True)
                    logging.info("clean model dir: %s", path)
