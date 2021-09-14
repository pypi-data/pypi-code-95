import os
import copy
import logging
import re
import abc

from bmlx.execution.driver import BaseDriver
from typing import Dict, Text, Any, Optional, Tuple
from bmlx.flow import Channel, DriverArgs, Pipeline, Component
from bmlx.execution.execution import ExecutionInfo
from bmlx.config import Configuration
from bmlx.utils import json_utils, io_utils

MY_DIR = os.path.dirname(os.path.realpath(__file__))


class XdlDriver(BaseDriver):
    @abc.abstractmethod
    def _resolve_model_paths(
        self, input_dict, exec_properties
    ) -> Tuple[Text, Text]:
        raise NotImplementedError("please not use 'XdlLauncher' directly ")

    @abc.abstractmethod
    def _rewrite_launch_config(self, exec_properties):
        raise NotImplementedError("super method wont override")

    def _zk_addr(self, exec_properties) -> Text:
        return "zfs://%s/mlplat/bmlx/xdl-k8s/ps/%s" % (
            ",".join(
                exec_properties["runtime_configs"]["zk_addr"].as_str_seq()
            ),
            exec_properties["job_id"],
        )

    def _get_model_bank_uri(self, model_uri, model_file_pattern):
        # get model bank infos
        # xdl的model bank传参格式为 {regex}@{uri}, 比较奇怪，这里暂时兼容格式，之后有时间再改
        regex_str = ",".join(
            ["re#%s" % file_pattern for file_pattern in model_file_pattern]
        )

        model_bank_format = "{regex}@{uri}"
        fs, path = io_utils.resolve_filesystem_and_path(model_uri)
        if not fs.exists(path):
            raise RuntimeError(
                "resolved model uri %s does not exist!" % model_uri
            )

        logging.info("get_model_bank: resolved model uri %s", model_uri)
        if not re.match(
            r"^hdfs:\/\/[0-9a-zA-Z-_\.,\/]+\/[0-9]{8}\/[0-9]{2}\/?$", model_uri
        ) and not re.match(
            r"^hdfs:\/\/[0-9a-zA-Z-_\.,\/]+\/[0-9]{8}\/?$", model_uri
        ):
            raise ValueError("invalid model uri %s", model_uri)

        return model_bank_format.format(regex=regex_str, uri=model_uri)

    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ) -> ExecutionInfo:
        ret = super(XdlDriver, self).pre_execution(
            input_dict,
            output_dict,
            exec_properties,
            pipeline,
            component,
            driver_args,
        )

        # 下面这段代码都是调整参数，和设置一些XDL任务公用的参数

        # runtime_configs是用户传递的覆盖性质的参数
        param_view = ret.exec_properties["runtime_configs"]["parameters"]
        user_config = []
        if param_view.exists():
            user_config = param_view.as_filename(relative_to="project")

            # xdl_base 级别的配置
            ret.exec_properties["parameters"] = Configuration(
                os.path.join(MY_DIR, "default.yml"),
                user_config,
                value_converter=lambda x: x["value"]
                if isinstance(x, dict) and "value" in x
                else x,
            )

        # 生成 job_id
        if "job_id" not in ret.exec_properties:
            # generate job_id by other infos in 'submit' stage
            # job id and task index are required for distributed xdl running
            ret.exec_properties["job_id"] = "bmlx-%s" % (
                "%s-%s-%s"
                % (
                    driver_args.pipeline_execution.name,
                    component.id.replace("_", "-"),
                    str(driver_args.pipeline_execution.id)[:8],
                )
            ).lower()[-30:].lstrip("-")

        if driver_args.local_mode:
            ret.exec_properties["is_local"] = True
        else:
            ret.exec_properties["is_local"] = False
            ret.exec_properties["zk_addr"] = self._zk_addr(
                exec_properties=ret.exec_properties
            )
            ret.exec_properties["chief_zk_addr"] = (
                "%s-ck" % ret.exec_properties["zk_addr"]
            )

        # 解析model bank参数
        model_bank, ckpt = self._resolve_model_paths(
            exec_properties=ret.exec_properties, input_dict=ret.input_dict
        )
        logging.info("[model_bank] %s", model_bank)
        logging.info("[ckpt] %s", ckpt)
        ret.exec_properties["model_bank"] = model_bank
        ret.exec_properties["ckpt"] = ckpt

        # 增加一些额外的参数
        ret.exec_properties[
            "pipeline_execution_id"
        ] = driver_args.pipeline_execution.id
        ret.exec_properties["component_id"] = component.id
        ret.exec_properties[
            "experiment_id"
        ] = driver_args.pipeline_execution.experiment_id
        ret.exec_properties[
            "artifact_storage_base"
        ] = driver_args.artifact_storage_base

        # 子Driver可能会重写一些关键性的参数
        self._rewrite_launch_config(ret.exec_properties)

        # 因为框架结构的关系，exec_properties里面埋了大量的参数，不太利于阅读，所以这里使用大量的assert
        # 一是方便确认参数，二是提前检查问题

        # TODO: 需要从 meta server中获取一些参数，比如提交xdl 任务的namespace 放到 exec_properties 中
        # assert "namespace" in ret.exec_properties
        return ret
