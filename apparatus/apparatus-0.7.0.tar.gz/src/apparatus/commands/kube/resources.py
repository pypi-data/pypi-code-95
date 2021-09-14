from typing import List

from clicasso import Slug
import kubernetes
from kubernetes.client.api_client import ApiClient
from tabulate import tabulate

from apparatus.config import Config
from apparatus.core import Command
from apparatus.utils import maybe


class Resources(Command):
    # pylint: disable=no-member
    @classmethod
    def slug(cls) -> Slug:
        return ("kube", "resources")

    namespace: str

    def run(self, config: Config, remainder: List[str]) -> None:
        records = self._fetch_records(config)
        print(tabulate(records, headers="keys"))

    def _fetch_records(self, config: Config):
        def it(v1):
            result = v1.list_namespaced_pod(namespace=self.namespace)
            for pod in result.items:
                for container in pod.spec.containers:
                    yield {
                        "pod": pod.metadata.name,
                        "container": container.name,
                        "limits.memory": maybe(container.resources.limits, "memory"),
                        "limits.cpu": maybe(container.resources.limits, "cpu"),
                        "requests.memory": maybe(container.resources.requests, "memory"),
                        "requests.cpu": maybe(container.resources.requests, "cpu"),
                    }

        kubernetes.config.load_kube_config(config.kubernetes.config)
        with ApiClient() as api:
            v1 = kubernetes.client.CoreV1Api(api)
            return list(it(v1))
