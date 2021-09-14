# -*- coding: UTF-8 -*-
from bmlx.flow import (
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
    Channel,
    Executor,
    Artifact
)
from bmlx_components import custom_artifacts
from typing import Text, Dict, List, Any
from bmlx.execution.driver import BaseDriver
from bmlx.execution.launcher import Launcher
import logging
from bmlx_components.origin_sample_selector.executor import OriginSampleSelectorExecutor


class OriginSampleSelectorSpec(ComponentSpec):
    PARAMETERS = {
        "candidate_uri_base": ExecutionParameter(
            type=(str, Text),
            description="fg数据输入路径base",
            optional=False
        ),

        "candidate_time_range": ExecutionParameter(
            type=(str, Text),
            description="fg数据输入路径扫描时间范围，"
                        "起始和结束时间（day/hours）,[start_time-end_time],"
                        "为空字符或start和end均为空时，使用trace_back_length",
            optional=True
        ),

        "trace_back_length": ExecutionParameter(
            type=(str, Text),
            description="格式为day/hours ^[0-9]*[hdHD]{1}$，"
                        "用于指定从当前时间往前扫描路径范围",
            optional=False
        ),

        "output_uri_base": ExecutionParameter(
            type=(str, Text),
            description="fg输出结果路径，根据时间格式设置："
                        "文件格式为YYYYMMDD/HH 或 YYYYMMDD",
            optional=False
        ),

        "max_wait_minutes": ExecutionParameter(
            type=(str, Text),
            description="max wait time to find ready uri before exit",
            optional=False
        ),

        "min_selected_ready_uris": ExecutionParameter(
            type=(str, Text),
            description="min count of selected ready uris",
            optional=False
        ),

        "max_selected_ready_uris": ExecutionParameter(
            type=(str, Text),
            description="max count of selected ready uris",
            optional=False
        ),

    }

    INPUTS = {}

    OUTPUTS = {
        "ready_uris": ChannelParameter(type=custom_artifacts.OriginSamples,
                                       description="selected ready uris"),
    }


class OriginSampleSelector(Component):
    SPEC_CLASS = OriginSampleSelectorSpec

    EXECUTOR_SPEC = ExecutorClassSpec(OriginSampleSelectorExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
            self,
            instance_name,
            candidate_uri_base="",
            candidate_time_range="",
            trace_back_length="",
            output_uri_base="",
            max_wait_minutes=1,
            min_selected_ready_uris=1,
            max_selected_ready_uris=1
    ):
        ready_uris = Channel(
            artifact_type=custom_artifacts.OriginSamples,
            artifacts=[custom_artifacts.OriginSamples()],
        )
        spec = OriginSampleSelectorSpec(
            candidate_uri_base=candidate_uri_base,
            candidate_time_range=candidate_time_range,
            trace_back_length=trace_back_length,
            output_uri_base=output_uri_base,
            max_wait_minutes=max_wait_minutes,
            min_selected_ready_uris=min_selected_ready_uris,
            max_selected_ready_uris=max_selected_ready_uris,
            ready_uris=ready_uris,
        )
        super(OriginSampleSelector, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher