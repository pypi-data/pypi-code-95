import io
import base64
import inspect
import json
import importlib.util
import sys

from importlib import import_module
from slai.loaders import base_loader


class TorchLoader(base_loader.BaseLoader):
    @classmethod
    def load_model(cls, model_artifact, deployment_instance_path):
        model_artifact = json.loads(model_artifact)
        model_artifact_model_class_source = base64.b64decode(
            model_artifact["class_source"]
        ).decode("utf-8")

        model_artifact_model_state_dict = base64.b64decode(model_artifact["state_dict"])

        # write model to deployment instance environment
        model_path = f"{deployment_instance_path}/model.py"
        with open(model_path, "w") as f_out:
            f_out.write(model_artifact_model_class_source)

        # dynamically load model module
        spec = importlib.util.spec_from_file_location("model", model_path)
        model_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model_module)
        sys.modules["model"] = model_module

        model_object = None
        for name, obj in inspect.getmembers(model_module):
            if inspect.isclass(obj):
                model_object = obj
                break

        # instantiate model instance
        loaded_model = model_object()

        _torch = import_module("torch")
        model_state_dict_binary = io.BytesIO(model_artifact_model_state_dict)
        _state_dict = _torch.load(model_state_dict_binary)

        loaded_model.load_state_dict(_state_dict)
        loaded_model.eval()

        inference_method_name = None
        return loaded_model, inference_method_name
