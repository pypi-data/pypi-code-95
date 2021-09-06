from setuptools import setup, find_packages


setup(
    name="infinstor-mlflow-plugin",
    version="2.0.13",
    description="InfinStor plugin for MLflow",
    packages=find_packages(),
    # Require MLflow as a dependency of the plugin, so that plugin users can simply install
    # the plugin & then immediately use it with MLflow
    install_requires=["mlflow"],
    entry_points={
        # Define a Tracking Store plugin for tracking URIs with scheme 'infinstor'
        "mlflow.tracking_store": "infinstor=infinstor_mlflow_plugin.cognito_auth_rest_store:CognitoAuthenticatedRestStore",
        # Define a ArtifactRepository plugin for artifact URIs with scheme 'infinstor'
        "mlflow.artifact_repository":
            "infinstor=infinstor_mlflow_plugin.infinstor_artifact:InfinStorArtifactRepository",
        # Define a RunContextProvider plugin. The entry point name for run context providers
        # is not used, and so is set to the string "unused" here
        "mlflow.run_context_provider":
            "unused=infinstor_mlflow_plugin.run_context_provider:PluginRunContextProvider",
        # Define a Model Registry Store plugin for tracking URIs with scheme 'infinstor'
        "mlflow.model_registry_store":
            "infinstor=infinstor_mlflow_plugin.cognito_auth_rest_store:CognitoAuthenticatedRestStore",
        # Define a MLflow Project Backend plugin called 'infinstor-backend'
        "mlflow.project_backend":
            "infinstor-backend=infinstor_mlflow_plugin.infinstor_backend:PluginInfinStorProjectBackend",
        # Define a MLflow model deployment plugin for target 'faketarget'
        "mlflow.deployments": "infinstor=infinstor_mlflow_plugin.infinstor_deployment_plugin",
    },
)
