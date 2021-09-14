"""BMLX history model cleaner component definition."""
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
from bmlx.execution.driver import BaseDriver
from bmlx.metadata import standard_artifacts
from bmlx_components.model_cleaner.executor import CleanerExecutor
from bmlx.execution.launcher import Launcher

"""
删除规则：
60天以前：不保留
48h以前-60天：每天保留一个23点模型
48h内：全部保留
"""


class ModelCleanerSpec(ComponentSpec):
    """ModelCleanerSpec component spec."""

    PARAMETERS = {
        "model_uri_base": ExecutionParameter(
            type=(str, Text), optional=False, description="模型的根路径"
        ),
        # keep_none_before_days 天之前的模型都不保留
        "keep_none_before_days": ExecutionParameter(
            type=int, optional=False, description="最新一个版本,X天之前的模型不再保留"
        ),
        # keep_final_before_days 天之前 到keep_none_before_days 的模型，只保留每天的23点模型
        "keep_final_before_days": ExecutionParameter(
            type=int, optional=False, description="最新一个版本,X天之前的模型只保留每天23点的版本"
        ),
    }

    INPUTS = {}

    OUTPUTS = {}


class ModelCleaner(Component):
    SPEC_CLASS = ModelCleanerSpec

    EXECUTOR_SPEC = ExecutorClassSpec(CleanerExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        instance_name,
        model_uri_base: Text,
        keep_none_before_days: int = 60,
        keep_final_before_days: int = 2,
    ):
        if not model_uri_base:
            raise ValueError("model_uri_base not provided")

        if not instance_name:
            instance_name = "history_model_cleaner"

        spec = ModelCleanerSpec(
            model_uri_base=model_uri_base,
            keep_none_before_days=keep_none_before_days,
            keep_final_before_days=keep_final_before_days,
        )

        super(ModelCleaner, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher
