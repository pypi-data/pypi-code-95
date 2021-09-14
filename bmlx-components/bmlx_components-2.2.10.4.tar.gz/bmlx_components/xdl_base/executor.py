"""bmlx xdl base executor."""
import os
import logging
import re
import tensorflow as tf
import socket
import functools
import tempfile
import abc
import json
import numpy as np
import copy
from typing import Any, Dict, List, Text, Tuple

from bmlx.config import Configuration
from bmlx.flow import Executor, Artifact
from bmlx.utils import import_utils, artifact_utils, io_utils
from bmlx_components.proto import schema_pb2


MY_DIR = os.path.dirname(os.path.realpath(__file__))


class MetricsSinker:
    def __init__(self):
        self._dir = tempfile.mkdtemp()

    def close(self):
        # io_utils.rmtree(self._dir)
        pass

    @abc.abstractmethod
    def __call__(self, ts, metrics, sample_ts, step):
        raise NotImplementedError("not implelmented")


class XdlExecutor(Executor):
    __slots__ = []

    def _resolve_schema(self, schema_artifact) -> schema_pb2.Schema:
        # 获取schema信息
        schema_uri = artifact_utils.get_single_uri(schema_artifact)
        return io_utils.parse_pbtxt_file(schema_uri, schema_pb2.Schema())

    def _substitude_reader_script(self, script_str):
        ret = re.sub(r' --config ', ' --json_file ', script_str)
        return ret

    def _resolve_latest_sample_meta(
        self, samples_artifacts
    ) -> Tuple[Text, Text]:
        # 最新的样本
        latest_sample_uri = max(
            samples_artifacts, key=lambda x: x.meta.uri
        ).meta.uri

        # 目前机制，限制输出必须为YYYYMMDD/HH的格式，之后再fix这个限制 TODO by zhangguanxing@bigo.sg
        if re.match(r".*\/[0-9]{8}\/[0-9]{2}$", latest_sample_uri):
            latest_sample_hour = latest_sample_uri[-11:]
        elif re.match(r".*\/[0-9]{8}$", latest_sample_uri):
            latest_sample_hour = latest_sample_uri[-8:]
        else:
            raise RuntimeError(
                "last_sample_uri %s does not match valid pattern %s or %s",
                latest_sample_uri,
                r".*\/[0-9]{8}\/[0-9]{2}$",
                r".*\/[0-9]{8}$",
            )

        return (latest_sample_uri, latest_sample_hour)

    def init_chief_worker_env(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        try:
            import xdl.python.training.env as xdl_env
            from xdl.python.utils.config import parse_from_raw
        except ImportError:
            raise RuntimeError("please run bmlx in docker_env with xdl env")
        is_local = exec_properties["is_local"]
        if is_local:
            args = [
                "--run_mode",
                "local",
                "--model_bank",
                exec_properties["model_bank"],
                "--ckpt_dir",
                exec_properties["ckpt"],
                "--launch_time",
                str(exec_properties["launch_time"]),
            ]
        else:
            args = [
                "--run_mode",
                "dist",
                "--task_name",
                "chief",
                "--zk_addr",
                exec_properties["zk_addr"],
                "--chief_zk_addr",
                exec_properties["chief_zk_addr"],
                "--app_id",
                exec_properties["job_id"],
                "--task_num",
                str(exec_properties["task_num"]),
                "--task_index",
                str(exec_properties["task_index"]),
                "--model_bank",
                exec_properties["model_bank"],
                "--ckpt_dir",
                exec_properties["ckpt"],
                "--launch_time",
                str(exec_properties["launch_time"]),
            ]

        if not exec_properties["need_ps"]:
            args.extend(["--ps_mode", False])
        parse_from_raw(args)

        logging.info("startup chief commands is %s" % args)
        xdl_env.init_env()

    def init_worker_env(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        try:
            import xdl.python.training.env as xdl_env
            from xdl.python.utils.config import parse_from_raw
        except ImportError:
            raise RuntimeError("please run bmlx in docker_env with xdl env")
        is_local = exec_properties["is_local"]
        if is_local:
            args = [
                "--run_mode",
                "local",
                "--model_bank",
                exec_properties["model_bank"],
                "--ckpt_dir",
                exec_properties["ckpt"],
                "--launch_time",
                str(exec_properties["launch_time"]),
            ]
        else:
            args = [
                "--run_mode",
                "dist",
                "--task_name",
                "worker",
                "--zk_addr",
                exec_properties["zk_addr"],
                "--chief_zk_addr",
                exec_properties["chief_zk_addr"],
                "--app_id",
                exec_properties["job_id"],
                "--task_num",
                str(exec_properties["task_num"]),
                "--task_index",
                str(exec_properties["task_index"]),
                "--model_bank",
                exec_properties["model_bank"],
                "--ckpt_dir",
                exec_properties["ckpt"],
                "--launch_time",
                str(exec_properties["launch_time"]),
            ]

        if not exec_properties["need_ps"]:
            args.extend(["--ps_mode", False])
        parse_from_raw(args)

        logging.info("startup commands is %s" % args)
        xdl_env.init_env()

    def init_ps_or_scheduler_env(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ) -> None:
        try:
            import xdl.python.training.env as xdl_env
            from xdl.python.utils.config import parse_from_raw
        except ImportError:
            raise RuntimeError("please run bmlx in docker_env with xdl env")

        args = [
            "--run_mode",
            "dist",
            "--task_name",
            exec_properties["cluster_role"],
            "--zk_addr",
            exec_properties["zk_addr"],
            "--chief_zk_addr",
            exec_properties["chief_zk_addr"],
            "--app_id",
            exec_properties["job_id"],
            "--task_num",
            str(exec_properties["task_num"]),
            "--task_index",
            str(exec_properties["task_index"]),
            "--model_bank",
            exec_properties["model_bank"],
            "--ckpt_dir",
            exec_properties["ckpt"],
            "--launch_time",
            str(exec_properties["launch_time"]),
        ]

        if exec_properties["need_ps"]:
            args.extend(
                [
                    "--ps_num",
                    str(
                        exec_properties["runtime_configs"]["resources"]["ps"][
                            "instances"
                        ].as_number()
                    ),
                    "--ps_memory_m",
                    "%.f"
                    % exec_properties["runtime_configs"]["resources"]["ps"][
                        "memory"
                    ]
                    .as_sunit()
                    .to_mega_i(),
                    "--ps_cpu_cores",
                    str(
                        exec_properties["runtime_configs"]["resources"]["ps"][
                            "cpu"
                        ].as_number()
                    ),
                ]
            )

        parse_from_raw(args)
        xdl_env.init_env()

    def _tf_metrics_sinker(self, exec_properties):
        class S(MetricsSinker):
            def __init__(self):
                super(S, self).__init__()
                self.fw = tf.compat.v1.summary.FileWriter(self._dir)
                self._final_metric_value = dict()

            def __call__(self, ts, metrics, sample_ts, step):
                logging.debug("dump metrics step %s to %s" % (step, self._dir))
                for name, value in metrics:
                    if isinstance(value, np.ndarray):
                        self._final_metric_value[name] = []
                        for i, subvalue in enumerate(
                            value.tolist()
                            if isinstance(value.tolist(), list)
                            else [value.tolist()]
                        ):
                            summary = tf.Summary(
                                value=[
                                    tf.Summary.Value(
                                        tag="%s_%d" % (name, i),
                                        simple_value=subvalue,
                                    )
                                ]
                                if not isinstance(subvalue, list)
                                else [
                                    tf.Summary.Value(
                                        tag="%s_%d" % (name, i),
                                        simple_value=sv,
                                    )
                                    for sv in subvalue
                                ]
                            )
                            self.fw.add_summary(
                                summary=summary, global_step=step
                            )
                            self._final_metric_value[name].append(subvalue)
                    elif isinstance(value, (int, float)):
                        summary = tf.Summary(
                            value=[
                                tf.Summary.value(tag=name, simple_value=value)
                            ]
                        )
                        self.fw.add_summary(summary=summary, global_step=step)
                        self._final_metric_value[name] = value
                    else:
                        raise RuntimeError(
                            "unknown metrics type: %s" % (type(value))
                        )
                self._final_metric_value["sample_ts"] = sample_ts
                self.fw.flush()

            def close(self):
                fp = "{}/exp_{}/run_{}/{}".format(
                    exec_properties["artifact_storage_base"],
                    str(exec_properties["experiment_id"]),
                    str(exec_properties["pipeline_execution_id"]),
                    str(exec_properties["component_id"]),
                )
                logging.info("upload metrics from %s => %s" % (self._dir, fp))
                io_utils.copytree(self._dir, fp)
                self.fw.close()
                if self._final_metric_value:
                    io_utils.write_string_file(
                        os.path.join(fp, "final_metrics"),
                        json.dumps(self._final_metric_value).encode(),
                    )
                    logging.info("final metrics: %s", self._final_metric_value)
                super(S, self).close()

        return S()

    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)
        logging.info(
            "running xdl in host : %s",
            socket.gethostbyname(socket.gethostname()),
        )

        cluster_role = exec_properties["cluster_role"]
        if cluster_role == "chief-worker":
            self.init_chief_worker_env(input_dict, output_dict, exec_properties)
            self.execute_as_chief_worker(input_dict, output_dict, exec_properties)
        elif cluster_role == "worker":
            self.init_worker_env(input_dict, output_dict, exec_properties)
            self.execute_as_worker(input_dict, output_dict, exec_properties)
        elif cluster_role in ("scheduler", "ps"):
            self.init_ps_or_scheduler_env(
                input_dict, output_dict, exec_properties
            )
            self.execute_as_ps_or_scheduler(
                input_dict, output_dict, exec_properties
            )
        else:
            raise RuntimeError("Invalid cluster role %s" % cluster_role)

    """
    worker的执行，在不同的阶段，worker的初始化和执行逻辑不同，子类主要设置
    1. exec_properties["model_bank"], exec_properties["ckpt"]
    """

    @abc.abstractmethod
    def execute_as_chief_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    def execute_as_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    def execute_as_ps_or_scheduler(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        raise NotImplementedError()
