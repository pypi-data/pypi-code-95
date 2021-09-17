import io
import base64
import inspect
import json
import pickle

from importlib import import_module
from slai.modules.requirements import generate_requirements_from_runtime


class ValidModelFrameworks:
    Torch = "TORCH"
    Sklearn = "SKLEARN"


class ModelSaver:
    @staticmethod
    def _clean_model_source(model_source):
        model_source_lines = model_source.split("\n")
        cleaned_model_source_lines = []

        indentation_to_remove = 0
        class_def_found = False
        for line in model_source_lines:
            if "class" in line and not class_def_found:
                class_def_found = True

                for c in line:
                    if c != " ":
                        break
                    indentation_to_remove += 1

            cleaned_model_source_lines.append(line[indentation_to_remove:])

        return cleaned_model_source_lines

    @staticmethod
    def _add_import_lines(*, cleaned_model_source, imports=[]):
        for _import in imports:
            cleaned_model_source.insert(0, _import)

        return cleaned_model_source

    @staticmethod
    def save_pytorch(model):
        _torch = import_module("torch")
        model_state_dict_binary = io.BytesIO()
        model_class_source = inspect.getsource(model.__class__)
        _torch.save(model.state_dict(), model_state_dict_binary)

        cleaned_model_source_lines = ModelSaver._clean_model_source(model_class_source)
        requirements, import_lines = generate_requirements_from_runtime(
            module_name="trainer"
        )
        cleaned_model_source_lines = ModelSaver._add_import_lines(
            cleaned_model_source=cleaned_model_source_lines, imports=import_lines
        )
        cleaned_model_source = "\n".join(cleaned_model_source_lines)

        # model class source
        model_class_source_binary_base64 = base64.b64encode(
            cleaned_model_source.encode("utf-8")
        ).decode()

        # model parameters
        model_state_dict_binary_base64 = base64.b64encode(
            model_state_dict_binary.getvalue()
        ).decode()

        model_artifact = {
            "state_dict": model_state_dict_binary_base64,
            "class_source": model_class_source_binary_base64,
        }

        model_artifact_base_64 = base64.b64encode(
            json.dumps(model_artifact).encode("utf-8")
        ).decode()

        return model_artifact_base_64, requirements

    @staticmethod
    def save_sklearn(model):
        model_binary = pickle.dumps(model)
        model_artifact_base64 = base64.b64encode(model_binary).decode()
        requirements, import_lines = generate_requirements_from_runtime(
            module_name="trainer"
        )
        return model_artifact_base64, requirements

    @staticmethod
    def save_fastai(model):
        return None

    @staticmethod
    def save_keras(model):
        # _keras = import_module("keras")
        # model_binary = io.BytesIO()
        # _keras.save(model, model_binary)
        # model_binary_base64 = base64.b64encode(model_binary.getvalue())
        # return model_binary_base64

        return None

    @staticmethod
    def save_tf(model):
        return None
