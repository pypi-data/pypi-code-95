import logging, os, time, re, struct
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

def time2stamp(time_str):
    """ this function is used for convert time to timestmap """
    from datetime import datetime
    time_obj = datetime.strptime(time_str, '%Y-%m-%d/%H:%M:%S')
    timestamp = time.mktime(time_obj.timetuple()) * 1000.0
    return int(timestamp)

class SampleSelectorForOnlineLearningDriver(BaseDriver):
    def __init__(self, metadata: Metadata):
        self._metadata = metadata

    def search_last_model_version(self, model_uri_base):
        fs, path = io_utils.resolve_filesystem_and_path(model_uri_base)
        if not fs.exists(path):
            raise Exception("model uri base: %s does not exist!" % model_uri_base)
        checkpoint_file = os.path.join(model_uri_base, "checkpoints")
        if not fs.exists(checkpoint_file):
            logging.info("There are no model in model_uri_base")
            return ""
       
        with fs.open(checkpoint_file, "rb") as fd:
            content = fd.read()
        assert len(content) >= 8, "There is empty checkpoint file"
        begin = 0
        ckpt_num = struct.unpack("<Q", content[begin:begin+8:])[0]
        assert ckpt_num > 0, "There is empty checkpoint file"
        begin = begin + 8
        for i in range(ckpt_num):
            length = struct.unpack("<Q", content[begin:begin+8:])[0]
            begin = begin + 8
            ckpt_version = content[begin:begin+length:]
            begin = begin + length
        return ckpt_version.decode("utf-8")

    def generate_sample_uri(self, sample_uri_base):
        path = sample_uri_base[:]
        normal_path = None
        if "#" in path:
            serverAndTopic, begin_off = path.split("#")
            normal_path = serverAndTopic + "#0_32535140969000" # 3000-12-31 11:09:21
            if "_" in begin_off:
                begin_off, end_off = begin_off.split("_")
                begin_stamp = time2stamp(begin_off)
                end_stamp = time2stamp(end_off)
                print(begin_off, begin_stamp, flush=True)
                print(end_off, end_stamp, flush=True)
            else:
                begin_stamp = time2stamp(begin_off)
                end_stamp = 32535140969000
                path = serverAndTopic + "#" + str(begin_stamp) + "_" + str(end_stamp)
        else:
            path = path + "#" + "0" + "_" + "32535140969000" # 9999-12-31 11:09:29
            normal_path = path
        print("sample_uri: ", path, flush=True)
        if sample_uri_base.startswith("kafka"):
            return [path]
        elif sample_uri_base.startswith("pulsar"):
            return [path, normal_path]
        else:
            raise Exception("The data source {} is not support".format(sample_uri_base))

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

        last_model_version = self.search_last_model_version(model_uri_base)
        last_model_uri = os.path.join(model_uri_base, last_model_version)
        
        sample_uris = self.generate_sample_uri(sample_uri_base)
        output_artifacts = {}
        assert len(output_dict) == 2

        output_artifacts["samples"] = []
        for uri in sample_uris:
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
