import logging
import sys

from bmlx.execution.driver import BaseDriver
from bmlx.execution.driver import ExecutionInfo
from typing import Dict, Text, Any, List, Optional
from bmlx.flow import Channel, Pipeline, Component, Artifact, DriverArgs
from bmlx.utils import channel_utils, import_utils


class ImporterDriver(BaseDriver):
    def _import_artifact(
        self,
        pipeline: Pipeline,
        component: Component,
        uris: List[Text],
        reimport: bool,
        channel: Channel,
        driver_args: DriverArgs,
        import_checker: Text,
    ) -> List[Artifact]:
        results = []
        import_check_callback = import_utils.import_func_from_module(
            "bmlx_components.importer_node.import_checker", import_checker
        )

        for uri in uris:
            if not import_check_callback(uri):
                raise RuntimeError("check artifact %s failed!" % uri)

            previous_artifacts = self._metadata.get_artifacts_by_uri(uri)

            result = Artifact(type_name=channel.type_name)
            result.meta.uri = uri
            # 表示并不创建文件，只是引入
            result.meta.import_only = True
            result.meta.producer_component = component.id

            if previous_artifacts and not reimport:
                associate_meta = max(previous_artifacts, key=lambda m: m.id)
                result.meta.id = associate_meta.id

            results.append(result)

        return results

    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ):
        output_artifacts = {
            "result": self._import_artifact(
                pipeline=pipeline,
                component=component,
                uris=exec_properties["source_uri"],
                channel=output_dict["result"],
                reimport=exec_properties["reimport"],
                driver_args=driver_args,
                import_checker=exec_properties["import_checker"],
            )
        }

        output_dict["result"] = channel_utils.as_channel(
            output_artifacts["result"]
        )

        logging.info("Imported Artifact %s" % output_dict["result"])

        return ExecutionInfo(
            input_dict={},
            output_dict=output_artifacts,
            exec_properties={},
            use_cached_result=False,
        )
