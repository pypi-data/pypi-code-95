# -*- coding: utf-8 -*-
import multiprocessing
import platform
import subprocess
import sys
import tempfile
import time

import ray

from outflow.core.logging import logger
from outflow.core.pipeline import config, context, get_pipeline_states
from outflow.ray.remote_run import remote_run
from outflow.ray.run_main_workflow import run_main_workflow


class SlurmRayBackend:
    def __init__(self):
        self._job_ids_queue = None
        self.num_ray_nodes = 0
        self.head_node_params = dict()
        self.workers_params = dict()
        self.setup_cluster()
        self.stop_event = None
        self.sbatch_proc = None

        if self.num_ray_nodes < 1:
            raise AttributeError("Number of ray nodes must be greater than 0")

    @property
    def job_ids_queue(self):
        if self._job_ids_queue is None:
            self._job_ids_queue = multiprocessing.Queue()

        return self._job_ids_queue

    @staticmethod
    def launch_ray_nodes(
        workers_params: dict,
        num_ray_nodes: int,
        job_ids_q: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
    ):
        # subprocess local imports
        from outflow.core.logging import logger
        from simple_slurm import Slurm

        # redirect logs from subprocess to logger
        # sys.stdout = StreamToLogger(logger)

        ray_node = Slurm(
            cpus_per_task=workers_params["cpu_per_node"],
            mem=workers_params["mem_per_node"],
            job_name="ray_node",
        )

        for index in range(num_ray_nodes):
            if index > 0:
                time.sleep(3)

            if stop_event.is_set():
                return

            python_path = sys.executable

            sbatch = (
                "srun {python_path} -m ray.scripts.scripts start --block --address='{redis_address}' "
                "--num-cpus={cpu_per_node} "
                "--redis-password='{_redis_password}'".format(
                    python_path=python_path,
                    **workers_params,
                )
            )
            logger.debug(f"calling sbatch with : {sbatch}")

            job_ids_q.put(ray_node.sbatch(sbatch))

    def setup_cluster(self):
        """
        Starts the ray head server, the main worker and sbatch the ray nodes
        """
        import ray

        # shutdown ray to avoid re-init issues
        ray.shutdown()

        # launch ray head server and main worker

        cluster_config = config.get("ray", {})

        if "mem_per_node" in cluster_config:
            # --- Binary ---
            # 1 MiB = 1024 * 1024
            # 1 MiB = 2^20 bytes = 1 048 576 bytes = 1024 kibibytes
            # 1024 MiB = 1 gibibyte (GiB)

            # --- Decimal ---
            # 1 MB = 1^3 kB = 1 000 000 bytes

            self.workers_params.update({"mem_per_node": cluster_config["mem_per_node"]})
        if "cpu_per_node" in cluster_config:
            self.workers_params.update({"cpu_per_node": cluster_config["cpu_per_node"]})

        self.workers_params.update(
            {"_redis_password": cluster_config.get("redis_password", "outflow")}
        )
        self.head_node_params.update(
            {"_redis_password": self.workers_params["_redis_password"]}
        )

        # FIXME: fix ray to support parallel job on windows
        if platform.system() == "Windows" or config["local_mode"]:
            self.head_node_params.update({"local_mode": True})
        else:
            self.head_node_params.update({"num_cpus": 0})

        temp_dir = tempfile.mkdtemp(prefix="outflow_ray_")
        self.head_node_params.update({"_temp_dir": temp_dir})

        ray_info = ray.init(
            **self.head_node_params,
            object_store_memory=1000000000
            # log_to_driver=False,
        )

        self.workers_params.update({"redis_address": ray_info["redis_address"]})
        context.redis_address = ray_info["redis_address"].split(":")[0]

        self.num_ray_nodes = cluster_config.get("num_ray_nodes", 0)

    def run(self, task_list=None):
        if task_list is None:
            task_list = []
        main_workflow_result = remote_run.remote(
            run_main_workflow,
            pipeline_states=get_pipeline_states(),
            task_list=task_list,
        )

        self.stop_event = multiprocessing.Event()
        logger.info(f"Launching {self.num_ray_nodes} ray nodes")

        self.sbatch_proc = multiprocessing.Process(
            target=self.launch_ray_nodes,
            args=(
                self.workers_params,
                self.num_ray_nodes,
                self.job_ids_queue,
                self.stop_event,
            ),
        )
        self.sbatch_proc.start()

        # call to launch pipeline execution with ray
        result = ray.get(main_workflow_result)
        return result

    def clean(self):

        if self.stop_event:
            self.stop_event.set()
        if self.sbatch_proc:
            self.sbatch_proc.join()

        while not self.job_ids_queue.empty():
            slurm_id = self.job_ids_queue.get()
            logger.debug("cancelling slurm id {id}".format(id=slurm_id))
            subprocess.run(["scancel", str(slurm_id)])
