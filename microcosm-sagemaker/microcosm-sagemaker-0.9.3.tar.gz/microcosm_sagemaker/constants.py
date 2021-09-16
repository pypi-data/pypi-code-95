"""
SageMaker global constants.

"""
from pathlib import Path


APP_HOOKS_GROUP = "microcosm_sagemaker.app_hooks"

EVALUATE_APP_HOOK = "evaluate"
SERVE_APP_HOOK = "serve"
TRAIN_APP_HOOK = "train"

SAGEMAKER_PREFIX = Path("/opt/ml/")
ARTIFACT_CONFIGURATION_PATH = "configuration.json"


class SagemakerPath:
    INPUT_DATA = SAGEMAKER_PREFIX / "input/data"
    MODEL = SAGEMAKER_PREFIX / "model"
    OUTPUT = SAGEMAKER_PREFIX / "output"
    HYPERPARAMETERS = SAGEMAKER_PREFIX / "input/config/hyperparameters.json"


# NOTE: We can only use up to 10 dimensions:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html
CLOUDWATCH_MAX_DIMENSIONS = 10
