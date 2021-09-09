from dagster_cloud.execution.watchful_run_launcher.base import WatchfulRunLauncher
from dagster_docker import DockerRunLauncher


class WatchfulDockerRunLauncher(DockerRunLauncher, WatchfulRunLauncher):
    def check_run_health(self, _run_id):
        pass
