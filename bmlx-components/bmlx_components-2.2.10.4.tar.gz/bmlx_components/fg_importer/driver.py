import logging
import sys
import os
from bmlx.execution.driver import BaseDriver
from bmlx.execution.driver import ExecutionInfo
from typing import Dict, Text, Any, List, Optional
from bmlx.flow import Channel, Pipeline, Component, Artifact, DriverArgs
from bmlx.utils import channel_utils, import_utils, io_utils
from bmlx_components import custom_artifacts


class FgImporterDriver(BaseDriver):
    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ):
        def gen_artifact(type_name, uri):
            artifact = Artifact(type_name=type_name)
            artifact.meta.uri = uri
            artifact.meta.producer_component = component.id
            return artifact

        logging.info("fg_importer exec properties: %s", exec_properties)

        fg_conf_input_path = input_dict.get("fg_conf_input", None)
        fg_dir = exec_properties.get("fg_dir", "")
        fg_conf_path = exec_properties.get("fg_conf_path", "")
        fg_cpp_lib_path = exec_properties.get("fg_cpp_lib_path", "")
        fg_py_lib_path = exec_properties.get("fg_py_lib_path", "")

        input_artifacts = self.resolve_input_artifacts(
            input_dict, component, driver_args
        )

        # fg_dir
        output_artifacts = {}

        if fg_dir:
            logging.info("using fg dir %s to import fg", fg_dir)
            if not io_utils.exists(fg_dir):
                raise RuntimeError("fg_dir uri %s does not exist!" % fg_dir)
            else:
                assert io_utils.exists(os.path.join(fg_dir, "VERSION"))
                version = (
                    io_utils.read_file_string(os.path.join(fg_dir, "VERSION"))
                    .decode()
                    .strip("\t\n ")
                )
                logging.info(
                    "got fg version: %s, final fg_dir: %s",
                    version,
                    os.path.join(fg_dir, version),
                )
                assert io_utils.exists(os.path.join(fg_dir, version))
                assert io_utils.exists(os.path.join(fg_dir, version, "fg.yaml"))
                output_artifacts["fg_conf"] = [
                    gen_artifact(
                        custom_artifacts.FgConf.TYPE_NAME,
                        os.path.join(fg_dir, version, "fg.yaml"),
                    )
                ]
                assert io_utils.exists(
                    os.path.join(fg_dir, version, "fglib_py3.so")
                )
                output_artifacts["fg_py_lib"] = [
                    gen_artifact(
                        custom_artifacts.FgPyLib.TYPE_NAME,
                        os.path.join(fg_dir, version, "fglib_py3.so"),
                    )
                ]
                assert io_utils.exists(
                    os.path.join(fg_dir, version, "libfg_operators.so")
                )
                output_artifacts["fg_cpp_lib"] = [
                    gen_artifact(
                        custom_artifacts.FgCppLib.TYPE_NAME,
                        os.path.join(fg_dir, version, "libfg_operators.so"),
                    )
                ]
        else:
            if fg_conf_input_path is not None:
                output_artifacts["fg_conf"] = [
                    gen_artifact(
                        custom_artifacts.FgConf.TYPE_NAME, ""
                    )
                ]
            elif fg_conf_path:
                assert io_utils.exists(fg_conf_path)
                output_artifacts["fg_conf"] = [
                    gen_artifact(
                        custom_artifacts.FgConf.TYPE_NAME, fg_conf_path
                    )
                ]
            if fg_py_lib_path:
                assert io_utils.exists(fg_py_lib_path)
                output_artifacts["fg_py_lib"] = [
                    gen_artifact(
                        custom_artifacts.FgPyLib.TYPE_NAME, fg_py_lib_path
                    )
                ]
            if fg_cpp_lib_path:
                assert io_utils.exists(fg_cpp_lib_path)
                output_artifacts["fg_cpp_lib"] = [
                    gen_artifact(
                        custom_artifacts.FgCppLib.TYPE_NAME, fg_cpp_lib_path
                    )
                ]

        if not output_artifacts:
            raise RuntimeError("Failed to import fg, nothing imported")

        return ExecutionInfo(
            input_dict=input_artifacts,
            output_dict=output_artifacts,
            exec_properties=exec_properties,
            use_cached_result=False,
        )
