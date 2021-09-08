# -*- coding: utf-8 -*-
import os
import sys
import threading

import ray

from outflow.core.backends.backend import Backend as DefaultBackend
from outflow.core.logging import logger
from outflow.core.logging import LogRecordSocketReceiver
from outflow.core.pipeline import config, context

from outflow.ray.backends import SlurmRayBackend
from outflow.ray.backends import LocalRayBackend


class Backend(DefaultBackend):
    def __init__(self):
        super().__init__()
        self.tcpserver = LogRecordSocketReceiver()
        self.init_tcp_socket_receiver()
        # needed when plugins are not installed but only in python path
        os.environ["PYTHONPATH"] = ":".join(sys.path)

        self.name = "ray"
        cluster_type = config["ray"]["cluster_type"]
        if cluster_type == "local":
            self.backend = LocalRayBackend()
        elif cluster_type == "slurm":
            self.backend = SlurmRayBackend()
        else:
            raise AttributeError(f"Unknown cluster type : {cluster_type}")

    def run(self, task_list):
        return self.backend.run(task_list)

    def init_tcp_socket_receiver(self):
        logger.debug("About to start TCP server...")

        self.server_thread = threading.Thread(target=self.tcpserver.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        _, context.logger_port = self.tcpserver.server_address

    def clean(self):
        logger.debug("Cleaning ray backend")
        self.tcpserver.shutdown()
        self.backend.clean()
        ray.shutdown()
