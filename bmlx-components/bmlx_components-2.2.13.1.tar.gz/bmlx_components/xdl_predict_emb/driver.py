import os
import logging
import re
from bmlx.utils import artifact_utils, io_utils
from bmlx_components.proto import model_pb2
from bmlx_components.xdl_base.driver import XdlDriver
from bmlx.execution.execution import ExecutionInfo
from typing import Dict, Text, Any
from bmlx.flow import Channel, Pipeline, Component, DriverArgs
from bmlx.execution.execution import ExecutionInfo

CEPH_ARTIFACT_PATH_PATTERN = "ceph://([a-zA-Z0-9\-_\.\/]*)(exp_[0-9]+)/(run_[0-9]+)/([a-zA-Z0-9\-_\.]+)"
HDFS_ARTIFACT_PATH = "hdfs://bigo-rt/user/bmlx/artifacts"

# 将ceph路径重构成hdfs指定路径
def reconstruct_path(ceph_path: Text):
    ret = re.match(CEPH_ARTIFACT_PATH_PATTERN, ceph_path)
    if ret is None or ret.group(0) != ceph_path:
        raise RuntimeError(
            "Reconstruct path failed: input (%s) is not ceph_artifact_path" %
            ceph_path
        )

    output_path = os.path.join(
        HDFS_ARTIFACT_PATH,
        ret.group(2), ret.group(3), ret.group(4)
    )
    return output_path

class XdlPredictEmbDriver(XdlDriver):
    # override super method
    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ) -> ExecutionInfo:
        ret = super(XdlPredictEmbDriver, self).pre_execution(
            input_dict,
            output_dict,
            exec_properties,
            pipeline,
            component,
            driver_args,
        )
        output_uri = artifact_utils.get_single_uri(
            ret.output_dict["output"]
        )
        logging.info("[origin]output_uri is %s", output_uri)
        changed_output_uri = reconstruct_path(output_uri)
        ret.output_dict["output"][0].meta.uri = changed_output_uri
        changed_output_uri = artifact_utils.get_single_uri(
            ret.output_dict["output"]
        )
        logging.info("[changed]output_uri is %s", changed_output_uri)
        return ret

    def _rewrite_launch_config(self, exec_properties):
        pass
            
    def _resolve_model_paths(self, input_dict, exec_properties):
        model_uri = ""
        if "model" in input_dict:
            if len(input_dict["model"]) > 0:
                model_uri = artifact_utils.get_single_uri(
                    input_dict["model"]
                )  
                if model_uri and io_utils.exists(os.path.join(model_uri, "model.pbtxt")):
                    model_pb = io_utils.parse_pbtxt_file(os.path.join(model_uri, "model.pbtxt"), model_pb2.Model())
                    model_uri = os.path.join(model_pb.model_path, model_pb.model_version)

        if "model_file_pattern" not in exec_properties:
            raise RuntimeError("model file pattern must set")

        warmup_opened = False
        # 如果选到了基础模型，则使用基础模型
        if model_uri:
            model_bank_uri = self._get_model_bank_uri(
                model_uri, exec_properties["model_file_pattern"]
            )
            warmup_opened = False
        # 如果没有基础模型，且设置了 warmup_model_bank
        elif exec_properties.get("warmup_model_bank"):
            warmups = exec_properties["warmup_model_bank"].split("@")
            if len(warmups) == 2 and io_utils.exists(warmups[1]):
                model_bank_uri = exec_properties["warmup_model_bank"]
                warmup_opened = True
        else:
            model_bank_uri = ""
            warmup_opened = False

        logging.info(
            "warmup %s, selected model bank uri: %s",
            "opened" if warmup_opened else "closed",
            model_bank_uri,
        )
        print("model_bank_uri: ", model_bank_uri, flush=True)
        return model_bank_uri, exec_properties.get("model_uri_base", "")

