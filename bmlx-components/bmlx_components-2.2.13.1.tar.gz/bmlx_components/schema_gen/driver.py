import logging

import os

from typing import Dict, Text, Any, Optional
from bmlx.flow import DriverArgs, Channel, Pipeline, Component, Artifact
from bmlx.metadata.metadata import Metadata
from bmlx.utils import io_utils
from bmlx.execution.execution import ExecutionInfo
from bmlx.execution.driver import BaseDriver


class SchemaGenDriver(BaseDriver):
    def __init__(self, metadata: Metadata):
        self._metadata = metadata

    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ) -> ExecutionInfo:
        input_artifacts = self.resolve_input_artifacts(
            input_dict, component, driver_args
        )

        # schema 都存放在特定目录，根据 checksum 来索引
        schema_storage_base_path = os.path.join(
            driver_args.artifact_storage_base, "schemas"
        )
        output_artifacts = {}
        for name, channel in output_dict.items():
            output_artifacts[name] = []

            for artifact in channel.get():
                logging.info(
                    "schema_gen driver, allocate schema storage at: %s",
                    driver_args.artifact_storage_base,
                )
                if not io_utils.exists(schema_storage_base_path):
                    io_utils.mkdirs(schema_storage_base_path)
                artifact.meta.uri = schema_storage_base_path
                output_artifacts[name].append(artifact)

        return ExecutionInfo(
            input_dict=input_artifacts,
            output_dict=output_artifacts,
            exec_properties=exec_properties,
        )
