import logging
import copy
import re
import os
import abc
import time
import kazoo
import json

from typing import Text, Tuple
from bmlx.utils import proc_utils, artifact_utils, io_utils
from kazoo.client import KazooClient

from bmlx.execution.launcher import Launcher
from bmlx.execution.execution import ExecutionInfo
from bmlx_components.xdl_base.executor import XdlExecutor
from bmlx.proto.metadata import execution_pb2
from bmlx.config import Configuration
from bmlx_components.xdl_base import k8s_job_helper
from bmlx_components.utils import metric_client


MY_DIR = os.path.dirname(os.path.realpath(__file__))

"""
XDL launcher主要是针对不同的运行需求，启动不同JOB，目前主要包括两个
1. Distribute mode. 这里主要是向k8s发起启动命令。
    bmlx_submitter  -> watcher  -> (ink8s)  scheduler
                                -> (ink8s)  worker
                                -> (ink8s)  parameter server
    在这种运行模式下，会多次运行launcher的代码，通过cluster_role参数，在一次k8s执行中，launcher会有四种角色(watcher, scheduler, ps, worker[master-slave])
2. Local Mode, 本地模式实际上就是启动了xdl的local mode，同时在本地启动ps, worker的角色
"""


class XdlLauncher(Launcher):
    __slots__ = []

    """
    子类需要提供ckpt和modelbank计算逻辑
    """

    @abc.abstractmethod
    def _need_launch_xdl(self, input_dict, exec_properties) -> bool:
        raise NotImplementedError("please not use 'XdlLauncher' directly ")

    # 是否需要启动ps
    @abc.abstractmethod
    def _need_ps(self) -> bool:
        raise NotImplementedError("subclass should implement this")

    # 当单个worker失败的时候，是否直接被动Kill
    @abc.abstractmethod
    def _need_passive_quit(self) -> bool:
        raise NotImplementedError("subclass should implement this")

    @abc.abstractmethod
    def _stage(self) -> str:
        raise NotImplementedError("stage name")

    def _get_role_index(self):
        # 给xdl 各个pod 分配 task_index
        return int(os.environ["HOSTNAME"].split("-")[-1])

    def _run_as_watcher(self, execution_info):
        def command_generator(**kwargs):
            return self._ctx.generate_component_run_command(
                component_id=self._component.id,
                collect_log=True,
                experiment_id=self._driver_args.pipeline_execution.experiment_id,
                execution_name=self._driver_args.pipeline_execution.name,
                sub_component=True,
                extra=kwargs,
            )

        # namespace used for xdl job
        if not execution_info.exec_properties.get("namespace"):
            execution_info.exec_properties["namespace"] = self._ctx.namespace
        # launch 时间戳, 用于设置各个worker, ps, sc 的需要保持一致的参数，
        # 比如(xdl-convert时候的model version, 用于各个worker写入到相同的hdfs目录)
        execution_info.exec_properties["launch_time"] = int(time.time())

        self.register_component_execution()

        state = execution_pb2.State.RUNNING
        if execution_info.skip_execution:
            logging.info("component %s skip execution", self._component.id)
            state = execution_pb2.State.SKIPPED
        elif execution_info.use_cached_result:
            logging.info("component %s use cached result", self._component.id)
            state = execution_pb2.State.CACHED
        else:
            watcher_status_2_execution_state = {
                proc_utils.PollWaitStatus.SUCC: execution_pb2.State.SUCCEEDED,
                proc_utils.PollWaitStatus.FAIL: execution_pb2.State.FAILED,
                proc_utils.PollWaitStatus.CANCEL: execution_pb2.State.CANCELED,
                proc_utils.PollWaitStatus.TIMEOUT: execution_pb2.State.FAILED,
            }

            logging.info("execute %s", self._component.id)
            if self._need_launch_xdl(
                execution_info.input_dict, execution_info.exec_properties
            ):
                # create job, and waiting for completion
                # wait until all pods finished
                k8s_job_helper.launch_k8s_watcher(
                    context=self._ctx,
                    execution_info=execution_info,
                    command_generator=command_generator,
                    extra_spec={
                        "need_ps": self._need_ps(),
                        "passive_quit": self._need_passive_quit(),
                    },
                )

                # update volcano job info to component_execution
                self.update_component_execution_run_context(
                    volcano_job_id=execution_info.exec_properties["job_id"],
                    volcano_job_namespace=execution_info.exec_properties[
                        "namespace"
                    ],
                    cluster=execution_info.exec_properties["runtime_configs"][
                        "cluster"
                    ].as_str(),
                )

                watcher_status = k8s_job_helper.wait_k8s_job_completed(
                    execution_info=execution_info
                )
                state = watcher_status_2_execution_state[watcher_status]
            else:
                logging.info("does not need to launch xdl job")
                state = execution_pb2.State.SUCCEEDED

        self._report_metrics(execution_info)

        # persist result
        self.publish_component_execution(
            execution_info=execution_info, state=state
        )

    def _report_metrics(self, execution_info):
        # 从s3 下载metric 数据
        fp = "{}/exp_{}/run_{}/{}/final_metrics".format(
            execution_info.exec_properties["artifact_storage_base"],
            str(execution_info.exec_properties["experiment_id"]),
            str(execution_info.exec_properties["pipeline_execution_id"]),
            self._component.id,
        )
        if not io_utils.exists(fp):
            logging.warning("no final metrics found at %s", fp)
            return
        try:
            metrics = json.loads(io_utils.read_file_string(fp).decode())
        except Exception as e:
            raise RuntimeError(
                "Failed to get final metric value, remote path: %s, exception: %s",
                fp,
                e,
            )
        sample_ts = metrics.get("sample_ts", time.time()) * 1000
        del metrics["sample_ts"]
        # 根据 execution_id, experiment_id, component_id 将metric 数据写入到 prometheus
        labels = {
            "env": self._ctx.env,
            "run_id": str(
                execution_info.exec_properties["pipeline_execution_id"]
            ),
            "experiment_id": str(
                execution_info.exec_properties["experiment_id"]
            ),
            "component_id": str(self._component.id),
        }

        def convert_metric_name(name):
            return f"bmlx_metric_{name}".replace("/", "_").replace("-", "_")

        xdl_parameters = execution_info.exec_properties["parameters"]
        multi_labels = xdl_parameters["labels"].as_str_seq()

        prometheus_data = []
        for name, value in metrics.items():
            # 只针对 xdlauc 和 loss 进行上报
            if "xdlauc" not in name and "loss" not in name:
                continue

            if isinstance(value, list):
                for v, idx in zip(value, range(len(value))):
                    prometheus_data.append(
                        {
                            "n": convert_metric_name(name),
                            "ls": {
                                **labels,
                                **{
                                    "label": str(idx)
                                    if len(multi_labels) <= idx
                                    else multi_labels[idx]
                                },
                            },
                            "ts": int(sample_ts),
                            "v": float(v),
                        }
                    )
            else:
                prometheus_data.append(
                    {
                        "n": convert_metric_name(name),
                        "ls": labels,
                        "ts": int(sample_ts),
                        "v": float(value),
                    }
                )
        logging.info(
            "metric client report metrics to prometheus, metrics: %s",
            prometheus_data,
        )
        metric_client.report_metric_to_prometheus(prometheus_data)

    def _run_in_cluster(self, execution_info):
        cluster_role = execution_info.exec_properties["cluster_role"]

        # task index为分布式XDL必需参数，作用是制定启动角色
        vk_role_index = self._get_role_index()
        execution_info.exec_properties["task_index"] = (
            vk_role_index
        )

        assert cluster_role in (
            "scheduler",
            "ps",
            "worker",
            "chief-worker",
        )

        execution_info.exec_properties[
            "app_id"
        ] = execution_info.exec_properties["job_id"]

        super(XdlLauncher, self).run_executor(
            execution_info.input_dict,
            execution_info.output_dict,
            execution_info.exec_properties,
        )

    def _run_local_worker(self, execution_info: ExecutionInfo):
        self.register_component_execution()

        execution_info.exec_properties["cluster_role"] = "chief-worker"
        execution_info.exec_properties["launch_time"] = int(time.time())

        logging.info("run local worker, parameters: %s" % (execution_info))

        super(XdlLauncher, self).run_executor(
            execution_info.input_dict,
            execution_info.output_dict,
            execution_info.exec_properties,
        )

        state = execution_pb2.State.SUCCEEDED
        self.publish_component_execution(
            execution_info=execution_info, state=state
        )

    def launch(self):
        execution_info = self.run_driver()
        assert execution_info is not None
        assert execution_info.exec_properties is not None

        """
        k8s的labels，这些labels会被volcano inject到各个pods里面。promethues和日志收集器会根据这些label，去追踪此次执行
        所以如果删除这些labels，需要确认
        1. promethues没有依赖
        2. logcollector没有依赖
        3. api-service等服务没有依赖
        所以更改这些labels请务必小心
        """
        workflow_id_prefix = "exe"
        if self._ctx.env == "dev":
            workflow_id_prefix = "exe_dev"

        execution_info.exec_properties["labels"] = {
            "bmlx_pipeline": self._pipeline.meta.name,
            "bmlx_pipeline_version": self._ctx.checksum,
            "bmlx_workflow_id": "{}_{}".format(
                workflow_id_prefix,
                execution_info.exec_properties["pipeline_execution_id"],
            ),
            "bmlx_component": self._component.id,
        }

        execution_info.exec_properties["need_ps"] = self._need_ps()
        execution_info.exec_properties["stage"] = self._stage()

        if not self._ctx.local_mode:
            if "cluster_role" not in execution_info.exec_properties:
                # this means we are in emit stage
                self._run_as_watcher(execution_info=execution_info)
            else:
                self._run_in_cluster(execution_info=execution_info)
        else:
            self._run_local_worker(execution_info=execution_info)

    def cleanup(self, component_execution_state):
        if (
            component_execution_state == execution_pb2.State.SUCCEEDED
            or component_execution_state == execution_pb2.State.UNKNOWN
        ):
            return "ignore"

        self._exec_properties["job_id"] = (
            "bmlx-%s"
            % (
                "%s-%s-%s"
                % (
                    self._driver_args.pipeline_execution.name,
                    self._component.id.replace("_", "-"),
                    str(self._driver_args.pipeline_execution.id),
                )
            )
            .lower()[-30:]
            .lstrip("-")
        )

        # namespace used to clean k8s xdl job
        if not self._exec_properties.get("namespace"):
            self._exec_properties["namespace"] = self._ctx.namespace

        return k8s_job_helper.cleanup_k8s_watcher(
            exec_properties=self._exec_properties,
            ret=False,
            exec_info="cleaned up",
            throwError=False,
        )
