import os
import logging
import re
from bmlx.utils import artifact_utils, io_utils
from bmlx_components.proto import model_pb2
from bmlx_components.xdl_base.driver import XdlDriver
from bmlx.execution.execution import ExecutionInfo
from typing import Dict, Text, Any
from bmlx.flow import Channel, Pipeline, Component, DriverArgs

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

class XdlPredictorDriver(XdlDriver):
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
        ret = super(XdlPredictorDriver, self).pre_execution(
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
            
    def _resolve_model_uri(self, model_meta_path):
        model_pb = io_utils.parse_pbtxt_file(model_meta_path, model_pb2.Model())
        if not (model_pb and model_pb.model_path):
            raise RuntimeError(
                "invalid model meta info parsed from %s" % model_meta_path
            )
        logging.info("parsed model meta info: %s", model_pb)

        return os.path.join(model_pb.model_path, model_pb.model_version)

    def _resolve_model_paths(self, input_dict, exec_properties):
        model_uri = ""
        if "model" in input_dict:
            # TODO @sunkaicheng: 这块 uri的管理有点乱，需要重构
            if len(input_dict["model"]) > 0:
                # 使用 input-dcit 传入的uri，可能是meta 信息 （比如train之后的结果）
                model_uri = artifact_utils.get_single_uri(input_dict["model"])
                # 通过bmlx的 meta 文件获取model uri
                if io_utils.exists(os.path.join(model_uri, "model.pbtxt")):
                    model_uri = self._resolve_model_uri(
                        os.path.join(model_uri, "model.pbtxt")
                    )

        if not model_uri:
            raise RuntimeError("predictor must have model input")

        model_bank_uri = self._get_model_bank_uri(
            model_uri, exec_properties["model_file_pattern"]
        )
        # eval 阶段内存优化，强制只加载phase0 的 embedding 数据
        # TDOO: find a better way to handle model bank uri for different job types
        model_bank_uri = (
            "re#phase0.*,xdl_global_step@" + model_bank_uri.split("@")[1]
        )
        return model_bank_uri, exec_properties.get("model_uri_base", "")