"""bmlx xdl evaluator executor."""
import os
import logging
import re
import xdl
import functools
import random
from typing import Any, Dict, List, Text

from bmlx.flow import Executor, Artifact
from bmlx_components.proto import schema_pb2, model_pb2
from bmlx.utils import import_utils, artifact_utils, io_utils
from bmlx_components.xdl_base.runner import XdlRunner
from bmlx_components.xdl_base.reader import XdlReader
from bmlx_components.xdl_base.executor import XdlExecutor

PREDICT_TRACE_FILE = "predict.trace"


class XdlPredictorExecutor(XdlExecutor):
    def execute_as_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        """
        XDL Predictor Executor invokes a training_fn callback function provided by
        the user via the module_file parameter.
        """
        schema = self._resolve_schema(input_dict["schema"])
        assert (
            exec_properties.get("parameters") is not None
        ), "please call _load_xdl_parameters first"

        # resolve train func
        stage = exec_properties["stage"]
        module = exec_properties.get("module")
        parameters = exec_properties["parameters"]
        # predict 模式phase = 1
        updated_dict = {"phases": 1, "reader.enable_state": False}

        if exec_properties["enable_trace"]:
            meta_output_path = artifact_utils.get_single_uri(
                output_dict["output"]
            )
            updated_dict.update({"hooks.trace.output_dir": meta_output_path})
            # 强制限制 predict 的trace file， 用于 在 xdl-convert的时候，可以通过相同文件名获取
            updated_dict.update(
                {"hooks.trace.output_file_name": PREDICT_TRACE_FILE}
            )
        else:
            updated_dict.update({"hooks.trace": {}})

        if exec_properties["score_validation"]:
            updated_dict["reader.shuffle_file"] = False
            updated_dict["reader.shuffle_sample"] = False
            updated_dict["reader.reverse_file"] = False
            updated_dict["reader.batch_size"] = 1

        if parameters["hooks"]["save_metrics"].exists():
            updated_dict["hooks.save_metrics.output_file_path"] = os.path.join(
                meta_output_path,
                parameters["hooks"]["save_metrics"]["output_file_name"].as_str(
                    "metrics.txt"
                ),
            )

        parameters.set_args(updated_dict)

        module = exec_properties.get("module")

        if not module:
            raise ValueError(
                "'module_file' or 'module' field not set in 'exec_properties'."
            )

        runner = XdlRunner(
            model_module=module,
            parameters=parameters,
            stage=stage,
            is_training=False,
            schema=schema,
            is_local=exec_properties["is_local"],
        )

        reader_conf = parameters["reader"]
        # 这里给xdl.reader.script 进行赋值，来传递一些在 用户的 convert 脚本中会用到的参数
        reader_conf.set_args(
            {"script": self._substitude_reader_script(reader_conf["script"].as_str()) + f" -jt {stage} -p bmlx"}
        )
        reader = XdlReader.get_reader(
            conf=reader_conf,
            name="xdl_reader",
            input_dict=input_dict,
            schema=schema,
            sampling_rate=exec_properties["sampling_rate"],
        )

        runner.run(reader=reader)

    def execute_as_chief_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        pass