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
        min_selected_sample_hours,
        max_selected_sample_hours,
    ):
        """
        candidate_sample_uris: 候选samples, 有些可能不满足要求
        max_wait_minutes: 最多等待时间
        min_selected_sample_hours: 一次训练最少使用多少个小时数据
        max_selected_sample_hours: 一次训练最多使用多少个小时数据
        """
        current_timestamp = int(datetime.now().timestamp())
        final_timestamp = current_timestamp + max_wait_minutes * 60
        selected_sample_uris = []

        while current_timestamp <= final_timestamp and not selected_sample_uris:
            for sample_uri in candidate_sample_uris:
                if check_succ_flag(sample_uri) and not check_skip_flag(
                    sample_uri
                ):
                    logging.info(
                        "Select sample with uri %s successfully!", sample_uri
                    )
                    selected_sample_uris.append(sample_uri)

                if len(selected_sample_uris) >= max_selected_sample_hours:
                    break

            if len(selected_sample_uris) < min_selected_sample_hours:
                time.sleep(60)
                current_timestamp = int(datetime.now().timestamp())
                logging.info("waiting samples to be ready...")
        return selected_sample_uris

    def search_last_model_hour(self, model_uri_base, start_sample_hour):
        end_search_hour = datetime.strptime(
            f"{start_sample_hour} +0800", "%Y%m%d/%H %z"
        )
        end_search_hour -= timedelta(hours=1)
        end_search_hour = end_search_hour.strftime("%Y%m%d/%H")

        fs, path = io_utils.resolve_filesystem_and_path(model_uri_base)
        if not fs.exists(path):
            logging.info("model uri base %s does not exist!" % model_uri_base)
            return None

        model_days_list = [
            f
            for f in fs.ls(path)
            if fs.isdir(f) and re.match(MODEL_DIR_PATTERN, f)
        ]

        model_days_list.sort(reverse=True)

        last_model_hour = None
        for model_dir in model_days_list:
            if last_model_hour or model_dir[-8:] < end_search_hour[:-3]:
                break
            model_hours_list = [f for f in fs.ls(model_dir) if fs.isdir(f)]
            model_hours_list.sort(reverse=True)
            for hourly_model_dir in model_hours_list:
                if (
                    check_succ_flag(hourly_model_dir)
                    and hourly_model_dir[-11:] >= end_search_hour
                ):
                    last_model_hour = hourly_model_dir[-11:]
                    break
        return last_model_hour

    def gen_candidate_samples(
        self,
        sample_uri_base,
        last_model_hour,
        start_sample_hour,
        end_sample_hour,
    ):
        begin_hour = datetime.strptime(
            f"{start_sample_hour} +0800", "%Y%m%d/%H %z"
        )
        if last_model_hour:
            begin_hour = max(
                begin_hour,
                datetime.strptime(f"{last_model_hour} +0800", "%Y%m%d/%H %z")
                + timedelta(hours=1),
            )

        cst_tz = timezone("Asia/Chongqing")

        if end_sample_hour:
            end_hour = datetime.strptime(
                f"{end_sample_hour} +0800", "%Y%m%d/%H %z"
            )
        else:
            end_hour = datetime.now(cst_tz)

        # 每次选择不跨越23点，即要求 每次选择样本训练如果包含23点，那么23点必须作为最后一个样本小时 形成一个版本的模型
        if begin_hour.day != end_hour.day:
            end_hour = datetime.strptime(
                begin_hour.strftime("%Y%m%d/23 +0800"), "%Y%m%d/%H %z"
            )

        candidate_sample_uris = []
        while begin_hour <= end_hour:
            candidate_sample_uris.append(
                os.path.join(sample_uri_base, begin_hour.strftime("%Y%m%d/%H"))
            )
            begin_hour += timedelta(hours=1)
        return candidate_sample_uris

    def select_samples(
        self,
        sample_uri_base,
        last_model_hour,
        start_sample_hour,
        end_sample_hour,
        min_selected_sample_hours,
        max_selected_sample_hours,
        max_wait_minutes,
    ):
        candidate_sample_uris = self.gen_candidate_samples(
            sample_uri_base,
            last_model_hour,
            start_sample_hour,
            end_sample_hour,
        )
        if not candidate_sample_uris:
            return candidate_sample_uris
        return self.select_samples_from_candidates(
            candidate_sample_uris,
            max_wait_minutes,
            min_selected_sample_hours,
            max_selected_sample_hours,
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
        start_sample_hour = exec_properties["start_sample_hour"]
        end_sample_hour = exec_properties["end_sample_hour"]
        max_wait_minutes = exec_properties["max_wait_minutes"]
        min_selected_sample_hours = exec_properties["min_selected_sample_hours"]
        max_selected_sample_hours = exec_properties["max_selected_sample_hours"]

        if not re.match("[\d+]{8}\/[\d+]{2}", start_sample_hour):
            raise ValueError(
                "start sample hour does not match pattern [\d+]{8}\/[\d+]{2}"
            )

        last_model_hour = self.search_last_model_hour(
            model_uri_base, start_sample_hour
        )

        if last_model_hour:
            last_model_uri = os.path.join(model_uri_base, last_model_hour)
        else:
            last_model_uri = ""

        selected_sample_uris = self.select_samples(
            sample_uri_base,
            last_model_hour,
            start_sample_hour,
            end_sample_hour,
            min_selected_sample_hours,
            max_selected_sample_hours,
            max_wait_minutes,
        )

        if not selected_sample_uris:
            raise RuntimeError(
                "Select samples failed with sample_uri_base %s,"
                "model_uri_base %s, start_sample_hour %s, end_sample_hour %s,\n"
                "Possible Reasons: \n"
                "(1. start_sample_hour > end_sample_hour)\n"
                "(2. start_sample_hour ~ end_sample_hour 的样本在model_uri_base 目录下都有相应的训练好的模型)\n"
                "(3. start_sample_hour ~ end_sample_hour 的样本都还未生成)\n"
                "(4. sample_uri_base 目录不存在)\n"
                % (
                    sample_uri_base,
                    model_uri_base,
                    start_sample_hour,
                    end_sample_hour,
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
            # 表示并不创建模型数据，只是引入之前创建好的模型
            artifact.meta.import_only = True
            output_artifacts["model"].append(artifact)

        return ExecutionInfo(
            input_dict=input_artifacts,
            output_dict=output_artifacts,
            exec_properties=exec_properties,
            use_cached_result=False,
        )
