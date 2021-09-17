from slai.clients.cli import get_cli_client
from slai.modules.parameters import from_config
from importlib import import_module


def get_model_client(*, model_name, project_name):
    import_path = from_config(
        "MODEL_CLIENT",
        "slai.clients.model.ModelClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)(model_name=model_name)


class ModelClient:
    def __init__(self, *, model_name=None):
        self.cli_client = get_cli_client()

        self.model_name = model_name
        self.model = self.get_model()

    def create_model_artifact(
        self,
        *,
        model_data,
        artifact_type,
        artifact_notebook,
        artifact_requirements,
        model_version_id=None,
        custom_metadata={},
    ):
        if model_version_id is None:
            model_version_id = self.model["model_version_id"]

        model_artifact = self.cli_client.create_model_artifact(
            model_version_id=model_version_id,
            artifact_type=artifact_type,
            artifact_notebook=artifact_notebook,
            artifact_requirements=artifact_requirements,
            custom_metadata=custom_metadata,
        )

        model_artifact = self.cli_client.upload_model_artifact(
            model_artifact_id=model_artifact["id"],
            upload_url=model_artifact["upload_url"],
            model_data=model_data,
        )
        return model_artifact

    def create_model_deployment(
        self,
        *,
        model_artifact_id,
        model_handler_data,
        requirements,
    ):
        model_deployment = self.cli_client.create_model_deployment(
            model_artifact_id=model_artifact_id,
            model_handler_data=model_handler_data,
            requirements=requirements,
        )
        return model_deployment

    def update_model(self, *, key, value):
        model_data = self.get_model()
        model_data[key] = value
        model_data = self.cli_client.update_model(model_data=model_data)
        return model_data

    def get_model(self):
        model_data = self.cli_client.retrieve_model(
            name=self.model_name,
        )
        return model_data

    def get_model_version_by_name(self, *, model_version_name):
        model_version_data = self.cli_client.retrieve_model_version_by_name(
            model_id=self.model["id"],
            model_version_name=model_version_name,
        )
        return model_version_data

    def get_model_version_by_id(self, *, model_version_id):
        model_version_data = self.cli_client.retrieve_model_version_by_id(
            model_version_id=model_version_id,
        )
        return model_version_data

    def get_latest_model_artifact(self, model_version_id=None):
        model_data = self.get_model()

        if model_version_id is None:
            model_version_id = model_data["model_version_id"]

        model_artifact = self.cli_client.retrieve_model_artifact(
            model_version_id=model_version_id,
            model_artifact_id=None,
        )
        return model_artifact

    def list_model_artifacts(self, model_version_id):
        model_artifacts = self.cli_client.retrieve_model_artifact(
            model_version_id=model_version_id,
        )
        return model_artifacts
