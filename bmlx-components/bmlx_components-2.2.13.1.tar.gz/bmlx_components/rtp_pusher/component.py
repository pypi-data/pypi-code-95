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
from bmlx_components.rtp_pusher.executor import PusherExecutor
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
        "disable_skip_execution": ExecutionParameter(
            type=bool,
            optional=True,
            description="是否禁止掉 skip 该组件的操作，如果是，则该组件在pipeline中总是会执行",
        ),
        "target": ExecutionParameter(
            type=list,
            optional=True,
            description="发布地区—— sg(只发新加坡，默认)/eu(只发欧洲)/sg,eu(同时发新加坡和欧洲)",
        ),
        "local_emb": ExecutionParameter(
            type=bool,
            optional=True,
            description="是否发布为本地模型，需要和xdl_convert中保持一致",
        ),
        "cyclone_test": ExecutionParameter(
            type=bool,
            optional=True,
            description="发布到香港测试cyclone,测试模型使用",
        ),
        "validate_accuracy": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="事前校验的精度"
        ),
        "validate_rate": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="事前校验通过的最低一致率"
        ),
        "cyclone_wait_timeout": ExecutionParameter(
            type=int,
            optional=True,
            description="等待cyclone发布完成的超时时限(s)"
        ),
    }

    INPUTS = {
        "converted_model": ChannelParameter(
            type=custom_artifacts.ConvertedModel, description="转换之后的模型"
        ),
        "validation_samples": ChannelParameter(
            type=custom_artifacts.CheckSample,
            optional=True,
            description="事前校验样本"
        )
    }
    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.PushedModel, description="发布之后的模型"
        )
    }


class RtpPusher(Component):
    SPEC_CLASS = PusherSpec

    EXECUTOR_SPEC = ExecutorClassSpec(PusherExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        converted_model: Channel,
        model_name: Text,
        validation_samples: Optional[Channel] = None,
        namespace: Optional[Text] = "default",
        disable_skip_execution: bool = False,
        target: list = ["sg"],
        local_emb: bool = False,
        cyclone_test: bool = False,
        validate_accuracy: Text = "5",
        validate_rate: Text = "99",
        cyclone_wait_timeout: int = 3600,
        instance_name: Optional[Text] = None,
    ):
        if not namespace:
            raise ValueError(
                "Empty namespace, ceto need a namespace to publish model"
            )
        if not converted_model:
            raise ValueError("Empty pushed model")
        if not model_name:
            raise ValueError("Empty model name")
        for i in target:
            if i not in {"eu", "sg"}:
                raise ValueError("target not in [\"eu\",\"sg\"]")
        assert validate_accuracy.isnumeric()
        assert (isinstance(eval(validate_rate), float)
            or isinstance(eval(validate_rate), int))

        output = Channel(
            artifact_type=custom_artifacts.PushedModel,
            # 注意！！！ 这里的 name 填充为model_name，用于显示在模型中心上
            artifacts=[custom_artifacts.PushedModel(name=model_name)],
        )

        spec = PusherSpec(
            converted_model=converted_model,
            model_name=model_name,
            validation_samples=validation_samples,
            namespace=namespace,
            disable_skip_execution=disable_skip_execution,
            target=target,
            local_emb=local_emb,
            cyclone_test=cyclone_test,
            validate_accuracy=validate_accuracy,
            validate_rate=validate_rate,
            cyclone_wait_timeout=cyclone_wait_timeout,
            output=output,
        )

        super(RtpPusher, self).__init__(spec=spec, instance_name=instance_name)

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
