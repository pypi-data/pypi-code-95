import logging
import os
import time
import re
import hashlib
import json
from datetime import datetime, timedelta
from pytz import timezone
from typing import Dict, Text, Any, Optional

from bmlx.flow import Driver, DriverArgs, Channel, Pipeline, Component, Artifact
from bmlx.metadata.metadata import Metadata
from bmlx.utils import io_utils
from bmlx.execution.execution import ExecutionInfo
from bmlx_components.importer_node.import_checker import (
    check_succ_flag,
    check_skip_flag,
)
from bmlx_components.utils.ceto_fetcher import fetch_model_from_ceto
from bmlx_components.proto import model_pb2

from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts

MODEL_PARSE_PATTERN = (
    "(hdfs://bigocluster)*([a-zA-Z0-9\/\-_]*\/[0-9]{10})"
)


class ModelSelectorDriver(Driver):
    def __init__(self, metadata: Metadata):
        self._metadata = metadata

    def _parse_pushed_model(self, config_info) -> model_pb2.PushedModel:
        pushed_model = model_pb2.PushedModel()
        ret = re.match(MODEL_PARSE_PATTERN, config_info["path"])
        if ret is None:
            raise RuntimeError("Failed to parse pushed_model: %s" %
                config_info["path"]
            )

        pushed_model.origin_model_path = os.path.join(
            'hdfs://bigocluster', ret.group(2).lstrip('/')
        )
        pushed_model.name = config_info["name"]
        pushed_model.version = int(ret.group(2)[-10:])
        return pushed_model

    def _save_pushed_model_meta(
        self,
        pushed_model: model_pb2.PushedModel,
        pushed_model_storage_base_path: Text,
    ):
        if not io_utils.exists(pushed_model_storage_base_path):
            io_utils.mkdirs(pushed_model_storage_base_path)

        hasher = hashlib.md5()
        hasher.update(pushed_model.SerializeToString())
        checksum = hasher.hexdigest()
        meta_path = os.path.join(
            pushed_model_storage_base_path, checksum, "pushed_model.pbtxt"
        )
        if not io_utils.exists(meta_path):
            io_utils.write_pbtxt_file(meta_path, pushed_model)
        return meta_path

    def _parse_source_model_info(self, origin_model_path: Text):
        file_path = os.path.join(
            origin_model_path.rstrip("/"), "source_model_info.json"
        )
        read_in = io_utils.read_file_string(file_path)
        content = json.loads(read_in.decode())
        logging.info("_parse_source_model_info: %s, json_content: %s" % (read_in, content))
        model = content['model']
        fg_conf = content['fg_conf']
        return model, fg_conf

    def pre_execution(
        self,
        input_dict: Dict[Text, Channel],
        output_dict: Dict[Text, Channel],
        exec_properties: Dict[Text, Any],
        pipeline: Pipeline,
        component: Component,
        driver_args: DriverArgs,
    ) -> ExecutionInfo:
        logging.info(
            "online_model_selector exec properties: %s", exec_properties
        )

        min_serve_minutes = exec_properties["min_serve_minutes"]
        model_namespace = exec_properties["model_namespace"]
        model_name = exec_properties["model_name"]

        published_configs = fetch_model_from_ceto(
            name=model_name,
            namespace=model_namespace,
        )

        if published_configs["total"] == 0:
            raise RuntimeError(
                "Failed to get k8s model: '%s' within model_namespace: '%s'"
                % (model_name, model_namespace)
            )

        config = None
        for cfg in published_configs["list"]:
            if cfg["name"] == model_name:
                config = cfg
                break

        if config is None:
            raise RuntimeError(
                "Failed to get k8s model: '%s' within model_namespace: '%s'"
                % (model_name, model_namespace)
            )

        while (
            int(datetime.now().timestamp()) - config["pub_time"] / 1000
            <= min_serve_minutes * 60
        ):
            logging.info(
                "waiting until model to be served more than %d minutes"
                % min_serve_minutes
            )
            time.sleep(60)

        output_artifacts = {}
        assert len(output_dict) == 4

        pushed_model_storage_base_path = os.path.join(
            driver_args.artifact_storage_base, "pushed_model"
        )
        logging.info("pushed_model_storage_base_path: %s", pushed_model_storage_base_path)
        pushed_model = self._parse_pushed_model(config)

        if pushed_model.origin_model_path:
            # 解析source_model_info文件得到xdl训练后的模型和fg.yml
            xdl_model, xdl_fg = self._parse_source_model_info(
                pushed_model.origin_model_path
            )
            # generate pushed model artifact
            artifact = Artifact(
                type_name=custom_artifacts.PushedModel.TYPE_NAME
            )
            artifact.meta.uri = self._save_pushed_model_meta(
                pushed_model, pushed_model_storage_base_path
            )
            artifact.meta.import_only = True
            artifact.meta.producer_component = component.id
            output_artifacts["pushed_model"] = [artifact]
            # generate model artifact
            artifact = Artifact(type_name=standard_artifacts.Model.TYPE_NAME)
            artifact.meta.uri = xdl_model
            artifact.meta.producer_component = component.id
            artifact.meta.import_only = True
            output_artifacts["model"] = [artifact]
            # generate fg_conf artifact
            artifact = Artifact(
                type_name=custom_artifacts.FgConf.TYPE_NAME
            )
            artifact.meta.uri = os.path.join(
                pushed_model.origin_model_path,
                "fg/fg.yaml"
            )
            artifact.meta.producer_component = component.id
            artifact.meta.import_only = True
            output_artifacts["fg_conf"] = [artifact]
            # generate xdl_fg_conf artifact
            artifact = Artifact(
                type_name=custom_artifacts.FgConf.TYPE_NAME
            )
            artifact.meta.uri = xdl_fg
            artifact.meta.producer_component = component.id
            artifact.meta.import_only = True
            output_artifacts["xdl_fg_conf"] = [artifact]

        logging.info(
            "selected pushed model: %s\norigin model: %s\nfg_conf: %s\nxdl_fg_conf: %s",
            pushed_model, xdl_model,
            os.path.join(pushed_model.origin_model_path, "fg/fg.yaml"),
            xdl_fg,
        )
        return ExecutionInfo(
            input_dict={},
            output_dict=output_artifacts,
            exec_properties=exec_properties,
        )
