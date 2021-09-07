# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains utilities for use by the deployment client"""
import json
import logging
import os
import yaml
from azureml.core import Environment as AzureEnvironment
from azureml.core.model import InferenceConfig
from azureml.exceptions import WebserviceException
from azureml.core.webservice import LocalWebservice
from azureml._model_management._constants import ACI_WEBSERVICE_TYPE, AKS_WEBSERVICE_TYPE, AKS_ENDPOINT_TYPE,\
    AKS_ENDPOINT_CREATE_VERSION, AKS_ENDPOINT_UPDATE_VERSION, AKS_ENDPOINT_DELETE_VERSION
from mlflow import get_tracking_uri, get_registry_uri
from mlflow import register_model as mlflow_register_model
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from mlflow.utils.file_utils import _copy_file_or_tree
from mlflow.version import VERSION as mlflow_version


_logger = logging.getLogger(__name__)


def file_stream_to_object(file_stream):
    """
    Take a YAML or JSON file_stream and return the dictionary object.

    :param file_stream: File stream from with open(file) as file_stream
    :type file_stream:
    :return: File dictionary
    :rtype: dict
    """
    file_data = file_stream.read()

    try:
        return yaml.safe_load(file_data)
    except Exception as ex:
        pass

    try:
        return json.loads(file_data)
    except Exception as ex:
        raise WebserviceException('Error while parsing file. Must be valid JSON or YAML file.', content=ex)


def handle_model_uri(model_uri, service_name):
    """
    Handle the various types of model uris we could receive.

    :param model_uri:
    :type model_uri: str
    :param service_name:
    :type service_name: str
    :return:
    :rtype:
    """
    client = MlflowClient()

    if model_uri.startswith("models:/"):
        model_name = model_uri.split("/")[-2]
        model_stage_or_version = model_uri.split("/")[-1]
        if model_stage_or_version in client.get_model_version_stages(None, None):
            # TODO: Add exception handling for no models found with specified stage
            model_version = client.get_latest_versions(model_name, [model_stage_or_version])[0].version
        else:
            model_version = model_stage_or_version
    elif (model_uri.startswith("runs:/") or model_uri.startswith("file://")) \
            and get_tracking_uri().startswith("azureml") and get_registry_uri().startswith("azureml"):
        # We will register the model for the user
        model_name = service_name + "-model"
        mlflow_model = mlflow_register_model(model_uri, model_name)
        model_version = mlflow_model.version

        _logger.info(
            "Registered an Azure Model with name: `%s` and version: `%s`",
            mlflow_model.name,
            mlflow_model.version,
        )
    else:
        raise MlflowException("Unsupported model uri provided, or tracking or registry uris are not set to "
                              "an AzureML uri.")

    return model_name, model_version


def create_inference_config(tmp_dir, model_name, model_version, service_name):
    """
    Create the InferenceConfig object which will be used to deploy.

    :param tmp_dir:
    :type tmp_dir:
    :param model_name:
    :type model_name:
    :param model_version:
    :type model_version:
    :param service_name:
    :type service_name:
    :return:
    :rtype:
    """
    try:
        from mlflow import pyfunc
        from mlflow.models import Model

        from mlflow.models.model import MLMODEL_FILE_NAME

        import pandas
    except ImportError as exception:
        raise get_deployments_import_error(exception)

    absolute_model_path = _download_artifact_from_uri('models:/{}/{}'.format(model_name, model_version))
    model_folder = absolute_model_path.split(os.path.sep)[-1]
    model_directory_path = tmp_dir.path("model")
    tmp_model_path = os.path.join(
        model_directory_path,
        _copy_file_or_tree(src=absolute_model_path, dst=model_directory_path),
    )

    # Create environment
    env_name = service_name + "-env"
    env_name = env_name[:32]
    mlflow_model = Model.load(os.path.join(absolute_model_path, MLMODEL_FILE_NAME))

    model_pyfunc_conf = load_pyfunc_conf(mlflow_model)
    if pyfunc.ENV in model_pyfunc_conf:
        environment = AzureEnvironment.from_conda_specification(
            env_name,
            os.path.join(tmp_model_path, model_pyfunc_conf[pyfunc.ENV])
        )
    else:
        raise MlflowException('Error, no environment information provided with model')

    sample_input_df = None
    sample_output_df = None

    # Leaving this here, commented out for now. The issue is that our swagger handling doesn't work with OpenAPI 3.
    # This runs into issues because a pandas dataframe in a split orient (the default) can have arrays of mixed
    # types, which isn't supported in OpenAPI 2. So for now, we will only use the empty signature to generate
    # swagger, and when we've updated our swagger handling to support OpenAPI 3 we can add this back in.
    """
    if mlflow_model.saved_input_example_info:
        sample_input_file_path = os.path.join(absolute_model_path,
                                              mlflow_model.saved_input_example_info['artifact_path'])
        with open(sample_input_file_path, 'r') as sample_input_file:
            if mlflow_model.saved_input_example_info['type'] == 'dataframe':
                sample_input_df = pandas.read_json(sample_input_file,
                                                   orient=mlflow_model.saved_input_example_info['pandas_orient'])
            else:
                raise MlflowException('Sample model input must be of type "dataframe"')
    """

    if mlflow_model.signature:
        if mlflow_model.signature.inputs and sample_input_df is None:
            # 'is None' check is necessary because dataframes don't like being used as truth values
            columns = mlflow_model.signature.inputs.column_names()
            types = mlflow_model.signature.inputs.pandas_types()
            schema = {}
            for c, t in zip(columns, types):
                schema[c] = t
            df = pandas.DataFrame(columns=columns)
            sample_input_df = df.astype(dtype=schema)
        if mlflow_model.signature.outputs and sample_output_df is None:
            columns = mlflow_model.signature.outputs.column_names()
            types = mlflow_model.signature.outputs.pandas_types()
            schema = {}
            for c, t in zip(columns, types):
                schema[c] = t
            df = pandas.DataFrame(columns=columns)
            sample_output_df = df.astype(dtype=schema)

    # Create execution script
    execution_script_path = tmp_dir.path("execution_script.py")
    create_execution_script(execution_script_path, model_folder, sample_input_df, sample_output_df)

    # Add inference dependencies
    environment.python.conda_dependencies.add_pip_package("mlflow=={}".format(mlflow_version))
    environment.python.conda_dependencies.add_pip_package("inference-schema>=1.2.0")
    environment.python.conda_dependencies.add_pip_package("azureml-model-management-sdk==1.0.1b6.post1")
    environment.python.conda_dependencies.add_pip_package("flask==1.0.3")
    environment.python.conda_dependencies.add_pip_package("gunicorn==19.9.0")
    environment.python.conda_dependencies.add_pip_package("applicationinsights>=0.11.7")
    environment.python.conda_dependencies.add_pip_package("werkzeug>=0.16.1,<=1.0.1")

    # Create InferenceConfig
    inference_config = InferenceConfig(entry_script=execution_script_path, environment=environment)

    return inference_config


def create_execution_script(output_path, model_folder, sample_input_df, sample_output_df):
    """
    Create the execution script which will be used to deploy.

    Creates an Azure-compatible execution script (entry point) for a model server backed by
    the specified model. This script is created as a temporary file in the current working
    directory.

    :param output_path: The path where the execution script will be written.
    :param model_folder: The folder containing the model files
    :param model_version: The version of the model to load for inference
    :param sample_input_df: A sample input dataframe, if we could parse one from the MLFlow Model object
    :param sample_output_df: A sample output dataframe, if we could parse one from the MLFlow Model object
    :return: A reference to the temporary file containing the execution script.
    """
    try:
        from numpy import dtype
        from pandas import StringDtype
        string_d_type_imported = True
    except ImportError:
        string_d_type_imported = False
    INIT_SRC = """\
import json
import os
import pandas as pd

from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType
from inference_schema.schema_decorators import input_schema, output_schema
from mlflow.pyfunc import load_model
from mlflow.pyfunc.scoring_server import parse_json_input, _get_jsonable_obj
from numpy import dtype

def init():
    global model

    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), '{model_folder}')
    model = load_model(model_path)
""".format(model_folder=model_folder)
    RUN_WITH_INFERENCE_SCHEMA_SRC = """\
def run(input_data):
    return _get_jsonable_obj(model.predict(input_data), pandas_orient="records")
"""
    RUN_WITHOUT_INFERENCE_SCHEMA_SRC = """\
def run(input_data):
    input_data = json.loads(input_data)
    input_data = input_data['input_data']
    input_df = parse_json_input(json_input=json.dumps(input_data), orient="split")
    return _get_jsonable_obj(model.predict(input_df), pandas_orient="records")
"""
    INPUT_DECORATOR_STR = "@input_schema('input_data', PandasParameterType(sample_input, orient='split'))"
    OUTPUT_DECORATOR_STR = "@output_schema(PandasParameterType(sample_output, orient='records'))"
    SAMPLE_INPUT_STR = "sample_input = pd.read_json('{input_format_str}', orient='split', dtype={input_df_dtypes})"
    SAMPLE_OUTPUT_STR = \
        "sample_output = pd.read_json('{output_format_str}', orient='records', dtype={output_df_dtypes})"

    if sample_output_df is not None:
        sample_output_dtypes_dict = sample_output_df.dtypes.to_dict()
        # Pandas has added an extension dtype for strings. However, the string repr for them can't be used in a format
        # string, and read_json still handles it as a dtype object anyway. So doing this conversion loses nothing.
        if string_d_type_imported:
            for column_name, column_type in sample_output_dtypes_dict.items():
                if type(column_type) is StringDtype:
                    sample_output_dtypes_dict[column_name] = dtype('O')

        # Append the sample output to init and prepend the output decorator to the run function
        SAMPLE_OUTPUT_STR = SAMPLE_OUTPUT_STR.format(output_format_str=sample_output_df.to_json(orient='records'),
                                                     output_df_dtypes=sample_output_dtypes_dict)
        INIT_SRC = INIT_SRC + "\n" + SAMPLE_OUTPUT_STR
        RUN_WITH_INFERENCE_SCHEMA_SRC = OUTPUT_DECORATOR_STR + "\n" + RUN_WITH_INFERENCE_SCHEMA_SRC
    if sample_input_df is not None:
        sample_input_dtypes_dict = sample_input_df.dtypes.to_dict()
        # Pandas has added an extension dtype for strings. However, the string repr for them can't be used in a format
        # string, and read_json still handles it as a dtype object anyway. So doing this conversion loses nothing.
        if string_d_type_imported:
            for column_name, column_type in sample_input_dtypes_dict.items():
                if type(column_type) is StringDtype:
                    sample_input_dtypes_dict[column_name] = dtype('O')

        # Append the sample input to init and prepend the input decorator to the run function
        SAMPLE_INPUT_STR = SAMPLE_INPUT_STR.format(input_format_str=sample_input_df.to_json(orient='split'),
                                                   input_df_dtypes=sample_input_dtypes_dict)
        INIT_SRC = INIT_SRC + "\n" + SAMPLE_INPUT_STR
        RUN_WITH_INFERENCE_SCHEMA_SRC = INPUT_DECORATOR_STR + "\n" + RUN_WITH_INFERENCE_SCHEMA_SRC

    if sample_input_df is not None or sample_output_df is not None:
        # Combine the init which contains appended sample line/s to the run function with prepended decorator/s
        execution_script_text = INIT_SRC + "\n\n" + RUN_WITH_INFERENCE_SCHEMA_SRC
    else:
        # No fancy handling, just our basic init and run without samples/decorators
        execution_script_text = INIT_SRC + "\n" + RUN_WITHOUT_INFERENCE_SCHEMA_SRC

    with open(output_path, "w") as f:
        f.write(execution_script_text)


def load_pyfunc_conf(model):
    """
    Load the pyfunc flavor configuration for the passed in model.

    Loads the `python_function` flavor configuration for the specified model or throws an exception
    if the model does not contain the `python_function` flavor.

    :param model_path: The MLFlow Model object to retrieve the pyfunc conf from
    :return: The model's `python_function` flavor configuration.
    """
    try:
        from mlflow import pyfunc
    except ImportError as exception:
        raise get_deployments_import_error(exception)

    if pyfunc.FLAVOR_NAME not in model.flavors:
        raise MlflowException(
            message=(
                "The specified model does not contain the `python_function` flavor. This "
                "flavor is currently required for model deployment."
            )
        )
    return model.flavors[pyfunc.FLAVOR_NAME]


def submit_update_call(service, models, inference_config, deploy_config, aks_endpoint_version_config):
    if service._webservice_type.lower() == ACI_WEBSERVICE_TYPE.lower():
        # aci update
        service.update(auth_enabled=deploy_config.auth_enabled,
                       ssl_enabled=deploy_config.ssl_enabled,
                       ssl_cert_pem_file=deploy_config.ssl_cert_pem_file,
                       ssl_key_pem_file=deploy_config.ssl_key_pem_file,
                       ssl_cname=deploy_config.ssl_cname,
                       enable_app_insights=deploy_config.enable_app_insights,
                       models=models,
                       inference_config=inference_config)
    elif service._webservice_type.lower() == AKS_WEBSERVICE_TYPE.lower():
        # aks update
        service.update(autoscale_enabled=deploy_config.autoscale_enabled,
                       autoscale_min_replicas=deploy_config.autoscale_min_replicas,
                       autoscale_max_replicas=deploy_config.autoscale_max_replicas,
                       autoscale_refresh_seconds=deploy_config.autoscale_refresh_seconds,
                       autoscale_target_utilization=deploy_config.autoscale_target_utilization,
                       collect_model_data=deploy_config.collect_model_data,
                       auth_enabled=deploy_config.auth_enabled,
                       cpu_cores=deploy_config.cpu_cores,
                       memory_gb=deploy_config.memory_gb,
                       enable_app_insights=deploy_config.enable_app_insights,
                       scoring_timeout_ms=deploy_config.scoring_timeout_ms,
                       replica_max_concurrent_requests=deploy_config.replica_max_concurrent_requests,
                       max_request_wait_time=deploy_config.max_request_wait_time,
                       num_replicas=deploy_config.num_replicas,
                       token_auth_enabled=deploy_config.token_auth_enabled,
                       models=models, inference_config=inference_config,
                       cpu_cores_limit=deploy_config.cpu_cores_limit,
                       memory_gb_limit=deploy_config.memory_gb_limit)
    elif service._webservice_type.lower() == AKS_ENDPOINT_TYPE.lower():
        # aksendpoint update
        if aks_endpoint_version_config and aks_endpoint_version_config['version_operation_type'] is not None:
            version_operation_type = aks_endpoint_version_config['version_operation_type'].lower()
            is_default = aks_endpoint_version_config['is_default']
            is_control_version_type = aks_endpoint_version_config['is_control_version']

            if version_operation_type == AKS_ENDPOINT_CREATE_VERSION.lower():
                service.create_version(
                    version_name=deploy_config.version_name,
                    autoscale_enabled=deploy_config.autoscale_enabled,
                    autoscale_min_replicas=deploy_config.autoscale_min_replicas,
                    autoscale_max_replicas=deploy_config.autoscale_max_replicas,
                    autoscale_refresh_seconds=deploy_config.autoscale_refresh_seconds,
                    autoscale_target_utilization=deploy_config.autoscale_target_utilization,
                    collect_model_data=deploy_config.collect_model_data,
                    cpu_cores=deploy_config.cpu_cores,
                    memory_gb=deploy_config.memory_gb,
                    scoring_timeout_ms=deploy_config.scoring_timeout_ms,
                    replica_max_concurrent_requests=deploy_config.replica_max_concurrent_requests,
                    max_request_wait_time=deploy_config.max_request_wait_time,
                    num_replicas=deploy_config.num_replicas,
                    models=models, inference_config=inference_config,
                    gpu_cores=deploy_config.gpu_cores,
                    period_seconds=deploy_config.period_seconds,
                    initial_delay_seconds=deploy_config.initial_delay_seconds,
                    timeout_seconds=deploy_config.timeout_seconds,
                    success_threshold=deploy_config.success_threshold,
                    failure_threshold=deploy_config.failure_threshold,
                    traffic_percentile=deploy_config.traffic_percentile, is_default=is_default,
                    is_control_version_type=is_control_version_type,
                    cpu_cores_limit=deploy_config.cpu_cores_limit,
                    memory_gb_limit=deploy_config.memory_gb_limit)
            elif version_operation_type == AKS_ENDPOINT_DELETE_VERSION.lower():
                service.delete_version(version_name=deploy_config.version_name)
            elif version_operation_type == AKS_ENDPOINT_UPDATE_VERSION.lower():
                service.update_version(
                    version_name=deploy_config.version_name,
                    autoscale_enabled=deploy_config.autoscale_enabled,
                    autoscale_min_replicas=deploy_config.autoscale_min_replicas,
                    autoscale_max_replicas=deploy_config.autoscale_max_replicas,
                    autoscale_refresh_seconds=deploy_config.autoscale_refresh_seconds,
                    autoscale_target_utilization=deploy_config.autoscale_target_utilization,
                    collect_model_data=deploy_config.collect_model_data,
                    cpu_cores=deploy_config.cpu_cores,
                    memory_gb=deploy_config.memory_gb,
                    scoring_timeout_ms=deploy_config.scoring_timeout_ms,
                    replica_max_concurrent_requests=deploy_config.replica_max_concurrent_requests,
                    max_request_wait_time=deploy_config.max_request_wait_time,
                    num_replicas=deploy_config.num_replicas,
                    models=models, inference_config=inference_config,
                    gpu_cores=deploy_config.gpu_cores,
                    period_seconds=deploy_config.period_seconds,
                    initial_delay_seconds=deploy_config.initial_delay_seconds,
                    timeout_seconds=deploy_config.timeout_seconds,
                    success_threshold=deploy_config.success_threshold,
                    failure_threshold=deploy_config.failure_threshold,
                    traffic_percentile=deploy_config.traffic_percentile, is_default=is_default,
                    is_control_version_type=is_control_version_type,
                    cpu_cores_limit=deploy_config.cpu_cores_limit,
                    memory_gb_limit=deploy_config.memory_gb_limit)
        else:
            service.update(auth_enabled=deploy_config.auth_enabled,
                           token_auth_enabled=deploy_config.token_auth_enabled,
                           enable_app_insights=deploy_config.enable_app_insights)
    elif service._webservice_type.lower() == 'local':
        # local update
        deployment_config = \
            LocalWebservice.deploy_configuration(port=deploy_config.port if deploy_config else None)

        service.update(models=models,
                       deployment_config=deployment_config,
                       inference_config=inference_config)
    else:
        raise WebserviceException("Unknown deployment type: {}".format(service._webservice_type))


def get_deployments_import_error(import_error):
    deployments_suffix = (". pandas numpy and flask are needed for"
                          "full mlflow.deployments support with the azureml backend.")
    return ImportError(import_error.msg + deployments_suffix)
