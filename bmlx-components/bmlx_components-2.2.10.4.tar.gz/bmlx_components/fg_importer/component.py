"""
从外部引入fg 相关的artifact，比如 fg conf， fg python so，fg cpp so
"""

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
from bmlx_components import custom_artifacts
from bmlx.execution.launcher import Launcher
from bmlx_components.fg_importer.driver import FgImporterDriver
from bmlx_components.fg_importer.executor import FgImporterExecutor


class FgImporterSpec(ComponentSpec):
    """ component spec """

    PARAMETERS = {
        # 如果指定 fg_dir， 则强制使用 fg_dir 中 VERSION 文件指定的 fg yml 和 fg so
        "fg_dir": ExecutionParameter(
            type=str, optional=True, description="fg 的所有文件存放的目录"
        ),
        "fg_conf_path": ExecutionParameter(
            type=str, optional=True, description="fg conf 文件存放的目录"
        ),
        "fg_cpp_lib_path": ExecutionParameter(
            type=str, optional=True, description="fg cpp so 文件(用于rtp发布)存放的目录"
        ),
        "fg_py_lib_path": ExecutionParameter(
            type=str, optional=True, description="fg python so 文件(用于离线校验)存放的目录"
        ),
    }

    INPUTS = {
        "fg_conf_input": ChannelParameter(
            type=custom_artifacts.FgConf, optional=True, description="由model_selector获取fg.yaml"
        ),
    }

    OUTPUTS = {
        "fg_conf": ChannelParameter(
            type=custom_artifacts.FgConf, description="fg配置文件"
        ),
        "fg_cpp_lib": ChannelParameter(
            type=custom_artifacts.FgCppLib, description="fg cpp so文件"
        ),
        "fg_py_lib": ChannelParameter(
            type=custom_artifacts.FgPyLib, description="fg python so文件"
        ),
    }


class FgImporter(Component):
    SPEC_CLASS = FgImporterSpec
    EXECUTOR_SPEC = ExecutorClassSpec(FgImporterExecutor)
    DRIVER_SPEC = DriverClassSpec(FgImporterDriver)

    def __init__(
        self,
        fg_conf_input: Optional[Channel] = None,
        fg_dir: Optional[Text] = None,
        fg_conf_path: Optional[Text] = None,
        fg_cpp_lib_path: Optional[Text] = None,
        fg_py_lib_path: Optional[Text] = None,
        instance_name: Optional[Text] = None,
    ):
        fg_conf = Channel(
            artifact_type=custom_artifacts.FgConf,
            artifacts=[custom_artifacts.FgConf()],
        )
        fg_cpp_lib = Channel(
            artifact_type=custom_artifacts.FgCppLib,
            artifacts=[custom_artifacts.FgCppLib()],
        )
        fg_py_lib = Channel(
            artifact_type=custom_artifacts.FgPyLib,
            artifacts=[custom_artifacts.FgPyLib()],
        )
        spec = FgImporterSpec(
            fg_dir=fg_dir,
            fg_conf_path=fg_conf_path,
            fg_cpp_lib_path=fg_cpp_lib_path,
            fg_py_lib_path=fg_py_lib_path,
            fg_conf_input=fg_conf_input,
            fg_conf=fg_conf,
            fg_cpp_lib=fg_cpp_lib,
            fg_py_lib=fg_py_lib,
        )
        if not instance_name:
            instance_name = "fg_importer"

        super(FgImporter, self).__init__(spec=spec, instance_name=instance_name)

    def get_launcher_class(self, ctx):
        return Launcher
