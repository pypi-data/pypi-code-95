import pickle

from slai.loaders import base_loader


class SklearnLoader(base_loader.BaseLoader):
    @classmethod
    def load_model(cls, model_artifact, deployment_instance_path):
        model_artifact_model_binary = model_artifact

        # write model to deployment instance environment
        model_path = f"{deployment_instance_path}/model"
        with open(model_path, "wb") as f_out:
            f_out.write(model_artifact_model_binary)

        loaded_model = pickle.loads(model_artifact_model_binary)

        inference_method_name = "predict"
        return loaded_model, inference_method_name
