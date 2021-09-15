import os
import subprocess
import time
from datetime import datetime
from socket import gethostbyname, gethostname
import requests

from biolib import utils
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger
from biolib.typing_utils import Optional
from biolib.biolib_api_client import BiolibApiClient
from biolib.compute_node.cloud_utils.enclave_parent_types import VsockProxyResponse
from biolib.compute_node.webserver.webserver_types import WebserverConfig, ComputeNodeInfo, ShutdownTimes
from biolib.biolib_api_client import RemoteHost


class _EnclaveUtils:
    _BASE_URL = 'http://127.0.0.1:5005'

    @staticmethod
    def get_webserver_config():
        response = requests.get(f'{_EnclaveUtils._BASE_URL}/config/', timeout=5)
        return response.json()

    @staticmethod
    def deregister_and_shutdown() -> None:
        requests.post(url=f'{_EnclaveUtils._BASE_URL}/deregister_and_shutdown/', timeout=5)

    @staticmethod
    def start_vsock_proxy(remote_host: RemoteHost) -> VsockProxyResponse:
        response = requests.post(url=f'{_EnclaveUtils._BASE_URL}/vsock_proxy/', json=remote_host, timeout=5)
        vsock_proxy: VsockProxyResponse = response.json()
        return vsock_proxy

    @staticmethod
    def stop_vsock_proxy(vsock_proxy_id: str) -> None:
        requests.delete(url=f'{_EnclaveUtils._BASE_URL}/vsock_proxy/{vsock_proxy_id}/', timeout=5)

    @staticmethod
    def start_shutdown_timer(minutes_until_shutdown: int) -> None:
        requests.post(
            url=f'{_EnclaveUtils._BASE_URL}/start_shutdown_timer/',
            json={'minutes_until_shutdown': minutes_until_shutdown},
            timeout=5,
        )


class CloudUtils:
    _webserver_config: Optional[WebserverConfig] = None
    enclave = _EnclaveUtils

    @staticmethod
    def initialize() -> None:
        logger.debug('Reporting availability...')
        CloudUtils._report_availability()

    @staticmethod
    def get_webserver_config() -> WebserverConfig:
        if CloudUtils._webserver_config:
            return CloudUtils._webserver_config

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils._webserver_config = CloudUtils.enclave.get_webserver_config()

        else:
            CloudUtils._webserver_config = WebserverConfig(
                compute_node_info=ComputeNodeInfo(
                   auth_token=CloudUtils._get_environment_variable('BIOLIB_COMPUTE_NODE_AUTH_TOKEN'),
                   public_id=CloudUtils._get_environment_variable('BIOLIB_COMPUTE_NODE_PUBLIC_ID'),
                   ip_address=gethostbyname(gethostname())
                ),
                base_url=CloudUtils._get_environment_variable('BIOLIB_BASE_URL'),
                is_dev=CloudUtils._get_environment_variable('BIOLIB_DEV').upper() == 'TRUE',
                shutdown_times=ShutdownTimes(
                    job_max_runtime_shutdown_time_in_seconds=CloudUtils._get_environment_variable_as_int(
                        'BIOLIB_CLOUD_JOB_MAX_RUNTIME_IN_SECONDS'
                    ),
                    auto_shutdown_time_in_seconds=CloudUtils._get_environment_variable_as_int(
                        'BIOLIB_CLOUD_AUTO_SHUTDOWN_TIME_IN_SECONDS'
                    ),
                    reserved_shutdown_time_in_seconds=CloudUtils._get_environment_variable_as_int(
                        'BIOLIB_CLOUD_RESERVED_SHUTDOWN_TIME_IN_SECONDS'
                    )
                )
            )

        return CloudUtils._webserver_config

    @staticmethod
    def deregister_and_shutdown() -> None:
        logger.debug('Deregistering and shutting down...')

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils.enclave.deregister_and_shutdown()
        else:
            config = CloudUtils.get_webserver_config()
            try:
                requests.post(url=f'{config["base_url"]}/api/jobs/deregister/', json={
                    'auth_token': config["compute_node_info"]["auth_token"],
                    'public_id': config["compute_node_info"]["public_id"],
                })
            except Exception as error:  # pylint: disable=broad-except
                logger.error(error)

            logger.debug('Shutting down...')
            try:
                subprocess.run(['sudo', 'shutdown', 'now'], check=True)
            except Exception as error:  # pylint: disable=broad-except
                logger.error(error)

    @staticmethod
    def start_auto_shutdown_timer() -> None:
        config = CloudUtils.get_webserver_config()
        CloudUtils._start_shutdown_timer(config['shutdown_times']['auto_shutdown_time_in_seconds'])

    @staticmethod
    def start_running_job_shutdown_timer() -> None:
        config = CloudUtils.get_webserver_config()
        CloudUtils._start_shutdown_timer(config['shutdown_times']['job_max_runtime_shutdown_time_in_seconds'])

    @staticmethod
    def start_reserved_shutdown_timer() -> None:
        config = CloudUtils.get_webserver_config()
        CloudUtils._start_shutdown_timer(config['shutdown_times']['reserved_shutdown_time_in_seconds'])

    @staticmethod
    def _start_shutdown_timer(seconds_until_shutdown: int) -> None:
        if not utils.IS_RUNNING_IN_CLOUD:
            raise BioLibError('Can not start shutdown timer when not running in cloud.')

        minutes_until_shutdown = int(seconds_until_shutdown / 60)
        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils.enclave.start_shutdown_timer(minutes_until_shutdown)
        else:
            subprocess.run(['sudo', 'shutdown', f'+{minutes_until_shutdown}'], check=True)
            logger.debug(f'Shutting down in {minutes_until_shutdown} minutes')

    @staticmethod
    def _report_availability() -> None:
        try:
            config = CloudUtils.get_webserver_config()
            compute_node_info = config['compute_node_info']
            api_client = BiolibApiClient.get()
            logger.debug(f'Registering with {compute_node_info} to host {api_client.base_url} at {datetime.now()}')

            response: Optional[requests.Response] = None
            max_retries = 5
            for retry_count in range(max_retries):
                try:
                    response = requests.post(f'{api_client.base_url}/api/jobs/report_available/',
                                             json=compute_node_info)
                    break
                except Exception as error:  # pylint: disable=broad-except
                    logger.error(f'Self-registering failed with error: {error}')
                    if retry_count < max_retries - 1:
                        seconds_to_sleep = 1
                        logger.info(f'Retrying self-registering in {seconds_to_sleep} seconds')
                        time.sleep(seconds_to_sleep)

            if not response:
                raise BioLibError('Failed to register. Max retry limit reached')

            if response.status_code != 201:
                raise Exception("Non 201 error code")

            if response.json()['is_reserved']:
                # Start running job shutdown timer if reserved. It restarts when the job is actually saved
                CloudUtils.start_reserved_shutdown_timer()

            else:
                # Else start the longer auto shutdown timer
                CloudUtils.start_auto_shutdown_timer()

        except Exception as exception:  # pylint: disable=broad-except
            logger.error(f'Shutting down as self register failed due to: {exception}')
            if not utils.IS_DEV:
                CloudUtils.deregister_and_shutdown()

    @staticmethod
    def _get_environment_variable(key: str) -> str:
        value = os.environ.get(key)
        # Purposely loose falsy check (instead of `is not None`) as empty string should fail
        if not value:
            raise Exception(f'CloudUtils: Missing environment variable "{key}"')

        return value

    @staticmethod
    def _get_environment_variable_as_int(key: str) -> int:
        return int(CloudUtils._get_environment_variable(key))
