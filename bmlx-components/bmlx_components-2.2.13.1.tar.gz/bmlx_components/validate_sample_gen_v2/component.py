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
from bmlx_components.validate_sample_gen_v2.executor import SampleGenExecutor

"""
从原始数据example (original feature), 特征预处理得到 sample
v2版本是获取事前校验用的小样本

执行逻辑：
1. 从kafka 上获取最新的 origin featurelog, 得到origin sample
2. 根据fg-importer 得到的 fg 信息，去获取 fg python lib; 根据 模型的发布目录，去获取模型转换后的yaml (其实也可以直接根据 fg-importer 去获取全集的yml)
3. 将origin featurelog 进行预处理，得到samples
4. 保存步骤1 产生的 origin sample 和 步骤3 产生的sample
"""


class SampleGenSpec(ComponentSpec):
    """ sample gen spec """

    PARAMETERS = {
        "output_sample_limit": ExecutionParameter(
            type=int, optional=True, description="最多产生多少条样本"
        ),
        "kafka_topic": ExecutionParameter(
            type=str, optional=False, description="读取原始样本使用的kafka topic"
        ),
        "kafka_brokers": ExecutionParameter(
            type=str, optional=False, description="读取原始样本使用的kafka broker"
        ),
        "fg_conf_path": ExecutionParameter(
            type=str, optional=True, description="手动指定预处理yaml"
        ),
        "product_name": ExecutionParameter(
            type=str, optional=True, description="业务线名称, process featurelog时需要"
        ),
        "source": ExecutionParameter(
            type=str, optional=True, description="fg请求来源，process featurelog时需要"
        ),
    }

    INPUTS = {
        "converted_model": ChannelParameter(
            type=custom_artifacts.ConvertedModel, description="从中解析经过convert的fg_path"
        ),
        "fg_py_lib": ChannelParameter(
            type=custom_artifacts.FgPyLib, description="预处理使用的python so"
        ),
    }

    OUTPUTS = {
        "origin_samples": ChannelParameter(
            type=custom_artifacts.OriginSamples, description="产生的原始样本"
        ),
        "samples": ChannelParameter(
            type=standard_artifacts.Samples, description="产生的预处理后的样本"
        ),
    }


class SampleGenV2(Component):
    SPEC_CLASS = SampleGenSpec
    EXECUTOR_SPEC = ExecutorClassSpec(SampleGenExecutor)
    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        converted_model: Channel,
        fg_py_lib: Channel,
        kafka_topic: Text,
        kafka_brokers: Text,
        output_sample_limit: int = 200,
        product_name: Text = "bmlx_validate",
        source: Text = "bmlx_validate",
        fg_conf_path: Optional[Text] = None,
        instance_name: Optional[Text] = None,
    ):
        if not fg_py_lib:
            raise ValueError("fg_py_lib does not provided")

        # 最多200条，减少读kafka产生的压力
        assert output_sample_limit <= 200

        samples = Channel(
            artifact_type=standard_artifacts.Samples,
            artifacts=[standard_artifacts.Samples()],
        )
        origin_samples = Channel(
            artifact_type=custom_artifacts.OriginSamples,
            artifacts=[custom_artifacts.OriginSamples()],
        )
        spec = SampleGenSpec(
            converted_model=converted_model,
            fg_py_lib=fg_py_lib,
            kafka_topic=kafka_topic,
            kafka_brokers=kafka_brokers,
            product_name=product_name,
            source=source,
            fg_conf_path=fg_conf_path,
            samples=samples,
            origin_samples=origin_samples,
            output_sample_limit=output_sample_limit,
        )

        super(SampleGenV2, self).__init__(spec=spec, instance_name=instance_name)

    def get_launcher_class(self, ctx):
        return Launcher
