"""BMLX XdlEvaluator component definition."""
from typing import Optional, Text, List
from bmlx.flow import (
    Channel,
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
)
from bmlx_components.xdl_evaluator.driver import XdlEvaluatorDriver
from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts
from bmlx_components.xdl_evaluator.executor import XdlEvaluatorExecutor
from bmlx_components.xdl_evaluator.launcher import XdlEvalLauncher


class XdlEvaluatorSpec(ComponentSpec):
    """XdlEvaluator component spec."""

    PARAMETERS = {
        "sampling_rate": ExecutionParameter(
            type=float, optional=True, description="样本采样率，抽样进行evaluate"
        ),
        "module": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="xdl evaluate使用的model文件",
        ),
        "model_file_pattern": ExecutionParameter(
            type=(list), optional=True, description="模型文件pattern，用于加载时候匹配模型"
        ),
        "model_uri_base": ExecutionParameter(
            type=(str, Text), optional=False, description="模型根目录"
        ),
        "enable_trace": ExecutionParameter(
            type=bool, optional=True, description="是否打开trace功能"
        ),
        "eval_slots": ExecutionParameter(
            type=bool, optional=True, description="是否eval slot"
        ),
        "specific_model": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="指定eval的模型文件，ceph路径默认解析路径下的model.pbtxt获取实际模型文件，hdfs路径直接作为模型文件",
        ),
        "specific_samples": ExecutionParameter(
            type=(list),
            optional=True,
            description="指定eval的样本文件，默认hdfs路径文件",
        ),
    }

    INPUTS = {
        "schema": ChannelParameter(
            type=standard_artifacts.Schema, description="样本的schema"
        ),
        "samples": ChannelParameter(
            type=standard_artifacts.Samples, optional=True, description="样本"
        ),
        "model": ChannelParameter(
            type=standard_artifacts.Model, optional=True, description="需要evaluate的模型"
        ),
    }

    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.ModelEval, description="evaluate的结果"
        ),
    }


class XdlEvaluator(Component):
    SPEC_CLASS = XdlEvaluatorSpec

    EXECUTOR_SPEC = ExecutorClassSpec(XdlEvaluatorExecutor)

    DRIVER_SPEC = DriverClassSpec(XdlEvaluatorDriver)

    def __init__(
        self,
        schema: Channel,
        samples: Optional[Channel] = None,
        model: Optional[Channel] = None,
        sampling_rate: float = 1.0,
        module: Optional[Text] = "",
        model_file_pattern: Optional[List[Text]] = [
            "phase0_emb/(.*)",
            "phase0_tf/(.*)",
        ],
        model_uri_base: Optional[Text] = "",
        namespace: Optional[Text] = "default",
        output: Optional[Text] = None,
        enable_trace: bool = False,
        eval_slots: bool = False,
        specific_model: Optional[Text] = "",
        specific_samples: Optional[List[Text]] = [],
        instance_name: Optional[Text] = None,
    ):
        if not samples and not specific_samples:
            raise ValueError("samples not provided")

        if not model and not specific_model:
            raise ValueError("model not provided")

        if not schema:
            raise ValueError("schema not provided")

        output = output or Channel(
            artifact_type=custom_artifacts.ModelEval,
            artifacts=[custom_artifacts.ModelEval()],
        )

        if not instance_name:
            instance_name = "xdl_eval"

        spec = XdlEvaluatorSpec(
            model=model,
            samples=samples,
            schema=schema,
            module=module,
            model_file_pattern=model_file_pattern,
            model_uri_base=model_uri_base,
            sampling_rate=sampling_rate,
            namespace=namespace,
            output=output,
            enable_trace=enable_trace,
            eval_slots=eval_slots,
            specific_model=specific_model,
            specific_samples=specific_samples,
        )
        super(XdlEvaluator, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return XdlEvalLauncher
