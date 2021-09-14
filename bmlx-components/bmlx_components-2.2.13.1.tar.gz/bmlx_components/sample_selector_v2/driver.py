import logging
import os
import time
import re
from datetime import datetime, timedelta
from pytz import timezone
from typing import Dict, Text, Any, Optional

from bmlx.flow import Driver, DriverArgs, Channel, Pipeline, Component, Artifact
from bmlx.metadata.metadata import Metadata
from bmlx.utils import io_utils
from bmlx.execution.execution import ExecutionInfo
from bmlx.execution.driver import BaseDriver
from bmlx_components.importer_node.import_checker import (
    check_succ_flag,
    check_skip_flag,
)

from bmlx.metadata import standard_artifacts

MODEL_DIR_PATTERN = "[\s\S]*2[0-9]{3}[0-1][0-9]{3}$"


class SampleSelectorDriver(BaseDriver):
    def __init__(self, metadata: Metadata):
        self._metadata = metadata

    def select_samples_from_candidates(
        self,
        candidate_sample_uris,
        max_wait_minutes,
        min_selected_sample_days,
        max_selected_sample_days,
        regular_day_interval,
    ):
        """
        candidate_sample_uris: 候选samples, 有些可能不满足要求
        max_wait_minutes: 最多等待时间
        min_selected_sample_days: 一次训练最少使用多少天数据
        max_selected_sample_days: 一次训练最多使用多少天数据
        regular_day_interval: 选择某个固定长度的时间间隔范围内的所有样本
        """
        current_timestamp = int(datetime.now().timestamp())
        final_timestamp = current_timestamp + max_wait_minutes * 60
        selected_sample_uris = []
        if regular_day_interval is not None:
            max_selected_sample_days = regular_day_interval + 1

        while current_timestamp <= final_timestamp and not selected_sample_uris:
            for sample_uri in candidate_sample_uris:
                if check_succ_flag(sample_uri) and not check_skip_flag(
                    sample_uri
                ):
                    logging.info(
                        "Select sample with uri %s successfully!", sample_uri
                    )
                    selected_sample_uris.append(sample_uri)

                if len(selected_sample_uris) >= max_selected_sample_days:
                    break

            if len(selected_sample_uris) < min_selected_sample_days:
                time.sleep(60)
                current_timestamp = int(datetime.now().timestamp())
                logging.info("waiting samples to be ready...")
        return selected_sample_uris

    def search_last_model_day(self, model_uri_base, start_sample_day):
        end_search_day = datetime.strptime(
            f"{start_sample_day} +0800", "%Y%m%d %z"
        )
        end_search_day -= timedelta(days=1)
        end_search_day = end_search_day.strftime("%Y%m%d")

        fs, path = io_utils.resolve_filesystem_and_path(model_uri_base)
        if not fs.exists(path):
            logging.info("model uri base %s does not exist!" % model_uri_base)
            return None

        model_days_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f)
            and re.match(MODEL_DIR_PATTERN, f)
            and f[-8:] >= end_search_day
        ]
        model_days_list.sort(reverse=True)
        logging.info("model days list: %s", model_days_list)

        last_model_day = None
        for model_dir in model_days_list:
            if check_succ_flag(model_dir):
                last_model_day = model_dir[-8:]
                break
        return last_model_day

    def gen_candidate_samples(
        self,
        sample_uri_base,
        last_model_day,
        start_sample_day,
        end_sample_day,
        regular_day_interval,
    ):
        cst_tz = timezone("Asia/Chongqing")

        if end_sample_day:
            end_day = datetime.strptime(f"{end_sample_day} +0800", "%Y%m%d %z")
        else:
            end_day = datetime.now(cst_tz)
        logging.info("[End_day]%s", end_day)

        # regular_day_interval更高优先级，选择某个固定长度的时间间隔范围内的所有样本
        if regular_day_interval is not None:
            begin_day = end_day - timedelta(days=regular_day_interval)
            logging.info("[Begin_day]%s", begin_day)
        else:
            begin_day = datetime.strptime(f"{start_sample_day} +0800", "%Y%m%d %z")
            if last_model_day:
                begin_day = max(
                    begin_day,
                    datetime.strptime(f"{last_model_day} +0800", "%Y%m%d %z")
                    + timedelta(days=1),
                )

        candidate_sample_uris = []
        while begin_day <= end_day:
            candidate_sample_uris.append(
                os.path.join(sample_uri_base, begin_day.strftime("%Y%m%d"))
            )
            begin_day += timedelta(days=1)
        return candidate_sample_uris

    def select_samples(
        self,
        sample_uri_base,
        last_model_day,
        start_sample_day,
        end_sample_day,
        min_selected_sample_days,
        max_selected_sample_days,
        regular_day_interval,
        max_wait_minutes,
    ):
        candidate_sample_uris = self.gen_candidate_samples(
            sample_uri_base,
            last_model_day,
            start_sample_day,
            end_sample_day,
            regular_day_interval,
        )
        if not candidate_sample_uris:
            return candidate_sample_uris
        return self.select_samples_from_candidates(
            candidate_sample_uris,
            max_wait_minutes,
            min_selected_sample_days,
            max_selected_sample_days,
            regular_day_interval,
        )

    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ) -> ExecutionInfo:
        logging.info("sample_selector exec properties: %s", exec_properties)
        input_artifacts = self.resolve_input_artifacts(
            input_dict, component, driver_args
        )

        sample_uri_base = exec_properties["sample_uri_base"]
        model_uri_base = exec_properties["model_uri_base"]
        start_sample_day = exec_properties["start_sample_day"]
        end_sample_day = exec_properties["end_sample_day"]
        max_wait_minutes = exec_properties["max_wait_minutes"]
        min_selected_sample_days = exec_properties["min_selected_sample_days"]
        max_selected_sample_days = exec_properties["max_selected_sample_days"]
        regular_day_interval = exec_properties["regular_day_interval"]
        logging.info("[regular_day_interval]%s", regular_day_interval)

        if not re.match("[\d+]{8}$", start_sample_day):
            raise ValueError(
                "start sample day does not match pattern [\d+]{8}$"
            )

        last_model_day = self.search_last_model_day(
            model_uri_base, start_sample_day
        )

        if last_model_day:
            last_model_uri = os.path.join(model_uri_base, last_model_day)
        else:
            last_model_uri = ""

        selected_sample_uris = self.select_samples(
            sample_uri_base,
            last_model_day,
            start_sample_day,
            end_sample_day,
            min_selected_sample_days,
            max_selected_sample_days,
            regular_day_interval,
            max_wait_minutes,
        )

        if not selected_sample_uris:
            raise RuntimeError(
                "Select samples failed with sample_uri_base %s,"
                "model_uri_base %s, start_sample_day %s, end_sample_day %s,\n"
                "Possible Reasons: \n"
                "(1. start_sample_day > end_sample_day)\n"
                "(2. start_sample_day ~ end_sample_day 的样本在model_uri_base 目录下都有相应的训练好的模型)\n"
                "(3. start_sample_day ~ end_sample_day 的样本都还未生成)\n"
                "(4. sample_uri_base 目录不存在)\n"
                % (
                    sample_uri_base,
                    model_uri_base,
                    start_sample_day,
                    end_sample_day,
                )
            )

        logging.info("selected last model %s", last_model_uri)
        logging.info("finally selected samples: %s", selected_sample_uris)

        output_artifacts = {}
        assert len(output_dict) == 2

        output_artifacts["samples"] = []
        for uri in selected_sample_uris:
            artifact = Artifact(type_name=standard_artifacts.Samples.TYPE_NAME)
            artifact.meta.uri = uri
            artifact.meta.producer_component = component.id
            output_artifacts["samples"].append(artifact)

        output_artifacts["model"] = []
        if last_model_uri:
            artifact = Artifact(type_name=standard_artifacts.Model.TYPE_NAME)
            artifact.meta.uri = last_model_uri
            artifact.meta.producer_component = component.id
            output_artifacts["model"].append(artifact)

        return ExecutionInfo(
            input_dict=input_artifacts,
            output_dict=output_artifacts,
            exec_properties=exec_properties,
            use_cached_result=False,
        )
