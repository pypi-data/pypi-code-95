"""BMLX XdlPredictor component definition."""
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

from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts
from bmlx_components.xdl_predict_emb.executor import XdlPredictEmbExecutor
from bmlx_components.xdl_predict_emb.driver import XdlPredictEmbDriver
from bmlx_components.xdl_predict_emb.launcher import XdlPredictEmbLauncher


class XdlPredictEmbSpec(ComponentSpec):
    """XdlPredictor component spec."""

    PARAMETERS = {
        "sampling_rate": ExecutionParameter(
            type=float, optional=False, description="样本采样率，抽样进行predict"
        ),
        "module": ExecutionParameter(
            type=(str, Text), optional=True, description="xdl predict使用的model文件"
        ),
        "model_uri_base": ExecutionParameter(
            type=(str, Text), optional=True, description="模型存储的基础路径"
        ),
        "model_file_pattern": ExecutionParameter(
            type=(list), optional=True, description="模型文件pattern，用于加载时候匹配"
        ),
        "warmup_model_bank": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="warmup 模型，用于训练一个新模型时候加载其他的模型作为基础模型。比如： 带有自动统计特征模型中， warmup_model_bank 可设置为单独统计的自动统计特征的数据。",
        ),
        "enable_trace": ExecutionParameter(
            type=bool, optional=True, description="是否打开trace功能"
        ),
    }

    INPUTS = {
        "schema": ChannelParameter(
            type=standard_artifacts.Schema, description="样本schema"
        ),
        "samples": ChannelParameter(
            type=standard_artifacts.Samples, description="样本"
        ),
        "model": ChannelParameter(
            type=standard_artifacts.Model, description="用于predict_embedd的模型"
        ),
    }

    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.PredictResult, description="predict结果"
        ),
    }


class XdlPredictEmb(Component):
    SPEC_CLASS = XdlPredictEmbSpec

    EXECUTOR_SPEC = ExecutorClassSpec(XdlPredictEmbExecutor)

    DRIVER_SPEC = DriverClassSpec(XdlPredictEmbDriver)

    def __init__(
        self,
        samples: Channel,
        schema: Channel,
        model: Channel,
        model_uri_base: Text,
        module: Optional[Text] = "",
        sampling_rate: float = 1.0,
        model_file_pattern: Optional[List[Text]] = [
            "phase0_emb/(.*)",
            "phase0_tf/(.*)",
        ],
        warmup_model_bank: Optional[Text] = None,
        enable_trace: bool = True,
        instance_name: Optional[Text] = None,
    ):
        if not model_uri_base:
            raise ValueError("model_uri_base does not set")

        if not samples:
            raise ValueError("samples not provided")

        if not model:
            raise ValueError("model not provided")

        if not schema:
            raise ValueError("schema not provided")

        if not instance_name:
            instance_name = "xdl_predict_emb"

        output = Channel(
            artifact_type=custom_artifacts.PredictResult,
            artifacts=[custom_artifacts.PredictResult()],
        )

        spec = XdlPredictEmbSpec(
            model=model,
            samples=samples,
            schema=schema,
            module=module,
            output=output,
            model_uri_base=model_uri_base,
            warmup_model_bank=warmup_model_bank,
            model_file_pattern=model_file_pattern,
            sampling_rate=sampling_rate,
            enable_trace=enable_trace,
        )
        super(XdlPredictEmb, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return XdlPredictEmbLauncher

