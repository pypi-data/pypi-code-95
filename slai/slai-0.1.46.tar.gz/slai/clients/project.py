import yaml

from slai.clients.cli import get_cli_client
from slai.modules.parameters import from_config

from pathlib import Path
from importlib import import_module


def get_project_client(*, project_name):
    import_path = from_config(
        "PROJECT_CLIENT",
        "slai.clients.project.ProjectClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])

    return getattr(import_module(path), class_)(project_name=project_name)


class ProjectClient:
    def __init__(self, *, project_name=None):
        self.project_name = project_name
        self.cli_client = get_cli_client()

    def list_models(self):
        """List models in a slai project."""

        project = self.get_project()
        return project["models"]

    def _load_config_from_disk(self):
        cwd = Path.cwd()
        config = None

        local_config_path = f"{cwd}/.slai/config.yml"

        with open(local_config_path, "r") as f_in:
            try:
                config = yaml.safe_load(f_in)
            except yaml.YAMLError:
                pass

        return config

    def get_project_name(self):
        """Retrieve project name."""
        if self.project_name is None:
            config = self._load_config_from_disk()
            return config["project_name"]

        return self.project_name

    def get_project(self):
        """Retrieve project configuration values."""
        project = self.cli_client.retrieve_project(project_name=self.get_project_name())

        return project
