from bmlx_components.xdl_base.driver import XdlDriver
from bmlx.execution.execution import ExecutionInfo
from bmlx.flow import Channel, Pipeline, DriverArgs, Component
from typing import Text, Any, Dict


class XdlConverterDriver(XdlDriver):
    # override super method
    def _rewrite_launch_config(self, exec_properties):
        pass

    def _resolve_model_paths(self, input_dict, exec_properties):
        return "", ""