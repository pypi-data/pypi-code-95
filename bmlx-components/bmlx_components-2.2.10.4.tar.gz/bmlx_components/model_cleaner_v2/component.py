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
from bmlx_components.model_cleaner_v2.executor import CleanerExecutor
from bmlx.execution.launcher import Launcher


class ModelCleanerSpec(ComponentSpec):
    """ModelCleanerSpec component spec."""

    PARAMETERS = {
        "model_uri_base": ExecutionParameter(
            type=(str, Text), optional=False, description="模型的根路径"
        ),
        "model_keep_max_versions": ExecutionParameter(
            type=int, optional=False, description="最多保留的版本数目"
        ),
    }

    INPUTS = {}

    OUTPUTS = {}


class ModelCleanerV2(Component):
    SPEC_CLASS = ModelCleanerSpec

    EXECUTOR_SPEC = ExecutorClassSpec(CleanerExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        instance_name,
        model_uri_base: Text,
        model_keep_max_versions: int = 3,
    ):
        if not model_uri_base:
            raise ValueError("model_uri_base not provided")

        if not model_keep_max_versions:
            raise ValueError("model_keep_max_versions not provided")

        if not instance_name:
            instance_name = "history_model_cleaner"

        spec = ModelCleanerSpec(
            model_uri_base=model_uri_base,
            model_keep_max_versions=model_keep_max_versions,
        )

        super(ModelCleanerV2, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher
