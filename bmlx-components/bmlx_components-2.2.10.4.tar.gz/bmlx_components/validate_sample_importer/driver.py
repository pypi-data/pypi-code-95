import logging
import sys

from bmlx.execution.driver import BaseDriver
from bmlx.execution.driver import ExecutionInfo
from typing import Dict, Text, Any, List, Optional
from bmlx.flow import Channel, Pipeline, Component, Artifact, DriverArgs
from bmlx.utils import channel_utils, import_utils, io_utils
from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts


class ValidateSampleImporterDriver(BaseDriver):
    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ):

        validate_samples_uri = exec_properties["validate_samples_uri"]
        validate_origin_samples_uri = exec_properties[
            "validate_origin_samples_uri"
        ]
        logging.info("imported validate_samples %s" % validate_samples_uri)
        logging.info(
            "imported validate_origin_samples %s" % validate_origin_samples_uri
        )
        input_artifacts = self.resolve_input_artifacts(
            input_dict, component, driver_args
        )

        output_artifacts = {}
        if not io_utils.exists(validate_samples_uri):
            raise RuntimeError(
                "validate sample uri %s does not exist!" % validate_samples_uri
            )

        if not io_utils.exists(validate_origin_samples_uri):
            raise RuntimeError(
                "validate origin sample uri %s does not exist!"
                % validate_origin_samples_uri
            )

        artifact = Artifact(type_name=standard_artifacts.Samples.TYPE_NAME)
        artifact.meta.uri = validate_samples_uri
        artifact.meta.producer_component = component.id
        artifact.meta.import_only = True
        output_artifacts["validate_samples"] = [artifact]

        artifact = Artifact(type_name=custom_artifacts.OriginSamples.TYPE_NAME)
        artifact.meta.uri = validate_origin_samples_uri
        artifact.meta.producer_component = component.id
        artifact.meta.import_only = True
        output_artifacts["validate_origin_samples"] = [artifact]

        return ExecutionInfo(
            input_dict=input_artifacts,
            output_dict=output_artifacts,
            exec_properties={},
            use_cached_result=False,  # 外部 import到 bmlx中的artifact，目前都没有重用(重复使用同一个artifact id)，后续需要整理下 artifact uri 逻辑，来支持重用
        )
