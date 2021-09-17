import requests

from requests.auth import HTTPBasicAuth
from importlib import import_module

from slai.config import get_api_base_url
from slai.modules.parameters import from_config
from slai.modules.runtime import detect_runtime, detect_credentials

REQUESTS_TIMEOUT = 15


def get_cli_client(client_id=None, client_secret=None):
    import_path = from_config(
        "CLI_CLIENT",
        "slai.clients.cli.SlaiCliClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)(
        client_id=client_id, client_secret=client_secret
    )


class SlaiCliClient:
    BASE_URL = get_api_base_url()

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        user_agent_header="SlaiCli smartshare/0.1.0",
    ):
        self.runtime = detect_runtime()

        if client_id is None or client_secret is None:
            credentials = detect_credentials(runtime=self.runtime)
            self.client_id = credentials["client_id"]
            self.client_secret = credentials["client_secret"]
        else:
            self.client_id = client_id
            self.client_secret = client_secret

        self.user_agent_header = user_agent_header

    def create_model(self, *, project_name, name):
        body = {"action": "create", "name": name, "project_name": project_name}

        res = requests.post(
            f"{self.BASE_URL}/cli/model",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model(self, *, project_name, name):
        body = {
            "action": "retrieve",
            "name": name,
            "project_name": project_name,
        }

        body = {k: v for k, v in body.items() if v is not None}

        res = requests.post(
            f"{self.BASE_URL}/cli/model",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def create_model_version(self, *, model_id, name):
        body = {"action": "create", "model_id": model_id, "name": name}

        res = requests.post(
            f"{self.BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model_version_by_name(self, *, model_id, model_version_name):
        body = {
            "action": "retrieve",
            "model_id": model_id,
            "model_version_name": model_version_name,
        }

        res = requests.post(
            f"{self.BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model_version_by_id(self, *, model_version_id):
        body = {
            "action": "retrieve",
            "model_version_id": model_version_id,
        }

        res = requests.post(
            f"{self.BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def list_model_versions(self, *, model_id):
        body = {"action": "list", "model_id": model_id}

        res = requests.post(
            f"{self.BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def list_model_artifacts(self, *, model_version_id):
        body = {
            "action": "list",
            "model_version_id": model_version_id,
        }

        res = requests.post(
            f"{self.BASE_URL}/cli/model-artifact",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model_artifact(self, *, model_version_id, model_artifact_id):
        body = {
            "action": "retrieve",
            "model_version_id": model_version_id,
            "model_artifact_id": model_artifact_id,
        }

        body = {k: v for k, v in body.items() if v is not None}

        res = requests.post(
            f"{self.BASE_URL}/cli/model-artifact",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def create_model_artifact(
        self,
        *,
        model_version_id,
        artifact_type,
        artifact_notebook,
        artifact_requirements,
        custom_metadata,
    ):
        body = {
            "action": "create",
            "model_version_id": model_version_id,
            "artifact_type": artifact_type,
            "artifact_notebook": artifact_notebook,
            "artifact_requirements": artifact_requirements,
            "custom_metadata": custom_metadata,
        }

        res = requests.post(
            f"{self.BASE_URL}/cli/model-artifact",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def upload_model_artifact(
        self,
        *,
        model_artifact_id,
        upload_url,
        model_data,
    ):
        body = {
            "action": "update",
            "model_artifact_id": model_artifact_id,
            "artifact_verified": True,
        }

        # First upload the artifact
        res = requests.put(
            f"{upload_url}",
            data=model_data,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()

        # Then update the artifact state
        res = requests.post(
            f"{self.BASE_URL}/cli/model-artifact",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def create_model_deployment(
        self,
        *,
        model_artifact_id,
        model_handler_data,
        requirements,
    ):
        body = {
            "action": "create",
            "model_artifact_id": model_artifact_id,
            "model_handler_data": model_handler_data,
            "requirements": requirements,
        }

        res = requests.post(
            f"{self.BASE_URL}/cli/deploy",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def update_model(self, *, model_data):
        body = model_data
        body["action"] = "update"

        # TODO: refactor this, this is weird
        model_id = body["id"]
        body["model_id"] = model_id

        del body["created"]
        del body["updated"]

        body = {k: v for k, v in body.items() if v is not None}
        res = requests.post(
            f"{self.BASE_URL}/cli/model",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def get_user(self):
        body = {"action": "retrieve"}

        res = requests.post(
            f"{self.BASE_URL}/cli/user",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def update_user(self, email=None, gauth_creds=None):
        body = {"action": "update", "email": email, "gauth_creds": gauth_creds}

        body = {k: v for k, v in body.items() if v is not None}
        res = requests.post(
            f"{self.BASE_URL}/cli/user",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def get_cli_version(self):
        body = {}
        res = requests.post(
            f"{self.BASE_URL}/cli/cli-version",
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_dataset(self, *, name, version, public, create):
        body = {
            "action": "retrieve",
            "name": name,
            "public": public,
            "version": version,
            "create": create,
        }

        body = {k: v for k, v in body.items() if v is not None}
        res = requests.post(
            f"{self.BASE_URL}/cli/dataset",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def update_dataset(self, *, name, public, diff_table):
        body = {
            "action": "update",
            "name": name,
            "public": public,
            "diff_table": diff_table,
        }

        body = {k: v for k, v in body.items() if v is not None}
        res = requests.post(
            f"{self.BASE_URL}/cli/dataset",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()
