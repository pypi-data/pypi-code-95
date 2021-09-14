"""
相比于 xdl_pusher， 去掉了检查并发布 fg.yml的功能， 适配RTP
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
from bmlx_components.rtp_pusher_eu.executor import PusherExecutor
from bmlx.execution.launcher import Launcher


class PusherSpec(ComponentSpec):
    """ Pusher spec """

    PARAMETERS = {
        "model_name": ExecutionParameter(
            type=(str, Text), optional=False, description="模型名称"
        ),
        "namespace": ExecutionParameter(
            type=(str, Text),
            optional=False,
            description="ceto 上模型发布到的namespace",
        ),
        "local_emb": ExecutionParameter(
            type=bool,
            optional=False,
            description="用来检查是否生成的本地模型，即该值必须为True"
        ),
        "disable_skip_execution": ExecutionParameter(
            type=bool,
            optional=True,
            description="是否禁止掉 skip 该组件的操作，如果是，则该组件在pipeline中总是会执行",
        ),
    }

    INPUTS = {
        "converted_model": ChannelParameter(
            type=custom_artifacts.ConvertedModel, description="转换之后的模型"
        ),
    }
    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.PushedModel, description="发布之后的模型"
        )
    }


class RtpPusherEU(Component):
    SPEC_CLASS = PusherSpec

    EXECUTOR_SPEC = ExecutorClassSpec(PusherExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        converted_model: Channel,
        model_name: Text,
        local_emb: bool,
        namespace: Optional[Text] = "default",
        disable_skip_execution: bool = False,
        instance_name: Optional[Text] = None,
    ):
        if not namespace:
            raise ValueError(
                "Empty namespace, ceto need a namespace to publish model"
            )
        if not converted_model:
            raise ValueError("Empty pushed model")
        if not local_emb:
            raise ValueError("local_emb should be True")
        if not model_name:
            raise ValueError("Empty model name")

        output = Channel(
            artifact_type=custom_artifacts.PushedModel,
            # 注意！！！ 这里的 name 填充为model_name，用于显示在模型中心上
            artifacts=[custom_artifacts.PushedModel(name=model_name)],
        )

        spec = PusherSpec(
            converted_model=converted_model,
            model_name=model_name,
            local_emb=local_emb,
            namespace=namespace,
            disable_skip_execution=disable_skip_execution,
            output=output,
        )

        super(RtpPusherEU, self).__init__(spec=spec, instance_name=instance_name)

    def get_launcher_class(self, ctx):
        return Launcher

    def skip_execution(self, pipeline_execution, exec_properties) -> bool:
        if (
            not exec_properties["disable_skip_execution"]
            and not pipeline_execution.deployment_running
        ):
            return True
        else:
            return False
