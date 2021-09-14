import os
import sys
import logging
import re
import functools
import time
import hashlib
import tempfile
from datetime import datetime, timedelta
from pytz import timezone
from typing import Any, Dict, List, Text

from bmlx.flow import Executor, Artifact
from bmlx_components.proto import schema_pb2, model_pb2
from bmlx.utils import import_utils, artifact_utils, io_utils

from bmlx_components.utils import ceto_publisher
from bmlx_components.utils.common_tools import digit_to_bytescount

EU_HDFS_HOST = "hdfs://bigo-eu"
EU_CETO_MODEL_ROOT_DIR = "/data/models"
SG_CETO_EMB_ROOT_DIR = "hdfs://bigocluster/data/embs"

EMB_META_PATTERN = "([a-zA-Z0-9\-_]+/[0-9]+/[0-9]+)/[0-9]+/"

class PusherExecutor(Executor):
    def _resolve_converted_model_meta(self, model_meta_path):
        model_pb = io_utils.parse_pbtxt_file(
            os.path.join(model_meta_path, "converted_model.pbtxt"),
            model_pb2.ConvertedModel(),
        )

        if not (model_pb and model_pb.embedding_path and model_pb.graph_path):
            raise RuntimeError(
                "invalid model meta info parsed from %s" % model_meta_path
            )
        logging.info("parsed pushed model meta info: %s", model_pb)

        fs, path = io_utils.resolve_filesystem_and_path(model_pb.embedding_path)
        if not fs.exists(path):
            raise RuntimeError(
                "model embedding path %s does not exist!"
                % model_pb.embedding_path
            )

        fs, path = io_utils.resolve_filesystem_and_path(model_pb.graph_path)
        if not fs.exists(path):
            raise RuntimeError(
                "model graph path %s does not exist!" % model_pb.graph_path
            )

        return model_pb

    def get_embeddings(self, emb_bin_path):
        fs, path = io_utils.resolve_filesystem_and_path(emb_bin_path)
        paths = fs.ls(path)

        assert len(paths) >= 1
        fpath = paths[0]

        res_paths = {}
        if fpath.find("emb_bin/meta_") < 0:
            raise ValueError(
                "Invalid emb bin meta file %s, should contains 'emb_bin/meta_0'"
                % fpath
            )
        file_content = io_utils.read_file_string(fpath).decode()
        for line in file_content.split("\n"):
            if not line or len(line) <= 8:
                continue

            dim, misc = line[8:].split("|", 1)
            meta_0_path, start, end, count, size = misc.split(",", 4)
            s = re.match(EMB_META_PATTERN, meta_0_path)
            if not s:
                raise ValueError(
                    "Invalid emb path (%s) in meta_0, should has info like 'model_name/1610000000/13/0/' "
                    % meta_0_path
                )
            real_path = s.group(1)
            emb_file_size = digit_to_bytescount(int(size))
            logging.info("[emb_%s] size : %s",
                dim, emb_file_size
            )

            emb_path = os.path.join(
                SG_CETO_EMB_ROOT_DIR,
                real_path
            )
            res_paths.update({dim : emb_path})
        return res_paths

    def publish_graph_and_emb(
            self,
            model_name,
            model_version,
            namespace,
            graph_path,
            embedding_path
        ):
        emb_paths = self.get_embeddings(embedding_path)
        logging.info("[emb_paths] are %s", emb_paths)

        # copy file to ceto"s model dir
        graph_dir_name = os.path.join(
            "upload",
            os.path.basename(graph_path)
        )
        logging.info("[graph_dir_name]%s", graph_dir_name)
        ceto_model_base_path = os.path.join(
            namespace, model_name, str(model_version)
        )
        ceto_model_path = os.path.join(
            EU_CETO_MODEL_ROOT_DIR, ceto_model_base_path
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            local_upload_path = os.path.join(
                tmpdir, graph_dir_name
            )
            logging.info("[upload_path]%s", local_upload_path)
            io_utils.download_dir(
                graph_path, local_upload_path
            )
            # upload emb with graph
            for dim in emb_paths:
                io_utils.download_dir(
                    emb_paths[dim],
                    os.path.join(
                        local_upload_path,
                        f"emb/{dim}"
                    )
                )

            io_utils.upload_dir(
                local_upload_path,
                os.path.join(
                    EU_HDFS_HOST.rstrip('/'), ceto_model_path.lstrip('/')
                )
            )
            logging.info("upload eu hdfs finish.")

        # update meta to ceto
        ret = ceto_publisher.publish_model_to_ceto(
            model_name, namespace, model_version, ceto_model_path, "eu"
        )
        if not ret:
            logging.error(
                "Failed to publish model to ceto, model name: %s, namespace: %s, model_version: %s, ceto_model_path: %s",
                model_name,
                namespace,
                model_version,
                ceto_model_path,
            )
            raise RuntimeError("Failed to publish model to ceto!")
        else:
            logging.info(
                "Successfully publish model to ceto, model name: %s, namespace: %s, model_version: %s, ceto_model_path: %s",
                model_name,
                namespace,
                model_version,
                ceto_model_path,
            )

    def save_meta(
        self, meta_output_path, model_name, model_version, origin_model_path
    ):
        logging.info("push finished, model meta gen to %s" % meta_output_path)
        pushed_model = model_pb2.PushedModel()
        pushed_model.version = model_version
        pushed_model.name = model_name
        pushed_model.origin_model_path = origin_model_path
        pushed_model.pushed_time = int(time.time())
        io_utils.write_pbtxt_file(
            os.path.join(meta_output_path, "pushed_model.pbtxt"), pushed_model
        )

    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)

        assert (
            "converted_model" in input_dict
            and len(input_dict["converted_model"]) == 1
        )
        converted_model_meta = self._resolve_converted_model_meta(
            input_dict["converted_model"][0].meta.uri
        )
        logging.info("[converted_model_meta]%s", converted_model_meta)

        local_emb = exec_properties["local_emb"]
        if local_emb != True:
            raise RuntimeError(
                "local_emb should be True [now: %s]"
                % local_emb
            )

        model_name = exec_properties["model_name"]
        namespace = exec_properties["namespace"]
        # 在xdl convert 中, 指定了model version, 并且将embedding数据转换成zmap格式，存放在了ceto指定的embedding目录下的 model_version子目录下
        # 这里的model version 和 converted_model 的 model version 保持一致
        model_version = converted_model_meta.converted_model_version

        self.publish_graph_and_emb(
            model_name,
            model_version,
            namespace,
            converted_model_meta.graph_path,
            converted_model_meta.embedding_path,
        )

        self.save_meta(
            artifact_utils.get_single_uri(output_dict["output"]),
            model_name,
            model_version,
            os.path.dirname(converted_model_meta.graph_path),
        )
