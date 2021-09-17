class BaseLoader:
    @classmethod
    def load_model(cls, *, model_artifact, deployment_instance_path):
        raise NotImplementedError
