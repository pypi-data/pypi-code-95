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
from bmlx_components.xdl_base.reader import XdlReader
from bmlx_components.xdl_base.executor import XdlExecutor
from bmlx_components.xdl_evaluator.runner import XdlEvalRunner


class XdlEvaluatorExecutor(XdlExecutor):
    def execute_as_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        """
        XDL Evaluator Executor invokes a training_fn callback function provided by
        the user via the module_file parameter.
        """

        stage = exec_properties["stage"]
        parameters = exec_properties["parameters"]
        schema = self._resolve_schema(input_dict["schema"])

        module = exec_properties.get("module")

        if not module:
            raise ValueError("'module' field not set in 'exec_properties'.")

        meta_output_path = artifact_utils.get_single_uri(output_dict["output"])
        # eval模式phase = 1
        updated_dict = {"phases": 1, "reader.enable_state": False}

        if exec_properties["enable_trace"]:
            updated_dict.update({"hooks.trace.output_dir": meta_output_path})
        else:
            updated_dict.update({"hooks.trace": {}})

        if parameters["hooks"]["save_metrics"].exists():
            updated_dict["hooks.save_metrics.output_file_path"] = os.path.join(
                meta_output_path,
                parameters["hooks"]["save_metrics"]["output_file_name"].as_str(
                    "metrics.txt"
                ),
            )

        parameters.set_args(updated_dict)

        runner = XdlEvalRunner(
            model_module=module,
            parameters=parameters,
            stage=stage,
            is_training=False,
            schema=schema,
            is_local=exec_properties["is_local"],
            metrics_sinker=self._tf_metrics_sinker(
                exec_properties=exec_properties
            ),
        )
        # 这里给xdl.reader.script 进行赋值，来传递一些在 用户的 convert 脚本中会用到的参数
        reader_conf = parameters["reader"]
        reader_conf.set_args(
            {"script": self._substitude_reader_script(reader_conf["script"].as_str()) + f" -jt {stage} -p bmlx"}
        )
        reader = XdlReader.get_reader(
            conf=reader_conf,
            name="xdl_reader",
            input_dict=input_dict,
            schema=schema,
            sampling_rate=exec_properties["sampling_rate"],
            specific_samples=True if "specific_samples" in input_dict else False,
        )

        eval_slots = []
        if exec_properties["eval_slots"]:
            if not parameters["eval_slots"].exists() or not parameters[
                "eval_slots"
            ].get(list):
                raise RuntimeError(
                    "XdlEvaluator setted to eval slot but with no eval_slots provided in configuration file"
                )
            else:
                eval_slots = parameters["eval_slots"].get(list)

        runner.run(reader=reader, eval_slots=eval_slots)

    def execute_as_chief_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        pass