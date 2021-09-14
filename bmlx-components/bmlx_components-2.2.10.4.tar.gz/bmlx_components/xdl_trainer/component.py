"""BMLX Trainer component definition."""
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
from bmlx_components.xdl_trainer.executor import XdlTrainerExecutor
from bmlx_components.xdl_trainer.launcher import XdlTrainerLauncher
from bmlx_components.xdl_trainer.driver import XdlTrainerDriver


class XdlTrainerSpec(ComponentSpec):
    """Trainer component spec."""

    PARAMETERS = {
        "model_name": ExecutionParameter(
            type=str, optional=True, description="模型名"
        ),
        "sampling_rate": ExecutionParameter(
            type=float,
            optional=True,
            description="样本抽样率，默认为1.0。设置小于1的数可以用于快速测试",
        ),
        "module": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="定义模型的python 类，比如 model.SparseDnnModel （表示在pipeline目录下的model.py 文件中的  SparseDnnModel 类）",
        ),
        "model_uri_base": ExecutionParameter(
            type=(str, Text), optional=True, description="模型存储的基础路径"
        ),
        "model_file_pattern": ExecutionParameter(
            type=(list), optional=True, description="模型文件通配符（用于加载模型时候指定加载某些文件）"
        ),
        "warmup_model_bank": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="warmup 模型，用于训练一个新模型时候加载其他的模型作为基础模型。比如： 带有自动统计特征模型中， warmup_model_bank 可设置为单独统计的自动统计特征的数据。",
        ),
        "enable_trace": ExecutionParameter(
            type=bool, optional=True, description="打开trace功能"
        ),
    }

    INPUTS = {
        "schema": ChannelParameter(
            type=standard_artifacts.Schema, description="样本schema"
        ),
        "samples": ChannelParameter(
            type=standard_artifacts.Samples, description="样本元数据"
        ),
        "previous_model": ChannelParameter(
            type=standard_artifacts.Model, optional=True, description="前置模型"
        ),
    }

    OUTPUTS = {
        "output": ChannelParameter(
            type=standard_artifacts.Model, description="模型输出路径"
        ),
    }


class XdlTrainer(Component):
    """
    向XDL集群提交任务; 此版本trainer直接提交k8s任务，轮询直到Completed状态位置
    """

    SPEC_CLASS = XdlTrainerSpec

    EXECUTOR_SPEC = ExecutorClassSpec(XdlTrainerExecutor)

    DRIVER_SPEC = DriverClassSpec(XdlTrainerDriver)

    def __init__(
        self,
        samples: Channel,
        schema: Channel,
        model_uri_base: Text,
        model_name: Text,
        previous_model: Optional[Channel] = None,
        model_file_pattern: Optional[List[Text]] = [
            "phase0_emb/(.*)",
            "phase0_tf/(.*)",
        ],
        warmup_model_bank: Optional[Text] = None,
        sampling_rate: float = 1.0,
        module: Optional[Text] = "",
        output: Optional[Channel] = None,
        enable_trace: bool = False,
        instance_name: Optional[Text] = None,
    ):
        if not model_uri_base:
            raise ValueError("model_uri_base does not set")

        if not model_name:
            raise ValueError("model_name not provided")

        if not samples:
            raise ValueError("samples not provided")

        if not isinstance(model_file_pattern, list):
            raise ValueError("previous model pattern must be list of str")

        output = output or Channel(
            artifact_type=standard_artifacts.Model,
            # 注意！！！ 这里的 name 填充为model_name，用于显示在模型中心上
            artifacts=[standard_artifacts.Model(name=model_name)],
        )

        if not instance_name:
            instance_name = "xdl_train"

        spec = XdlTrainerSpec(
            samples=samples,
            schema=schema,
            sampling_rate=sampling_rate,
            previous_model=previous_model,
            model_uri_base=model_uri_base,
            module=module,
            output=output,
            model_file_pattern=model_file_pattern,
            warmup_model_bank=warmup_model_bank,
            enable_trace=enable_trace,
            model_name=model_name,
        )

        super(XdlTrainer, self).__init__(spec=spec, instance_name=instance_name)

    def get_launcher_class(self, ctx):
        return XdlTrainerLauncher
