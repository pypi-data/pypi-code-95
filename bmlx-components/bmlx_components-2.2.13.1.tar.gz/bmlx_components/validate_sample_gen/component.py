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
from bmlx_components.validate_sample_gen.executor import SampleGenExecutor

"""
从原始数据example (original feature), 特征预处理得到 sample

执行逻辑：
1. 从kafka 上获取最新的 origin featurelog
2. 根据pushed_model 信息进行过滤，只保留需要进行一致性校验的 origin featurelog
3. 根据fg-importer 得到的 fg 信息，去获取 fg python lib; 根据 模型的发布目录，去获取模型转换后的yaml (其实也可以直接根据 fg-importer 去获取全集的yml)
4. 将origin featurelog 进行预处理，得到samples
5. 保存步骤2 产生的 origin sample 和 步骤4 产生的sample

NOTE:
由于目前这个component 只是用于一致性校验，一致性校验需要的sample数量很小. 所以直接
从 kafka 拉取original feature log，然后利用 fg.so 处理

如果需要处理大量数据，需要改造成提交到spark上执行
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
        "model_name_location": ExecutionParameter(
            type=str, optional=True, description="样本中记录使用的模型名称的位置"
        ),
        "model_version_location": ExecutionParameter(
            type=str, optional=True, description="样本中记录使用的模型版本的位置"
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
        "fg_conf_input": ChannelParameter(
            type=custom_artifacts.FgConf, description="预处理使用的yaml"
        ),
        "fg_py_lib": ChannelParameter(
            type=custom_artifacts.FgPyLib, description="预处理使用的python so"
        ),
        "pushed_model": ChannelParameter(
            type=custom_artifacts.PushedModel, description="需要校验的模型"
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


class SampleGen(Component):
    SPEC_CLASS = SampleGenSpec
    EXECUTOR_SPEC = ExecutorClassSpec(SampleGenExecutor)
    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        pushed_model: Channel,
        fg_conf_input: Channel,
        fg_py_lib: Channel,
        kafka_topic: Text,
        kafka_brokers: Text,
        output_sample_limit: int = 200,
        model_name_location: Text = "flow_info.feature[\"rank_info.model_name\"].bytes",
        model_version_location: Text = "flow_info.feature[\"rank_info.model_version\"].int32",
        product_name: Text = "bmlx_validate",
        source: Text = "bmlx_validate",
        fg_conf_path: Optional[Text] = None,
        instance_name: Optional[Text] = None,
    ):
        if not pushed_model:
            raise ValueError("pushed model does not provided")

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
            pushed_model=pushed_model,
            fg_conf_input=fg_conf_input,
            fg_py_lib=fg_py_lib,
            kafka_topic=kafka_topic,
            kafka_brokers=kafka_brokers,
            model_name_location=model_name_location,
            model_version_location=model_version_location,
            product_name=product_name,
            source=source,
            fg_conf_path=fg_conf_path,
            samples=samples,
            origin_samples=origin_samples,
            output_sample_limit=output_sample_limit,
        )

        super(SampleGen, self).__init__(spec=spec, instance_name=instance_name)

    def get_launcher_class(self, ctx):
        return Launcher
