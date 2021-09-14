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
from bmlx_components.xdl_predictor.executor import XdlPredictorExecutor
from bmlx_components.xdl_predictor.driver import XdlPredictorDriver
from bmlx_components.xdl_predictor.launcher import XdlPredictorLauncher


class XdlPredictorSpec(ComponentSpec):
    """XdlPredictor component spec."""

    PARAMETERS = {
        "sampling_rate": ExecutionParameter(
            type=float, optional=False, description="样本采样率，抽样进行predict"
        ),
        "module": ExecutionParameter(
            type=(str, Text), optional=True, description="xdl predict使用的model文件"
        ),
        "model_file_pattern": ExecutionParameter(
            type=(list), optional=True, description="模型文件pattern，用于加载时候匹配"
        ),
        # 是否是进行分数一致性校验
        # 如果为True的话，则需要保证样本文件和最终的trace结果中的 item 顺序一致。
        # 此时bmlx 会设置xdl predict的 batch size = 1，且设置worker instance= 1
        "score_validation": ExecutionParameter(
            type=bool,
            optional=False,
            description="是否保证样本文件和最终的trace结果中的 item 顺序一致",
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
            type=standard_artifacts.Model, description="用于predict的模型"
        ),
    }

    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.PredictResult, description="predict结果"
        ),
    }


class XdlPredictor(Component):
    SPEC_CLASS = XdlPredictorSpec

    EXECUTOR_SPEC = ExecutorClassSpec(XdlPredictorExecutor)

    DRIVER_SPEC = DriverClassSpec(XdlPredictorDriver)

    def __init__(
        self,
        samples: Channel,
        schema: Channel,
        model: Channel,
        score_validation: bool = False,
        module: Optional[Text] = "",
        sampling_rate: float = 1.0,
        model_file_pattern: Optional[List[Text]] = [
            "phase0_emb/(.*)",
            "phase0_tf/(.*)",
        ],
        enable_trace: bool = True,
        instance_name: Optional[Text] = None,
    ):
        if not samples:
            raise ValueError("samples not provided")

        if not model:
            raise ValueError("model not provided")

        if not schema:
            raise ValueError("schema not provided")

        if not instance_name:
            instance_name = "xdl_predict"

        output = Channel(
            artifact_type=custom_artifacts.PredictResult,
            artifacts=[custom_artifacts.PredictResult()],
        )

        spec = XdlPredictorSpec(
            model=model,
            samples=samples,
            schema=schema,
            module=module,
            output=output,
            model_file_pattern=model_file_pattern,
            sampling_rate=sampling_rate,
            score_validation=score_validation,
            enable_trace=enable_trace,
        )
        super(XdlPredictor, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return XdlPredictorLauncher
