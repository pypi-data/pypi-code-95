import os
import json
import subprocess
import re

from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join

import tornado
from tornado.web import StaticFileHandler


class RouteHandlerMetrics(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        metric_types = ["temperature.gpu",
                        "utilization.gpu",
                        "utilization.memory",
                        "memory.total",
                        "memory.free",
                        "memory.used",
                        "power.draw",
                        "power.max_limit",
                        "pstate"]

        cmd = ["/usr/bin/nvidia-smi",
               "--query-gpu=" + ','.join(metric_types),
               "--format=csv"]

        gpu_metrics = {}

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = bytes.decode(proc.stdout.read()).split('\n')[1].split(',')

        i = 0
        for v in data:
            gpu_metrics[metric_types[i]] = float(re.sub(r"[A-Za-z %]", "", v))
            i += 1

        cmd = ["df", "--output=used,avail,ipcent", "-h", "/home/jovyan"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = bytes.decode(proc.stdout.read()).split('\n')[1]
        data = ' '.join(data.split()).split()

        storage_data = {
            "used": data[0],
            "free": data[1],
            "pct": data[2],
        }

        metrics = {
            "gpu": gpu_metrics,
            "storage": storage_data
        }

        self.finish(json.dumps(metrics))


def setup_handlers(web_app, url_path):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # Prepend the base_url so that it works in a JupyterHub setting
    route_pattern = url_path_join(base_url, url_path, "metrics")
    handlers = [(route_pattern, RouteHandlerMetrics)]
    web_app.add_handlers(host_pattern, handlers)

    # Prepend the base_url so that it works in a JupyterHub setting
    doc_url = url_path_join(base_url, url_path, "public")
    doc_dir = os.getenv(
        "JLAB_SERVER_gpustats_STATIC_DIR",
        os.path.join(os.path.dirname(__file__), "public"),
    )
    handlers = [("{}/(.*)".format(doc_url), StaticFileHandler, {"path": doc_dir})]
    web_app.add_handlers(".*$", handlers)
