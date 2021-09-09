import os
from importlib_metadata import version, PackageNotFoundError

# try fetching version, if it fails (usually when in dev), add default
from biolib.biolib_logging import logger

try:
    BIOLIB_PACKAGE_VERSION = version('pybiolib')
except PackageNotFoundError:
    BIOLIB_PACKAGE_VERSION = '0.0.0'

IS_DEV = os.getenv('BIOLIB_DEV', '').upper() == 'TRUE'

BIOLIB_PACKAGE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

BIOLIB_CLOUD_ENVIRONMENT = os.getenv('BIOLIB_CLOUD_ENVIRONMENT', '').lower()

BIOLIB_IS_RUNNING_IN_ENCLAVE = BIOLIB_CLOUD_ENVIRONMENT == 'enclave'

IS_RUNNING_IN_CLOUD = BIOLIB_CLOUD_ENVIRONMENT in ('enclave', 'non-enclave')

if BIOLIB_CLOUD_ENVIRONMENT and not IS_RUNNING_IN_CLOUD:
    logger.warning((
        'BIOLIB_CLOUD_ENVIRONMENT defined but does not specify the cloud environment correctly. ',
        'The compute node will not act as a cloud compute node'
    ))

BIOLIB_CLOUD_SKIP_PCR_VERIFICATION = os.getenv('BIOLIB_CLOUD_SKIP_PCR_VERIFICATION', '').upper() == 'TRUE'

RUN_DEV_JOB_ID = 'run-dev-mocked-job-id'
