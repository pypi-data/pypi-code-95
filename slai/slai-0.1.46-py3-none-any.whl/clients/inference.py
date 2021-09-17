import requests

from slai.modules.parameters import from_config
from slai.config import get_api_base_url
from slai.modules.runtime import detect_runtime, detect_credentials
from slai.clients.model import get_model_client

from requests.auth import HTTPBasicAuth
from importlib import import_module


REQUESTS_TIMEOUT = 15


def get_inference_client(*, model_name, project_name, model_version_name):
    import_path = from_config(
        "MODEL_INFERENCE_CLIENT",
        "slai.clients.inference.ModelInferenceClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])

    return getattr(import_module(path), class_)(
        model_name=model_name,
        project_name=project_name,
        model_version_name=model_version_name,
    )


class ModelInferenceClient:
    BASE_URL = get_api_base_url()

    def __init__(self, *, model_name, project_name, model_version_name=None):
        self.runtime = detect_runtime()
        credentials = detect_credentials(runtime=self.runtime)
        self.client_id = credentials["client_id"]
        self.client_secret = credentials["client_secret"]

        self.model_name = model_name
        self.project_name = project_name
        self.model_version_name = model_version_name

        self._load_model()

    def _load_model(self):
        self.model_client = get_model_client(
            model_name=self.model_name, project_name=self.project_name
        )
        self.model = self.model_client.get_model()

        if self.model_version_name is not None:
            self.model_version = self.model_client.get_model_version_by_name(
                model_version_name=self.model_version_name
            )
            self.model_version_id = self.model_version["id"]
        else:
            self.model_version_id = None

    def call(self, payload):
        body = {
            "model_id": self.model["id"],
            "model_version_id": self.model_version_id,
            "payload": payload,
        }

        if body.get("model_version_id") is None:
            del body["model_version_id"]

        res = requests.post(
            f"{self.BASE_URL}/model/call",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def info(self):
        body = {
            "model_id": self.model["id"],
            "model_version_id": self.model_version_id,
        }

        if body.get("model_version_id") is None:
            del body["model_version_id"]

        res = requests.post(
            f"{self.BASE_URL}/model/info",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()
