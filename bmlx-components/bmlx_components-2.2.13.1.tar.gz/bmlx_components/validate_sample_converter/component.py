from typing import Text, Optional, List
from bmlx.flow import (
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
    Channel,
)
from bmlx.execution.driver import BaseDriver
from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts
from bmlx.execution.launcher import Launcher
from bmlx_components.validate_sample_converter.executor import ConverterExecutor

"""
生成rtp预估平台格式的小样本对分数据

输入：
    validate_origin_sample
    validate_sample
    predict_trace

输出：
    original_samples
    model_samples
    sample_scores
"""

class SampleConverterSpec(ComponentSpec):
    """validate sample converter"""
    PARAMETERS = {}

    INPUTS = {
        "validate_origin_sample": ChannelParameter(
            type=custom_artifacts.OriginSamples,
            description="小样本对分原始样本"
        ),
        "validate_sample": ChannelParameter(
            type=standard_artifacts.Samples,
            description="小样本对分预处理后样本"
        ),
        "predict_trace": ChannelParameter(
            type=custom_artifacts.PredictResult,
            description="小样本对分打分结果"
        )
    }

    OUTPUTS = {
        "converted_samples": ChannelParameter(
            type=custom_artifacts.CheckSample,
            description="转换后校验数据"
        )
    }

class SampleConverter(Component):
    SPEC_CLASS = SampleConverterSpec
    EXECUTOR_SPEC = ExecutorClassSpec(ConverterExecutor)
    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        validate_origin_sample: Channel,
        validate_sample: Channel,
        predict_trace: Channel,
        instance_name: Optional[Text] = None,
    ):
        if not validate_origin_sample:
            raise RuntimeError("validate_origin_sample not provided")

        if not validate_sample:
            raise RuntimeError("validate_sample not provided")

        if not predict_trace:
            raise RuntimeError("predict_trace not provided")

        converted_samples = Channel(
            artifact_type=custom_artifacts.CheckSample,
            artifacts=[custom_artifacts.CheckSample()]
        )

        if not instance_name:
            instance_name = "sample_converter"

        spec = SampleConverterSpec(
            validate_origin_sample=validate_origin_sample,
            validate_sample=validate_sample,
            predict_trace=predict_trace,
            converted_samples=converted_samples,
            instance_name=instance_name,
        )

        super(SampleConverter, self).__init__(spec=spec, instance_name=instance_name)

    def get_launcher_class(self, ctx):
        return Launcher