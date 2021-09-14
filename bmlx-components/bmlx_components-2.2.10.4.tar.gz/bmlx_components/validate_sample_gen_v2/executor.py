import os
import sys
import hashlib
import logging
import yaml
import collections
import tempfile
import subprocess
import gzip
import json
import shutil
import re
from typing import Dict, Text, List, Any
from datetime import datetime, timedelta
from pytz import timezone
from enum import Enum

from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from kafka.vendor import six

from bmlx.flow import Executor, Artifact
from bmlx.utils import artifact_utils, io_utils
from bmlx.fs.ceph import CephFileSystem
from bmlx.fs.hdfs import HadoopFileSystem
from bmlx_components.proto import model_pb2
from bmlx_components.utils import fg_utils

BMLX_KAFKA_CONSUMER_GROUP = "bmlx_consumer"
HDFS_CHECK_SAMPLE_PATH = "hdfs://bigo-rt/user/bmlx/check_sample"

class SampleGenExecutor(Executor):
    def _parse_fg_from_converted_model(self, model_meta_path):
        model_pb = io_utils.parse_pbtxt_file(
            os.path.join(model_meta_path, "converted_model.pbtxt"),
            model_pb2.ConvertedModel(),
        )

        if not (model_pb and model_pb.fg_path):
            raise RuntimeError(
                "invalid model meta info parsed from %s" % model_meta_path
            )
        logging.info("parsed pushed model meta info: %s", model_pb)

        fs, path = io_utils.resolve_filesystem_and_path(model_pb.fg_path)
        if not fs.exists(path):
            raise RuntimeError(
                "model fg path %s does not exist!"
                % model_pb.fg_path
            )

        fg_path = os.path.join(model_pb.fg_path, "fg.yaml")
        return fg_path

    def filter_origin_samples(
        self,
        kafka_brokers: Text,
        kafka_topic: Text,
        local_dir: Text,
        sample_count_limit: int,
    ):

        local_origin_samples_path = os.path.join(
            local_dir, "origin_samples.txt"
        )

        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), "../mlplat-protos")
        )
        from mlplat.feature.original_feature_pb2 import OriginalFeature

        with open(local_origin_samples_path, "w") as origin_sample_fp:
            samples_count = 0
            max_retry_times = 3
            now_retry_count = 0
            open_kafka_success = False
            while now_retry_count < max_retry_times:
                try:
                    consumer = KafkaConsumer(
                        kafka_topic,
                        group_id=BMLX_KAFKA_CONSUMER_GROUP,
                        bootstrap_servers=kafka_brokers,
                        auto_offset_reset="latest",
                        enable_auto_commit=True,
                    )
                    consumer.poll(1)
                    consumer.seek_to_end()
                    open_kafka_success = True
                    break
                except Exception as e:
                    logging.warning("consume kafka failed, exception: %s", e)
                    now_retry_count += 1
            if not open_kafka_success:
                raise RuntimeError("Failed to consume Kafka!")

            for msg in consumer:
                line = msg.value.decode("latin1")
                line = line[line.find("{") : line.rfind("}") + 1]
                try:
                    json_line = json.loads(line)
                    line = json_line.get("pb_msg")
                    dispatch_id = json_line.get("dispatcher_id")
                except json.decoder.JSONDecodeError:
                    continue

                origin_bytes = fg_utils.parse_featurelog_line(line)
                if not origin_bytes:
                    continue
                origin_pb = OriginalFeature()
                origin_pb.ParseFromString(origin_bytes)
                if len(origin_pb.items.item_ids) == 0:
                    continue

                if "dispatcher_id" not in origin_pb.scenario.feature:
                    logging.debug("fill dispatcher_id [%s] now", dispatch_id)
                    origin_pb.scenario.feature["dispatcher_id"].bytes = dispatch_id.encode()
                    outline = fg_utils.compress_originpb_to_line(origin_pb)
                    origin_sample_fp.write(outline.decode())
                else:
                    origin_sample_fp.write(line)
                origin_sample_fp.write("\n")
                samples_count += 1
                logging.info(
                    "[selected] %s/%s",
                    samples_count, sample_count_limit
                )
                if samples_count >= sample_count_limit:
                    break
        return local_origin_samples_path

    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)

        assert len(input_dict["converted_model"]) == 1
        assert len(input_dict["fg_py_lib"]) == 1
        assert len(output_dict["samples"]) == 1
        assert len(output_dict["origin_samples"]) == 1

        sample_count_limit = exec_properties["output_sample_limit"]
        product_name = exec_properties["product_name"]
        source = exec_properties["source"]
        # 这里有个trick的地方，fg.yaml 是根据模型的路径，找到的模型转换之后的yaml；
        # 而 fglib_py3.so 的地址 是fg-importer 获得的, 有可能两者对不上 (比如，模型发布完了之后，有人突然发布了新的 fg 版本。这样会导致使用了新的 fglib_py3.so)
        # 但是，鉴于模型端到端校验 工具使用的不是很频繁，因此这种case可以忽略
        fg_conf_path_manual = exec_properties.get(
            "fg_conf_path",
            ""
        )
        if fg_conf_path_manual:
            fg_conf_path = fg_conf_path_manual
        else:
            fg_conf_path = self._parse_fg_from_converted_model(
                input_dict["converted_model"][0].meta.uri
            )

        fg_lib_path = input_dict["fg_py_lib"][0].meta.uri
        logging.info("fg_conf_path: %s", fg_conf_path)
        logging.info("fg_lib_path: %s", fg_lib_path)


        with tempfile.TemporaryDirectory() as tempdir:
            fg_utils.fetch_fg(fg_conf_path, fg_lib_path, tempdir)

            # 事前校验默认填充的offline_extra_info
            fg_utils.add_validate_offline_op(os.path.join(tempdir, "fg.yaml"))

            local_origin_samples_path = self.filter_origin_samples(
                kafka_brokers=exec_properties["kafka_brokers"],
                kafka_topic=exec_properties["kafka_topic"],
                local_dir=tempdir,
                sample_count_limit=sample_count_limit,
            )

            local_processed_samples_path = os.path.join(
                tempdir, "processed_samples.tmp"
            )

            ret = fg_utils.fg_process(
                tempdir,
                local_origin_samples_path,
                local_processed_samples_path,
                product_name,
                source
            )
            if ret != 0:
                raise RuntimeError("Failed to process origin samples")

            gziped_processed_samples = os.path.join(
                tempdir, "processed_samples.gz"
            )
            # gzip the file, to feed xdl
            with open(local_processed_samples_path, "rb") as f_in:
                with gzip.open(gziped_processed_samples, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            logging.info("[origin]output_dict[samples].meta.uri: %s", output_dict["samples"][0].meta.uri)
            # 覆盖统一的artifact路径，改为采样样本存储到hdfs上（xdl读不了ceph）
            # ceph路径应为类似ceph://fs-ceph-hk.bigo.sg/mlpipeline-test/artifacts/exp_499/run_19026/validate_sample_gen 格式
            splited = (output_dict["samples"][0].meta.uri).rstrip('/').split('/')
            upload_hdfs_path = os.path.join(
               HDFS_CHECK_SAMPLE_PATH, splited[-3], splited[-2],
               os.path.basename(gziped_processed_samples)
            )
            output_dict["samples"][0].meta.uri = upload_hdfs_path

            logging.info("[modified]output_dict[samples].meta.uri: %s", output_dict["samples"][0].meta.uri)

            samples_remote_dir = "/".join(
                output_dict["samples"][0].meta.uri.rstrip('/').split('/')[:-1]
            )
            io_utils.upload_file(
                gziped_processed_samples, samples_remote_dir
            )
            io_utils.upload_file(
                local_origin_samples_path,
                output_dict["origin_samples"][0].meta.uri,
            )