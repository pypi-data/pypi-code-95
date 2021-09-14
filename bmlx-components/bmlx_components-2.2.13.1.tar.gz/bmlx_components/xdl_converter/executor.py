"""bmlx model converter executor."""
import os
import sys
import logging
import tempfile
import re
import json
import xdl
import subprocess
import functools
from typing import Any, Dict, List, Text
import tensorflow as tf
from xdl.python.ops.ps_ops import ps_local_read_variables
from xdl.python.backend.tf.convert_utils import TF2XDL

from bmlx.flow import Executor, Artifact
from bmlx.fs.file_system import LocalFileSystem
from bmlx_components.proto import schema_pb2, model_pb2
from bmlx.utils import import_utils, artifact_utils, io_utils
from bmlx_components.xdl_base.executor import XdlExecutor
from bmlx_components.xdl_converter import (
    tf_converter,
    sparse_converter,
    model_conf_converter,
)
from bmlx_components.xdl_converter.fg_converter import FgConfConverter

CONVERTED_MODEL_OUTPUT_DIR = "converted_model"
EMB_BIN_DIR = "emb_bin"
ONLINE_MODEL_DIR = "online_model/"
FG_DIR = "online_model/fg/"
VALIDATE_SAMPLE_DIR = "online_model/validate_sample/"
OPTIMIZED_GRAPH_DIR = "online_model/optimized_graph/"


class XdlConverterExecutor(XdlExecutor):
    def _init_output_dir(self, output_dir):
        fs, path = io_utils.resolve_filesystem_and_path(output_dir)
        if not fs.exists(path):
            fs.mkdir(path)
        if not fs.exists(os.path.join(output_dir, EMB_BIN_DIR)):
            fs.mkdir(os.path.join(output_dir, EMB_BIN_DIR))
        if not fs.exists(os.path.join(output_dir, ONLINE_MODEL_DIR)):
            fs.mkdir(os.path.join(output_dir, ONLINE_MODEL_DIR))
        if not fs.exists(os.path.join(output_dir, FG_DIR)):
            fs.mkdir(os.path.join(output_dir, FG_DIR))
        if (
            fs.exists(path)
            and fs.exists(os.path.join(output_dir, EMB_BIN_DIR))
            and fs.exists(os.path.join(output_dir, ONLINE_MODEL_DIR))
            and fs.exists(os.path.join(output_dir, FG_DIR))
        ):
            logging.info(
                "initialize converted model output dir: %s successfully!",
                output_dir,
            )
            return True
        else:
            logging.error(
                "initialize converted model output dir: %s failed!", output_dir
            )
            return False

    def _resolve_model_meta(self, model_meta_dir: Text):
        if io_utils.exists(os.path.join(model_meta_dir, "model.pbtxt")):
            model_meta_path = os.path.join(model_meta_dir, "model.pbtxt")
            model_pb = io_utils.parse_pbtxt_file(
                model_meta_path, model_pb2.Model()
            )
            if not (model_pb and model_pb.model_path):
                raise RuntimeError(
                    "invalid model meta info parsed from %s" % model_meta_path
                )
        elif io_utils.exists(model_meta_dir):
            model_meta_dir = model_meta_dir.strip("/")
            model_pb = model_pb2.Model()
            model_pb.model_path = "/".join(model_meta_dir.split("/")[:-1])
            model_pb.model_version = model_meta_dir.split("/")[-1]
        else:
            raise RuntimeError("Empty model meta dir")

        logging.info("parsed model meta info: %s", model_pb)
        return model_pb

    def _resolve_origin_fg_conf(self, origin_fg_conf_path):
        fs, uri = io_utils.resolve_filesystem_and_path(origin_fg_conf_path)
        if not fs.exists(uri):
            raise RuntimeError(
                "Origin fg conf %s does not exist" % origin_fg_conf_path
            )
        return io_utils.read_file_string(origin_fg_conf_path)

    def _save_model_meta(
        self,
        output_dir,
        trained_model_version,
        converted_model_version,
        model_meta_output_path,
    ):
        converted_model = model_pb2.ConvertedModel()
        converted_model.embedding_path = os.path.join(output_dir, EMB_BIN_DIR)
        converted_model.graph_path = os.path.join(output_dir, ONLINE_MODEL_DIR)
        converted_model.fg_path = os.path.join(output_dir, FG_DIR)
        converted_model.trained_model_version = trained_model_version
        converted_model.converted_model_version = int(converted_model_version)
        logging.info(
            "convert finished, model meta gen to %s" % model_meta_output_path
        )
        io_utils.write_pbtxt_file(
            os.path.join(model_meta_output_path, "converted_model.pbtxt"),
            converted_model,
        )

    def _convert_fg_conf(self, input_dict, origin_model_conf, inputs):
        origin_fg_conf_content = self._resolve_origin_fg_conf(
            input_dict["fg_conf"][0].meta.uri
        )
        yaml_converter = FgConfConverter(origin_fg_conf_content)

        whole_inputs = model_conf_converter.get_whole_inputs(
            origin_model_conf, inputs
        )
        converted_fg_yaml = yaml_converter.extract_sub_dag(whole_inputs)
        assert len(whole_inputs) > 0, "model inputs is empty."

        return converted_fg_yaml, yaml_converter.get_shared_slots()

    def execute_as_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        assert "model_name" in exec_properties
        assert "fg_conf" in input_dict and "model" in input_dict
        assert "model" in input_dict and len(input_dict["model"]) == 1

        # XDL 的逻辑已经改成 convert 阶段需要将 embedding 数据写到 ceto的hdfs 路径(hdfs://bigocluster/data/embs/)下，且指定版本
        # 这里先兼容 XDL 的逻辑，等后续XDL 统一改造
        # 这里是将 xdl convert job 启动时候的时间戳，写到各个worker启动的命令行参数中，从而实现各个worker的数值同步
        converted_model_version = xdl.get_launch_time()
        assert (
            converted_model_version != 0
        ), "Invalid launch time, not appliable to converted_model_version"

        worker_num = xdl.get_task_num()
        logging.info("worker_num: %s", worker_num)
        local_emb = exec_properties["local_emb"]
        logging.info("local_emb: %s", local_emb)

        stage = exec_properties["stage"]
        logging.info("start xdl %s", stage)

        model_meta_pb = self._resolve_model_meta(
            input_dict["model"][0].meta.uri
        )

        origin_model_conf = json.loads(
            io_utils.read_file_string(
                os.path.join(
                    model_meta_pb.model_path,
                    model_meta_pb.model_version,
                    "tf_predict_model_conf_0.txt",
                )
            )
        )

        output_dir = os.path.join(
            model_meta_pb.model_path,
            model_meta_pb.model_version,
            CONVERTED_MODEL_OUTPUT_DIR,
        )

        logging.info(
            "start convert, cluster_role: %s, converted model output_dir: %s",
            exec_properties["cluster_role"],
            output_dir,
        )

        if xdl.get_task_index() == 0 and not self._init_output_dir(output_dir):
            raise RuntimeError("Failed to init output dir")

        frozen_graph, real_output_node = tf_converter.convert_graph(
            exec_properties["output_node"],
            os.path.join(model_meta_pb.model_path, model_meta_pb.model_version),
        )
        # reset output node
        origin_model_conf["output"] = real_output_node
        # get all tf inputs
        tf_inputs = tf_converter.get_tf_graph_inputs(
            origin_model_conf, frozen_graph
        )
        # remove unused subgraph
        # # origin_model_conf, frozen_graph will be modified
        tf_converter.remove_unused_subgraph(origin_model_conf, frozen_graph)

        # all workers include worker-master and worker-slave do convert-sparse
        sparse_converter.convert_sparse(
            exec_properties,
            os.path.join(model_meta_pb.model_path, model_meta_pb.model_version),
            origin_model_conf,  # updated origin_model_conf
            os.path.join(output_dir, EMB_BIN_DIR),
            converted_model_version,
        )

        if xdl.get_task_index() != 0:
            return

        ############ only worker master do following works
        ############ only worker master do following works

        # get updated tf inputs
        tf_inputs = [
            node.name for node in frozen_graph.node if node.op == "Placeholder"
        ]

        # serialize tf graph
        io_utils.write_string_file(
            os.path.join(output_dir, ONLINE_MODEL_DIR, "graph.bin"),
            frozen_graph.SerializeToString(),
        )
        # convert fg conf
        converted_fg_yaml, shared_slots = self._convert_fg_conf(
            input_dict, origin_model_conf, tf_inputs
        )
        # save converted fg conf yaml
        io_utils.write_string_file(
            os.path.join(output_dir, FG_DIR, "fg.yaml"),
            converted_fg_yaml.encode(),
        )
        # record model_path & fg_path before convert
        source_model_info = {
            'fg_conf': input_dict["fg_conf"][0].meta.uri,
            'model': input_dict["model"][0].meta.uri
        }
        io_utils.write_string_file(
            os.path.join(output_dir, ONLINE_MODEL_DIR, "source_model_info.json"),
            json.dumps(source_model_info).encode()
        )

        # convert model conf
        model_conf = model_conf_converter.rewrite_model_conf(
            origin_model_conf,
            tf_inputs,
            real_output_node,
            shared_slots,
            # embedding的维度，目前是靠解析sparse embedding文件获得, 前面先调用了 convert_sparse()，因此能够从 meta_0 文件中获得这个信息
            sparse_converter.get_sparse_embedding_dims(
                os.path.join(output_dir, EMB_BIN_DIR)
            ),
            exec_properties["model_name"],
            exec_properties["model_class"],
            exec_properties["half_p"],
            local_emb
        )

        # save converted model conf
        io_utils.write_string_file(
            os.path.join(output_dir, ONLINE_MODEL_DIR, "model.json"),
            json.dumps(model_conf, indent=4, sort_keys=True).encode(),
        )

        # save fg so if needed
        if "fg_lib" in input_dict and len(input_dict["fg_lib"]) > 0:
            fg_lib_path = input_dict["fg_lib"][0].meta.uri
            assert io_utils.exists(fg_lib_path)

            file_content = io_utils.read_file_string(fg_lib_path)

            io_utils.write_string_file(
                os.path.join(
                    output_dir, FG_DIR, os.path.basename(fg_lib_path),
                ),
                file_content,
            )

        # RTP 图优化
        if (
            exec_properties["model_class"]
            == model_conf_converter.RTP_MODEL_CLASS
            and exec_properties["optimize_tool_path"]
        ):
            tf_converter.optimize_graph(
                exec_properties["optimize_tool_path"],
                frozen_graph,
                model_conf,
                os.path.join(output_dir, OPTIMIZED_GRAPH_DIR),
            )

        # save converted_model meta info
        model_meta_output_path = artifact_utils.get_single_uri(
            output_dict["output"]
        )
        self._save_model_meta(
            output_dir,
            model_meta_pb.model_version,
            converted_model_version,
            model_meta_output_path,
        )
