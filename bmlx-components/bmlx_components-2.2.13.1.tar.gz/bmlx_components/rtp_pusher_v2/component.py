"""
rtp_pusher 将embedding 数据发布到分布式cyclone服务器；rtp_pusher_v2 build 单机版本的embedding并发布到每台rtp 服务器
rtp_pusher_v2 适合小规模的模型发布使用
"""

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
from typing import Text, Optional, List
from bmlx_components.rtp_pusher_v2.executor import PusherExecutor
from bmlx.execution.launcher import Launcher


class PusherSpec(ComponentSpec):
    """ Pusher spec """

    PARAMETERS = {
        "model_name": ExecutionParameter(
            type=(str, Text), optional=False, description="模型名称"
        ),
        "namespace": ExecutionParameter(
            type=(str, Text), optional=False, description="ceto上的namespace"
        ),
        "embedding_build_tool_dir": ExecutionParameter(
            type=str, optional=True, description="模型build工具路径"
        ),
    }

    INPUTS = {
        "converted_model": ChannelParameter(
            type=custom_artifacts.ConvertedModel, description="转换之后的模型"
        )
    }
    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.PushedModel, description="发布后的模型"
        )
    }


class RtpPusherV2(Component):
    SPEC_CLASS = PusherSpec

    EXECUTOR_SPEC = ExecutorClassSpec(PusherExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        converted_model: Channel,
        model_name: Text,
        namespace: Text,
        embedding_build_tool_dir: Text,
        instance_name: Optional[Text] = None,
    ):
        if not namespace:
            raise ValueError("Empty namespace")
        if not converted_model:
            raise ValueError("Empty pushed model")
        if not model_name:
            raise ValueError("Empty model name")
        if not embedding_build_tool_dir:
            raise ValueError("Empty embedding_build_tool_dir")

        output = Channel(
            artifact_type=custom_artifacts.PushedModel,
            # 注意！！！ 这里的 name 填充为model_name，用于显示在模型中心上
            artifacts=[custom_artifacts.PushedModel(name=model_name)],
        )
        spec = PusherSpec(
            converted_model=converted_model,
            model_name=model_name,
            namespace=namespace,
            embedding_build_tool_dir=embedding_build_tool_dir,
            output=output,
        )

        super(RtpPusherV2, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher
