# -*- coding: UTF-8 -*-
from bmlx.flow import (
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
    Channel,
    Executor,
    Artifact
)
from bmlx_components import custom_artifacts
from typing import Text, Dict, List, Any
import logging
import re
import os
import time
from datetime import datetime, timedelta
from pytz import timezone
from bmlx_components.importer_node.import_checker import (
    check_succ_flag,
    check_skip_flag,
)


class OriginSampleSelectorExecutor(Executor):
    hour_re_pattern = "[0-9]{8}/[0-9]{2}$"
    day_re_pattern = "[0-9]{8}$"
    hour_date_format = "%Y%m%d/%H"
    day_date_format = "%Y%m%d"

    def execute(
            self,
            input_dict: Dict[Text, List[Artifact]],
            output_dict: Dict[Text, List[Artifact]],
            exec_properties: Dict[Text, Any]
    ):
        self._log_startup(input_dict, output_dict, exec_properties)

        candidate_uri_base = exec_properties["candidate_uri_base"]
        candidate_time_range = exec_properties["candidate_time_range"]
        trace_back_length = exec_properties["trace_back_length"]
        output_uri_base = exec_properties["output_uri_base"]
        max_wait_minutes = exec_properties["max_wait_minutes"]
        min_selected_ready_uris = exec_properties["min_selected_ready_uris"]
        max_selected_ready_uris = exec_properties["max_selected_ready_uris"]

        selected_ready_uris = self.select_ready_uris(
            candidate_uri_base,
            candidate_time_range,
            trace_back_length,
            output_uri_base,
            max_wait_minutes,
            min_selected_ready_uris,
            max_selected_ready_uris,
        )

        if not selected_ready_uris:
            raise RuntimeError(
                "Select ready failed with candidate_uri_base %s,"
                "candidate_time_range %s\n"
                "Possible Reasons: \n"
                "(1. candidate_time_range 还未ready)\n"
                "(2. candidate_uri_base 目录不存在)\n"
                "(3. 时间范围格式错误 天级/小时级)\n"
                % (
                    candidate_uri_base,
                    candidate_time_range,
                )
            )

        logging.info("finally selected ready uris: %s", selected_ready_uris)

        output_dict["ready_uris"] = []
        for uri in selected_ready_uris:
            artifact = Artifact(type_name=custom_artifacts.OriginSamples.TYPE_NAME)
            artifact.meta.uri = uri
            output_dict["ready_uris"].append(artifact)

    def select_ready_uris_from_candidates(
            self,
            candidate_uris,
            max_wait_minutes,
            min_selected_ready_uris,
            max_selected_ready_uris,
    ):
        """
        candidate_uris: 候选输入路径, 有些可能不满足要求
        max_wait_minutes: 最多等待时间
        min_selected_ready_uris: fg最少使用多少个小时数据
        max_selected_ready_uris: fg最多使用多少个小时数据
        """
        current_timestamp = int(datetime.now().timestamp())
        final_timestamp = current_timestamp + max_wait_minutes * 60
        selected_ready_uris = []

        while current_timestamp <= final_timestamp and not selected_ready_uris:
            for candidate_uri, output_uri in candidate_uris:
                if check_succ_flag(candidate_uri) and not check_skip_flag(
                        candidate_uri
                ):
                    if not check_succ_flag(output_uri):
                        logging.info(
                            "Select ready uri %s successfully!", candidate_uri
                        )
                        selected_ready_uris.append(candidate_uri)
                    else:
                        logging.info(
                            "output uri %s success file exists!", output_uri
                        )

                if len(selected_ready_uris) >= max_selected_ready_uris:
                    break

            if len(selected_ready_uris) < min_selected_ready_uris:
                time.sleep(60)
                current_timestamp = int(datetime.now().timestamp())
                logging.info("waiting uris to be ready...")
        return selected_ready_uris

    def gen_candidate_uris_delta(
            self, candidate_uri_base, output_uri_base, start_uri, end_uri, delta
    ):
        if delta == 1:
            time_format = self.hour_date_format
        else:
            time_format = self.day_date_format

        tz = " %z"
        cst_tz = timezone("Asia/Chongqing")

        begin_date = datetime.strptime(f"{start_uri} +0800", time_format + tz)

        if end_uri:
            end_date = datetime.strptime(f"{end_uri} +0800", time_format + tz)
        else:
            end_date = datetime.now(cst_tz)

        candidate_ready_uris = []
        while begin_date <= end_date:
            candidate_ready_uris.append(
                (os.path.join(candidate_uri_base, begin_date.strftime(time_format)),
                 os.path.join(output_uri_base, begin_date.strftime(time_format)))
            )
            begin_date += timedelta(hours=delta)
        return candidate_ready_uris

    def gen_candidate_uris(
            self, candidate_uri_base, output_uri_base, start_uri, end_uri,
    ):
        if re.match(self.hour_re_pattern, start_uri) and re.match(self.hour_re_pattern, end_uri):
            return self.gen_candidate_uris_delta(
                candidate_uri_base,
                output_uri_base,
                start_uri,
                end_uri,
                1)
        elif re.match(self.day_re_pattern, start_uri) and re.match(self.day_re_pattern, end_uri):
            return self.gen_candidate_uris_delta(
                candidate_uri_base,
                output_uri_base,
                start_uri,
                end_uri,
                24)
        else:
            raise ValueError("invalid start_time or end_time: {}-{}".format(start_uri, end_uri))

    def gen_start_end_from_range(self, candidate_time_range, trace_back_length):
        time_range_list = ["", ""]
        if candidate_time_range:
            time_range_list = list(map(lambda elem: elem.strip(), candidate_time_range.split("-")))
        if len(time_range_list) != 2:
            raise ValueError(
                "candidate_time_range format error: "
                "should follow start(null)-end/(null)")

        start_res, end_res = time_range_list
        cst_tz = timezone("Asia/Chongqing")
        tz = " %z"

        # check start & end 's format match or not
        if start_res or end_res:
            check_res = start_res if start_res else end_res
            if start_res and end_res:
                if not (re.match(self.hour_re_pattern, start_res) and re.match(self.hour_re_pattern, end_res)) \
                        and not (re.match(self.day_re_pattern, start_res) and re.match(self.day_re_pattern, end_res)):
                    raise ValueError(
                        "start:%s and end:%s format diffs,"
                        "should all be hour or day"
                        % (start_res, end_res))

            # end为空，设置end为当前时间，并根据 start 设置end
            if not end_res:
                if re.match(self.hour_re_pattern, check_res):
                    date_format = self.hour_date_format
                else:
                    date_format = self.day_date_format
                end_res = datetime.now(cst_tz).strftime(date_format)
            elif not start_res:
                raise ValueError(
                    "can not set end: %s without set start: %s"
                    % (end_res, start_res))
        # trace back mode
        else:
            if not re.match("^[0-9]*[hdHD]{1}$", trace_back_length):
                raise ValueError(
                    "trace_back_length: %s does not match pattern: %s"
                    % trace_back_length, "^[0-9]*[hdHD]{1}$")
            length_num = int(re.sub("[^0-9]", "", trace_back_length))
            if re.match("^[0-9]*[hH]{1}$", trace_back_length):
                date_format = self.hour_date_format
            else:
                date_format = self.day_date_format
                length_num = length_num * 24
            end_res = datetime.now(cst_tz).strftime(date_format)
            start_ts = datetime.strptime(f"{end_res} +0800", date_format + tz)
            start_ts -= timedelta(hours=length_num)
            start_res = start_ts.strftime(date_format)

        return start_res, end_res

    def select_ready_uris(
            self,
            candidate_uri_base,
            candidate_time_range,
            trace_back_length,
            output_uri_base,
            max_wait_minutes,
            min_selected_ready_uris,
            max_selected_ready_uris,
    ):
        start_time, end_time = self.gen_start_end_from_range(candidate_time_range, trace_back_length)
        candidate_ouput_uris = self.gen_candidate_uris(
            candidate_uri_base, output_uri_base, start_time, end_time,
        )
        if not candidate_ouput_uris:
            return candidate_ouput_uris
        return self.select_ready_uris_from_candidates(
            candidate_ouput_uris,
            max_wait_minutes,
            min_selected_ready_uris,
            max_selected_ready_uris,
        )