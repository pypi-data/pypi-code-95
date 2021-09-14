from typing import Text, Optional, List
from bmlx.flow import (
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
    Channel,
    Executor,
)
from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts
from bmlx.execution.launcher import Launcher
from bmlx_components.validate_sample_importer.driver import (
    ValidateSampleImporterDriver,
)

"""
从外部引入小样本验证需要的数据, validate_samples & validate_origin_samples
"""


class ValidateSampleImporterSpec(ComponentSpec):
    """ component spec """

    PARAMETERS = {
        "validate_origin_samples_uri": ExecutionParameter(
            type=str, optional=False, description="模型小样本校验使用的原始样本路径"
        ),
        "validate_samples_uri": ExecutionParameter(
            type=str, optional=False, description="模型小样本校验使用的预处理后样本路径"
        ),
    }

    INPUTS = {}

    OUTPUTS = {
        "validate_samples": ChannelParameter(
            type=standard_artifacts.Samples, description="模型小样本校验使用的原始样本"
        ),
        "validate_origin_samples": ChannelParameter(
            type=custom_artifacts.OriginSamples, description="模型小样本校验使用的预处理后样本"
        ),
    }


class ValidateSampleImporter(Component):
    SPEC_CLASS = ValidateSampleImporterSpec
    EXECUTOR_SPEC = ExecutorClassSpec(Executor)
    DRIVER_SPEC = DriverClassSpec(ValidateSampleImporterDriver)

    def __init__(
        self,
        validate_origin_samples_uri: Text,
        validate_samples_uri: Text,
        instance_name: Optional[Text] = None,
    ):
        if not validate_origin_samples_uri:
            raise ValueError("empty validate_origin_samples_uri")
        if not validate_samples_uri:
            raise ValueError("empty validate_samples_uri")
        if not instance_name:
            instance_name = "validate_sample_importer"

        spec = ValidateSampleImporterSpec(
            validate_origin_samples_uri=validate_origin_samples_uri,
            validate_samples_uri=validate_samples_uri,
            validate_origin_samples=Channel(
                artifact_type=custom_artifacts.OriginSamples,
                artifacts=[custom_artifacts.OriginSamples()],
            ),
            validate_samples=Channel(
                artifact_type=standard_artifacts.Samples,
                artifacts=[standard_artifacts.Samples()],
            ),
        )

        super(ValidateSampleImporter, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher
