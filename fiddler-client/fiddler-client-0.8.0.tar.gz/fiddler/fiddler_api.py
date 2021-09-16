# TODO: Add License
import configparser
import contextlib
import copy
import json
import logging
import math
import os.path
import pathlib
import pickle
import random
import re
import shutil
import tarfile
import tempfile
import textwrap
import threading
import time
from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import numpy as np
import pandas as pd
import requests
import yaml
from deepdiff import DeepDiff
from packaging import version
from requests.exceptions import Timeout
from werkzeug.datastructures import FileStorage

from fiddler.file_processor.src.constants import SUPPORTABLE_FILE_EXTENSIONS

from ._version import __version__
from .aws_utils import validate_gcp_uri_access, validate_s3_uri_access
from .core_objects import (
    CURRENT_SCHEMA_VERSION,
    ArtifactStatus,
    AttributionExplanation,
    BatchPublishType,
    Column,
    DatasetInfo,
    DataType,
    DeploymentOptions,
    EventTypes,
    FiddlerEventColumns,
    FiddlerPublishSchema,
    FiddlerTimestamp,
    InitMonitoringModifications,
    MalformedSchemaException,
    MLFlowParams,
    ModelInfo,
    ModelInputType,
    ModelTask,
    MonitoringViolation,
    MonitoringViolationType,
    MulticlassAttributionExplanation,
    SegmentInfo,
    name_check,
    possible_init_monitoring_modifications,
    sanitized_name,
)
from .file_processor.src.facade import upload_dataset
from .model_info_validator import ModelInfoValidator
from .monitoring_validator import MonitoringValidator
from .utils import (
    TIMESTAMP_FORMAT,
    ResourceNotFound,
    _df_to_dict,
    _try_series_retype,
    _type_enforce,
    cast_input_data,
    clean_df_types,
    df_from_json_rows,
    df_size_exceeds,
    do_not_proceed,
    formatted_utcnow,
    is_int_type,
    pad_timestamp,
    print_streamed_result,
)
from .validator import PackageValidator

# from sympy import symbols


LOG = logging.getLogger()

SUCCESS_STATUS = 'SUCCESS'
FAILURE_STATUS = 'FAILURE'
FIDDLER_ARGS_KEY = '__fiddler_args__'
STREAMING_HEADER_KEY = 'X-Fiddler-Results-Format'
AUTH_HEADER_KEY = 'Authorization'
ROUTING_HEADER_KEY = 'x-fdlr-fwd'
ADMIN_SERVICE_PORT = 4100
MAX_ID_LEN = 30
DATASET_MAX_ROWS = 50_000

# A PredictionEventBundle represents a batch of inferences and their input
# features. All of these share schema, latency, and success status. A bundle
# can consist just one event as well.
PredictionEventBundle = namedtuple(
    'PredictionEventBundle',
    [
        'prediction_status',  # typeof: int # 0 for success, failure otherwise
        'prediction_latency',  # typeof: float # Latency in seconds.
        'input_feature_bundle',  # list of feature vectors.
        'prediction_bundle',  # list of prediction vectors.
        # TODO: Support sending schema as well.
    ],
)


_protocol_version = 1


class JSONException(RuntimeError):
    def __init__(self, status, message, stacktrace, logs):
        self.status = status
        self.message = message
        self.stacktrace = stacktrace
        self.logs = logs

    def __str__(self):
        return (
            f'{self.status}: {self.message} \n\n '
            f'{self.stacktrace} \n Server Logs:\n {self.logs}'
        )


class FiddlerApi:
    """Broker of all connections to the Fiddler API.
    Conventions:
        - Exceptions are raised for FAILURE reponses from the backend.
        - Methods beginning with `list` fetch lists of ids (e.g. all model ids
            for a project) and do not alter any data or state on the backend.
        - Methods beginning with `get` return a more complex object but also
            do not alter data or state on the backend.
        - Methods beginning with `run` invoke model-related execution and
            return the result of that computation. These do not alter state,
            but they can put a heavy load on the computational resources of
            the Fiddler engine, so they should be paralellized with care.
        - Methods beginning with `delete` permanently, irrevocably, and
            globally destroy objects in the backend. Think "rm -rf"
        - Methods beginning with `upload` convert and transmit supported local
            objects to Fiddler-friendly formats loaded into the Fiddler engine.
            Attempting to upload an object with an identifier that is already
            in use will result in an exception being raised, rather than the
            existing object being overwritten. To update an object in the
            Fiddler engine, please call both the `delete` and `upload` methods
            pertaining to the object in question.

    :param url: The base URL of the API to connect to. Usually either
        https://dev.fiddler.ai (cloud) or http://localhost:4100 (onebox)
    :param org_id: The name of your organization in the Fiddler platform
    :param auth_token: Token used to authenticate. Your token can be
        created, found, and changed at <FIDDLER URL>/settings/credentials.
    :param proxies: optionally, a dict of proxy URLs. e.g.,
                    proxies = {'http' : 'http://proxy.example.com:1234',
                               'https': 'https://proxy.example.com:5678'}
    :param verbose: if True, api calls will be logged verbosely,
                    *warning: all information required for debugging will be
                    logged including the auth_token.
    """

    def __init__(
        self, url=None, org_id=None, auth_token=None, proxies=None, verbose=False
    ):
        if Path('fiddler.ini').is_file():
            config = configparser.ConfigParser()
            config.read('fiddler.ini')
            info = config['FIDDLER']
            if not url:
                url = info['url']
            if not org_id:
                org_id = info['org_id']
            if not auth_token:
                auth_token = info['auth_token']

        if url[-1] == '/':
            raise ValueError('url should not end in "/"')

        # use session to preserve session data
        self.session = requests.Session()
        if proxies:
            assert isinstance(proxies, dict)
            self.session.proxies = proxies
        self.adapter = requests.adapters.HTTPAdapter(
            pool_connections=25,
            pool_maxsize=25,
        )
        self.session.mount(url, self.adapter)
        self.url = url
        self.org_id = org_id
        self.auth_header = {AUTH_HEADER_KEY: f'Bearer {auth_token}'}
        self.streaming_header = {STREAMING_HEADER_KEY: 'application/jsonlines'}
        self.verbose = verbose
        self.strict_mode = True
        self.capture_server_log = False
        self.last_server_log = None
        self._check_connection()
        self.monitoring_validator = MonitoringValidator()
        self.experimental = ExperimentalFeatures(client=self)

    def __getattr__(self, function_name):
        """
        Overriding allows us to point unrecognized use cases to the documentation page
        """

        def method(*args, **kwargs):
            # This is a method that is not recognized
            error_msg = (
                f'Function `{function_name}` not found.\n'
                f'Please consult Fiddler documentation at `https://api.fiddler.ai/`'
            )
            raise RuntimeError(error_msg)

        return method

    def _check_connection(self, check_client_version=True, check_server_version=True):
        try:
            path = ['get_supported_features', self.org_id]
            result = self._call(path, is_get_request=True)
            server_version = result.get('supported_client_version', __version__)
            if version.parse(server_version) > version.parse(__version__):
                LOG.info(
                    f'client_version = {__version__} < server_version = {server_version}'
                )
                if check_client_version:
                    print(
                        f'OUTDATED CLIENT: Your client is running version {__version__}, '
                        f'consider upgrading to {server_version}.'
                    )
            elif version.parse(server_version) < version.parse(__version__):
                LOG.info(
                    f'client_version = {__version__} > server_version = {server_version}'
                )
                if check_server_version:
                    print(
                        f'OUTDATED SERVER: The URL you connected to is running version {server_version}, '
                        f'consider getting it upgraded to match your client {__version__}.'
                    )
            else:
                LOG.info(
                    f'client_version = {__version__} == server_version = {server_version}'
                )
            return 'OK'
        except requests.exceptions.ConnectionError:
            LOG.warning(
                'CONNECTION CHECK FAILED: Unable to connect with '
                'to Fiddler. Are you sure you have the right URL?'
            )
        except Exception as e:
            LOG.warning(
                f'API CHECK FAILED: Able to connect to Fiddler, '
                f'but request failed with message:\n"{str(e)}"'
            )

    def _safe_name_check(self, name: str, max_length: int):
        if self.strict_mode:
            name_check(name, max_length)

    @staticmethod
    def _abort_dataset_upload(
        dataset: Dict[str, pd.DataFrame], size_check_enabled: bool, max_len: int
    ):
        """
        This method checks if any of the dataframes exeeds size limit.
        In case the size limit is exceeded and size_check_enabled is True
        a warning is issued and the user is required to confirm if they'd
        like to proceed with the upload
        """
        # check if the dataset exceeds size limits
        warn_and_query = size_check_enabled and df_size_exceeds(dataset, max_len)
        if warn_and_query:
            LOG.warning(
                f'The dataset contains more than {max_len} datapoints. '
                f'Please allow for additional time to upload the dataset '
                f'and calculate statistical metrics. '
                f'To disable this message set the flag size_check_enabled to False. '
                f'\n\nAlternately, consider sampling the dataset. '
                f'If you plan to sample the dataset please ensure that the '
                f'representative sample captures all possible '
                f'categorical features, labels and numerical ranges that '
                f'would be encountered during deployment.'
                f'\n\nFor details on how datasets are used and considerations '
                f'for when large datasets are necessary, please refer to '
                f'https://docs.fiddler.ai/components/#dataset'
            )
            user_query = 'Would you like to proceed with the upload (y/n)? '
            return do_not_proceed(user_query)
        return False

    @staticmethod
    def _get_routing_header(path_base: str) -> Dict[str, str]:
        """Returns the proper header so that a request is routed to the correct
        service."""
        executor_service_bases = (
            'dataset_predictions',
            'execute',
            'executor',
            'explain',
            'explain_by_row_id',
            'fairness',
            'feature_importance',
            'generate',
            'new_project',
            'precache_globals',
        )
        if path_base in executor_service_bases:
            return {ROUTING_HEADER_KEY: 'executor_service'}
        else:
            return {ROUTING_HEADER_KEY: 'data_service'}

    def _call_executor_service(
        self,
        path: List[str],
        json_payload: Any = None,
        files: Optional[List[Path]] = None,
        is_get_request: bool = False,
        stream: bool = False,
    ):
        no_auth_onebox = False
        try:
            if self.url == 'http://localhost:6100':
                no_auth_onebox = True
                self.url = 'http://localhost:5100'

            return self._call(path, json_payload, files, is_get_request, stream)
        finally:
            if no_auth_onebox:
                self.url = 'http://localhost:6100'

    @staticmethod
    def _handle_fail_res(res, endpoint):
        """
        Raises an actionable error message for a response with a status code > 200
        """
        try:
            # catch auth failure
            json_response = res.json()
            message = json_response.get('message')
            error_msg = (
                f'API call to {endpoint} failed with status {res.status_code}:'
                f' The full response message was {message}'
            )
            # catch resource not found failure
            if res.status_code == 404:
                error = ResourceNotFound(message=message)
            elif res.status_code == 401:
                # More specific error message
                error_msg = (
                    'API call failed with status 401: '
                    'Authorization Required. '
                    'Do you have the right `org_id` and `auth_token`?'
                )
                error = RuntimeError(error_msg)
            else:
                error = JSONException(
                    status=json_response.get('status'),
                    message=error_msg,
                    stacktrace=json_response.get('stacktrace'),
                    logs=json_response.get('logs'),
                )
        except Exception:
            error_msg = (
                f'API call to {endpoint} failed with status {res.status_code}:'
                f' The full response message was {res.text}'
            )
            error = RuntimeError(error_msg)
        LOG.debug(error_msg)
        raise error

    def _form_request(
        self,
        path: List[str],
        is_get_request: bool = None,
        json_payload: Any = None,
        stream: bool = False,
        files: Optional[List[Path]] = None,
        context_stack=None,
        endpoint=None,
    ):
        if is_get_request:
            req = requests.Request('GET', endpoint)
        else:
            # if uploading files, we use a multipart/form-data request and
            # dump the json_payload to be the special "fiddler args"
            # as a json object in the form

            if files is not None:
                # open all the files into the context manager stack
                opened_files = {
                    fpath.name: context_stack.enter_context(fpath.open('rb'))
                    for fpath in files
                }
                #
                # NOTE: there are a lot LOT of ways to do this wrong with
                # `requests`
                #
                # Take a look here (and at the thread linked) for more info:
                # https://stackoverflow.com/a/35946962
                #
                # And here: https://stackoverflow.com/a/12385661
                #
                form_data = {
                    **{
                        FIDDLER_ARGS_KEY: (
                            None,  # filename
                            json.dumps(json_payload),  # data
                            'application/json',  # content_type
                        )
                    },
                    **{
                        fpath.name: (
                            fpath.name,  # filename
                            opened_files[fpath.name],  # data
                            'application/octet-stream',  # content_type
                        )
                        for fpath in files
                    },
                }
                req = requests.Request('POST', endpoint, files=form_data)
            else:
                req = requests.Request('POST', endpoint, json=json_payload)

        # add necessary headers
        # using prepare_request from session to keep session data
        req = self.session.prepare_request(req)

        added_headers = dict()
        added_headers.update(self.auth_header)
        added_headers.update(self._get_routing_header(path[0]))
        if self.capture_server_log:
            added_headers['X-Fiddler-Logs-Level'] = 'DEBUG'
        if stream:
            added_headers.update(self.streaming_header)
        req.headers = {**added_headers, **req.headers}

        return req

    def _call(
        self,
        path: List[str],
        json_payload: Any = None,
        files: Optional[List[Path]] = None,
        is_get_request: bool = False,
        stream: bool = False,
        timeout: Optional[int] = None,
        num_tries: Optional[int] = 1,
    ):
        """Issues a request to the API and returns the result,
        logigng and handling errors appropriately.

        Raises a RuntimeError if the response is a failure or cannot be parsed.
        Does not handle any ConnectionError exceptions thrown by the `requests`
        library.

        Note: Parameters `timeout` and `num_tries` are currently only utilized in a workaround
        for a bug involving Mac+Docker communication. See: https://github.com/docker/for-mac/issues/3448
        """

        # set up a context manager to open files
        with contextlib.ExitStack() as context_stack:
            endpoint = '/'.join([self.url] + path)
            request_type = 'GET' if is_get_request else 'POST'
            if json_payload:
                request_excerpt = textwrap.indent(
                    json.dumps(json_payload, indent=2)[:2048], '  '
                )
            else:
                request_excerpt = None
            if self.verbose:
                LOG.info(
                    f'running api call as {request_type} request\n'
                    f'to {endpoint}\n'
                    f'with headers {self.auth_header}\n'
                    f'with payload {request_excerpt}'
                )

            req = self._form_request(
                path=path,
                is_get_request=is_get_request,
                json_payload=json_payload,
                stream=stream,
                files=files,
                context_stack=context_stack,
                endpoint=endpoint,
            )

            # log the raw request
            raw_request_info = (
                f'Request:\n'
                f'  url: {req.url}\n'
                f'  method: {req.method}\n'
                f'  headers: {req.headers}'
            )
            LOG.debug(raw_request_info)

            if os.environ.get('REQUESTS_CA_BUNDLE'):
                self.session.verify = os.environ.get('REQUESTS_CA_BUNDLE')

            # send the request using session to carry auth info from login
            if 'FIDDLER_RETRY_PUBLISH' in os.environ and str(
                os.environ['FIDDLER_RETRY_PUBLISH']
            ).lower() in ['yes', 'y', 'true', '1']:
                # Experimental retry path needed in case of Mac-Docker communication bug.
                # Likely only needed in case of Onebox Mac-Docker setups, and as such only
                # accessible through this environmental variable
                res = None
                attempt_count = 0
                while attempt_count < num_tries:
                    try:
                        res = self.session.send(req, stream=stream, timeout=timeout)
                        break
                    except Timeout:
                        # Retrying due to a failure of some kind
                        attempt_count += 1
                        # Exponential sleep between calls (up to 10 seconds)
                        time.sleep(min(pow(2, attempt_count), 10))
                if res is None:
                    error_msg = (
                        'API call failed due to unknown reason. '
                        'Please try again at a later point.'
                    )
                    raise Timeout(error_msg)
            else:
                res = self.session.send(req, stream=stream)

            if self.verbose:
                LOG.info(f'response: {res.text}')

        # catch any failure
        if res.status_code != 200:
            self._handle_fail_res(res, endpoint)

        if stream:
            return self._process_streaming_call_result(res, endpoint, raw_request_info)
        return self._process_non_streaming_call_result(res, endpoint, raw_request_info)

    @staticmethod
    def _raise_on_status_error(
        response: requests.Response, endpoint: str, raw_request_info: str
    ):
        """Raises exception on HTTP errors similar to
        `response.raise_for_status()`."""
        # catch non-auth failures
        try:
            response.raise_for_status()
        except Exception:
            response_payload = response.json()
            try:
                failure_message = response_payload.get('message', 'Unknown')
                failure_stacktrace = response_payload.get('stacktrace')
                error_msg = (
                    f'API call failed.\n'
                    f'Error message: {failure_message}\n'
                    f'Endpoint: {endpoint}'
                )
                if failure_stacktrace:
                    error_msg += f'\nStacktrace: {failure_stacktrace}'

            except KeyError:
                error_msg = (
                    f'API call to {endpoint} failed.\n'
                    f'Request response: {response.text}'
                )
            LOG.debug(f'{error_msg}\n{raw_request_info}')
            raise RuntimeError(error_msg)

    def _process_non_streaming_call_result(
        self, response: requests.Response, endpoint: str, raw_request_info: str
    ):

        FiddlerApi._raise_on_status_error(response, endpoint, raw_request_info)

        # catch non-JSON response (this is rare, the backend should generally
        # return JSON in all cases)
        try:
            response_payload = response.json()
        except json.JSONDecodeError:
            print(response.status_code)
            error_msg = (
                f'API call to {endpoint} failed.\n' f'Request response: {response.text}'
            )
            LOG.debug(f'{error_msg}\n{raw_request_info}')
            raise RuntimeError(error_msg)

        assert response_payload['status'] == SUCCESS_STATUS
        result = response_payload.get('result')
        self.last_server_log = response_payload.get('logs')

        # log the API call on success (excerpt response on success)
        response_excerpt = textwrap.indent(
            json.dumps(response_payload, indent=2)[:2048], '  '
        )
        log_msg = (
            f'API call to {endpoint} succeeded.\n'
            f'Request response: {response_excerpt}\n'
            f'{raw_request_info}\n'
        )
        if self.verbose:
            LOG.info(log_msg)
        return result

    @staticmethod
    def _process_streaming_call_result(
        response: requests.Response, endpoint: str, raw_request_info: str
    ):
        """Processes response in jsonlines format. `json_streaming_endpoint`
        returns jsonlines with one json object per line when
        'X-Fiddler-Response-Format' header is set to 'jsonlines'.
        :returns: a generator for results."""

        FiddlerApi._raise_on_status_error(response, endpoint, raw_request_info)

        got_eos = False  # got proper end_of_stream.

        if response.headers.get('Content-Type') != 'application/x-ndjson':
            RuntimeError('Streaming response Content-Type is not "x-ndjson"')

        # Read one line at a time. `chunk_size` None ensures that a line
        # is returned as soon as it is read, rather waiting for any minimum
        # size (default is 512 bytes).
        for line in response.iter_lines(chunk_size=None):
            if line:
                row_json = json.loads(line)
                if 'result' in row_json:
                    yield row_json['result']
                elif row_json.get('status') == SUCCESS_STATUS:
                    got_eos = True
                    break
        if not got_eos:
            raise RuntimeError(
                'Truncated response for streaming request. '
                'Failed to receive successful status.'
            )

    def list_datasets(self, project_id: str) -> List[str]:
        """List the ids of all datasets in the organization.

        :returns: List of strings containing the ids of each dataset.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)

        path = ['list_datasets', self.org_id, project_id]
        res = self._call(path, is_get_request=True)

        return res

    def list_projects(self) -> List[str]:
        """List the ids of all projects in the organization.

        :returns: List of strings containing the ids of each project.
        """
        path = ['list_projects', self.org_id]
        res = self._call(path, is_get_request=True)
        return [proj['id'] for proj in res['projects']]

    def list_models(self, project_id: str) -> List[str]:
        """List the names of all models in a project.

        :param project_id: The unique identifier of the project on the Fiddler
            engine.
        :returns: List of strings containing the ids of each model in the
            specified project.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)

        path = ['list_models', self.org_id, project_id]
        res = self._call(path, is_get_request=True)

        return res

    def get_dataset_info(self, project_id: str, dataset_id: str) -> DatasetInfo:
        """Get DatasetInfo for a dataset.

        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine.

        :returns: A fiddler.DatasetInfo object describing the dataset.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        path = ['dataset_schema', self.org_id, project_id, dataset_id]
        res = self._call(path, is_get_request=True)

        info = DatasetInfo.from_dict(res)
        info.dataset_id = dataset_id
        return info

    def _basic_drift_checks(self, project_id, model_info, model_id):
        # Lets make sure prediction table is created and has prediction data by
        # just running the slice query
        violations = []
        try:
            query_str = f'select * from "{model_info.datasets[0]}.{model_id}" limit 1'
            df = self.get_slice(
                query_str,
                project_id=project_id,
            )
            for index, row in df.iterrows():
                for out_col in model_info.outputs:
                    if out_col.name not in row:
                        msg = f'Drift error: {out_col.name} not in predictions table. Please delete and re-register your model.'
                        violations.append(
                            MonitoringViolation(MonitoringViolationType.WARNING, msg)
                        )
        except RuntimeError:
            msg = 'Drift error: Predictions table does not exists. Please run trigger_pre_computation for an existing model, or use register_model to register a new model.'
            violations.append(MonitoringViolation(MonitoringViolationType.WARNING, msg))
            return violations

        return violations

    def get_model_info(self, project_id: str, model_id: str) -> ModelInfo:
        """Get ModelInfo for a model in a certain project.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.

        :returns: A fiddler.ModelInfo object describing the model.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        path = ['model_info', self.org_id, project_id, model_id]
        res = self._call(path, is_get_request=True)
        return ModelInfo.from_dict(res)

    def _query_dataset(
        self,
        project_id: str,
        dataset_id: str,
        fields: List[str],
        max_rows: int,
        split: Optional[str] = None,
        sampling=False,
        sampling_seed=0.0,
    ):
        payload = dict(
            fields=fields,
            limit=max_rows,
            sampling=sampling,
        )

        if sampling:
            payload['sampling_seed'] = sampling_seed
        if split is not None:
            payload['source'] = f'{split}.csv'

        path = ['dataset_query', self.org_id, project_id, dataset_id]
        res = self._call(path, json_payload=payload, stream=True)
        return res

    def get_dataset(
        self,
        project_id: str,
        dataset_id: str,
        max_rows: int = 1_000,
        splits: Optional[List[str]] = None,
        sampling=False,
        dataset_info: Optional[DatasetInfo] = None,
        include_fiddler_id=False,
    ) -> Dict[str, pd.DataFrame]:
        """Fetches data from a dataset on Fiddler.

        :param project_id: The unique identifier of the project on the Fiddler
            engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine.
        :param max_rows: Up to this many rows will be fetched from eash split
            of the dataset.
        :param splits: If specified, data will only be fetched for these
            splits. Otherwise, all splits will be fetched.
        :param sampling: If True, data will be sampled up to max_rows. If
            False, rows will be returned in order up to max_rows. The seed
            will be fixed for sampling.∂
        :param dataset_info: If provided, the API will skip looking up the
            DatasetInfo (a necessary precursor to requesting data).
        :param include_fiddler_id: Return the Fiddler engine internal id
            for each row. Useful only for debugging.

        :returns: A dictionary of str -> DataFrame that maps the name of
            dataset splits to the data in those splits. If len(splits) == 1,
            returns just that split as a dataframe, rather than a dataframe.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        if dataset_info is None:
            dataset_info = self.get_dataset_info(project_id, dataset_id)
        else:
            dataset_info = copy.deepcopy(dataset_info)

        def get_df_from_split(split, fiddler_id=include_fiddler_id):
            column_names = dataset_info.get_column_names()
            if fiddler_id:
                column_names.insert(0, '__fiddler_id')
            dataset_rows = self._query_dataset(
                project_id,
                dataset_id,
                fields=column_names,
                max_rows=max_rows,
                split=split,
                sampling=sampling,
            )
            return df_from_json_rows(
                dataset_rows, dataset_info, include_fiddler_id=include_fiddler_id
            )

        if splits is None:
            use_splits = [
                os.path.splitext(filename)[0] for filename in dataset_info.files
            ]
        else:
            use_splits = splits
        res = {split: get_df_from_split(split) for split in use_splits}
        if splits is not None and len(splits) == 1:
            # unwrap single-slice results
            res = next(iter(res.values()))
        return res

    def get_slice(
        self,
        sql_query: str,
        project_id: str,
        columns_override: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Fetches data from Fiddler via a *slice query* (SQL query).

        :param sql_query: A special SQL query that begins with the keyword
            "SLICE"
        :param project_id: The unique identifier of the project on the Fiddler
            engine.
        :param columns_override: A list of columns to return even if they are
            not specified in the slice.
        :returns: A table containing the sliced data (as a Pandas DataFrame)
        """
        payload = dict(sql=sql_query, project=project_id)
        if columns_override is not None:
            payload['slice_columns_override'] = columns_override

        path = ['slice_query', self.org_id, project_id]
        res = self._call(path, json_payload=payload)

        slice_info = res.pop(0)
        if not slice_info['is_slice']:
            raise RuntimeError(
                'Query does not return a valid slice. ' 'Query: ' + sql_query
            )
        column_names = slice_info['columns']
        dtype_strings = slice_info['dtypes']
        df = pd.DataFrame(res, columns=column_names)
        for column_name, dtype in zip(column_names, dtype_strings):
            df[column_name] = _try_series_retype(df[column_name], dtype)
        return df

    def delete_dataset(self, project_id: str, dataset_id: str):
        """Permanently delete a dataset.

        :param project_id: The unique identifier of the project on the Fiddler
            engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine.

        :returns: Server response for deletion action.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        path = ['dataset_delete', self.org_id, project_id, dataset_id]
        result = self._call(path)

        return result

    def delete_model(
        self, project_id: str, model_id: str, delete_prod=False, delete_pred=True
    ):
        """Permanently delete a model.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.
        :param delete_prod: Boolean value to delete the production table.
            By default this table is not dropped.
        :param delete_pred: Boolean value to delete the prediction table.
            By default this table is dropped.

        :returns: Server response for deletion action.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        payload = {
            'project_id': project_id,
            'model_id': model_id,
            'delete_prod': delete_prod,
            'delete_pred': delete_pred,
        }

        path = ['delete_model', self.org_id, project_id, model_id]
        try:
            result = self._call(path, json_payload=payload)
        except Exception:
            # retry on error
            result = self._call(path, json_payload=payload)

        self._delete_model_artifacts(project_id, model_id)

        # wait for ES to come back healthy
        for i in range(3):
            try:
                self._call_executor_service(
                    ['deploy', self.org_id], is_get_request=True
                )
                break
            except Exception:
                pass

        return result

    def _delete_model_artifacts(self, project_id: str, model_id: str):
        """Permanently delete a model artifacts.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.

        :returns: Server response for deletion action.
        """
        # delete from executor service cache
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        path = ['delete_model_artifacts', self.org_id, project_id, model_id]
        result = self._call_executor_service(path)

        return result

    def delete_project(self, project_id: str):
        """Permanently delete a project.

        :param project_id: The unique identifier of the project on the Fiddler
            engine.

        :returns: Server response for deletion action.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)

        path = ['delete_project', self.org_id, project_id]
        result = self._call(path)

        return result

    def _upload_dataset_csvs(
        self,
        project_id: str,
        dataset_id: str,
        csv_file_paths: List[Path],
        dataset_info: Optional[DatasetInfo] = None,
    ):
        """Uploads a CSV file to the Fiddler platform."""
        self._safe_name_check(dataset_id, MAX_ID_LEN)
        payload = dict(dataset_name=dataset_id)
        if dataset_info is not None:
            if self.strict_mode:
                dataset_info.validate()
            payload['dataset_info'] = dict(dataset=dataset_info.to_dict())
        payload['do_import'] = True
        payload['split_test'] = False
        path = ['dataset_upload', self.org_id, project_id]
        print(f'Uploading the dataset {dataset_id} ...')
        result = self._call(path, json_payload=payload, files=csv_file_paths)
        return result

    def _import_model_predictions(
        self,
        project_id: str,
        dataset_id: str,
        model_id: str,
        columns: Sequence[Dict],
        csv_file_paths: List[Path],
    ):
        """Uploads model predictions to Fiddler platform."""
        payload = dict(dataset=dataset_id)
        payload['model'] = model_id
        payload['columns'] = columns

        path = ['import_model_predictions', self.org_id, project_id]
        result = self._call(path, json_payload=payload, files=csv_file_paths)
        return result

    def upload_dataset(
        self,
        project_id: str,
        dataset: Dict[str, pd.DataFrame],
        dataset_id: str,
        info: Optional[DatasetInfo] = None,
        size_check_enabled: bool = True,
    ):
        """Uploads a representative dataset to the Fiddler engine.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param dataset: A dictionary mapping name -> DataFrame
            containing data to be uploaded to the Fiddler engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine. Must be a short string without whitespace.
        :param info: A DatasetInfo object specifying all the details of the
            dataset. If not provided, a DatasetInfo will be inferred from the
            dataset and a warning raised.
        :param size_check_enabled: Flag to enable the dataframe size check.
            Default behavior is to raise a warning and present an interactive
            dialogue if the size of the dataframes exceeds the default limit.
            Set this flag to False to disable the checks.

        :returns: The server response for the upload.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        assert (
            ' ' not in dataset_id
        ), 'The dataset identifier should not contain whitespace'

        self._safe_name_check(dataset_id, MAX_ID_LEN)

        # get a dictionary of str -> pd.DataFrame for all data to upload
        if not isinstance(dataset, dict):
            raise ValueError('dataset must be a dictionary mapping name -> DataFrame')

        # check if the dataset exceeds size limits
        abort_upload = self._abort_dataset_upload(
            dataset, size_check_enabled, DATASET_MAX_ROWS
        )
        if abort_upload:
            raise RuntimeError('Dataset upload aborted.')

        # infer a dataset_info
        inferred_info = DatasetInfo.from_dataframe(
            dataset.values(), display_name=dataset_id
        )

        if info:
            # Since we started populating stats recently, some older yamls
            # dont have it. Or the user might just supply us the basic
            # schema without stats.
            # If the user provided the schema/yaml file, ask the user to
            # re-create dataset info with:
            # info = DatasetInfo.update_stats_for_existing_schema(dataset,
            # info, max_inferred_cardinality)
            for column in info.columns:
                if (
                    (column.value_range_min is None) or (column.value_range_max is None)
                ) and column.data_type.is_numeric():
                    raise ValueError(
                        f'Dataset info does not contain min/max values for the numeric feature {column.name}. '
                        f'Please update using fdl.DatasetInfo.update_stats_for_existing_schema() '
                        f'and upload dataset with the updated dataset info.'
                    )
                if (not column.possible_values) and (
                    column.data_type.value
                    in [DataType.CATEGORY.value, DataType.BOOLEAN.value]
                ):
                    raise ValueError(
                        f'Dataset info does not contain possible values for the categorical feature {column.name}. '
                        f'Please update using fdl.DatasetInfo.update_stats_for_existing_schema() '
                        f'and upload dataset with the updated dataset info.'
                    )
        # validate `info` if passed
        if info is not None:
            inferred_columns = inferred_info.get_column_names()
            passed_columns = info.get_column_names()
            if inferred_columns != passed_columns:
                raise RuntimeError(
                    f'Provided data schema has columns:\n {passed_columns}, '
                    f'\n which does not match the data schema:\n {inferred_columns}'
                )

        # use inferred info with a warning if not `info` is passed
        else:
            LOG.warning(
                f'Heads up! We are inferring the details of your dataset from '
                f'the dataframe(s) provided. Please take a second to check '
                f'our work.'
                f'\n\nIf the following DatasetInfo is an incorrect '
                f'representation of your data, you can construct a '
                f'DatasetInfo with the DatasetInfo.from_dataframe() method '
                f'and modify that object to reflect the correct details of '
                f'your dataset.'
                f'\n\nAfter constructing a corrected DatasetInfo, please '
                f're-upload your dataset with that DatasetInfo object '
                f'explicitly passed via the `info` parameter of '
                f'FiddlerApi.upload_dataset().'
                f'\n\nYou may need to delete the initially uploaded version'
                f"via FiddlerApi.delete_dataset('{dataset_id}')."
                f'\n\nInferred DatasetInfo to check:'
                f'\n{textwrap.indent(repr(inferred_info), "  ")}'
            )
            info = inferred_info

        if self.strict_mode:
            info.validate()

        # determine whether or not the index of this dataset is a meaningful
        # column that should be written into CSV files
        include_index = next(iter(dataset.values())).index.name is not None

        # dump CSVs to named temp file
        with tempfile.TemporaryDirectory() as tmp:
            csv_paths = list()
            for name, df in dataset.items():
                filename = f'{name}.csv'
                path = Path(tmp) / filename
                csv_paths.append(path)
                LOG.info(f'[{name}] dataset upload: writing csv to {path}')
                df.to_csv(path, index=include_index)

            # add files to the DatasetInfo on the fly
            new_schema = copy.deepcopy(info)
            new_schema.files = [path.name for path in csv_paths]

            # upload the CSV
            LOG.info(f'[{dataset_id}] dataset upload: upload and import csv')
            res = self._upload_dataset_csvs(
                project_id,
                dataset_id,
                csv_paths,
                dataset_info=new_schema,
            )
            return res

    def upload_dataset_from_dir(
        self,
        project_id: str,
        dataset_id: str,
        dataset_dir: Path,
        file_type: str = 'csv',
        file_schema=None,
        size_check_enabled: bool = False,
    ):
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)
        dataset_dir = _type_enforce('dataset_dir', dataset_dir, Path)
        if f'.{file_type}' not in SUPPORTABLE_FILE_EXTENSIONS:
            raise ValueError(
                f'Invalid file_type :{file_type}. Valid file types are : {SUPPORTABLE_FILE_EXTENSIONS}'
            )

        if file_type.endswith('avro'):
            return self.process_avro(project_id, dataset_id, dataset_dir, file_schema)

        if not dataset_dir.is_dir():
            raise ValueError(f'{dataset_dir} is not a directory')

        dataset_yaml = dataset_dir / f'{dataset_id}.yaml'
        if not dataset_yaml.is_file():
            raise ValueError(f'YAML file not found: {dataset_yaml}')
        with dataset_yaml.open() as f:
            dataset_info = DatasetInfo.from_dict(yaml.safe_load(f))
            files = dataset_dir.glob('*.csv')
            csv_files = [x for x in files if x.is_file()]
            logging.info(f'Found CSV file {csv_files}')

            # Lets make sure that we add stats if they are not already there.
            # We need to read the datasets in pandas and create a dataset dictionary
            dataset = {}
            csv_paths = []
            for file in csv_files:
                csv_name = str(file).split('/')[-1]
                csv_paths.append(csv_name)
                name = csv_name[:-4]
                dataset[name] = pd.read_csv(file)

            # check if the dataset exceeds size limits
            abort_upload = self._abort_dataset_upload(
                dataset, size_check_enabled, DATASET_MAX_ROWS
            )
            if abort_upload:
                raise RuntimeError('Dataset upload aborted.')

            # Update stats
            dataset_info = DatasetInfo.update_stats_for_existing_schema(
                dataset, dataset_info
            )
            updated_infos = []
            for item in dataset.values():
                update_info = DatasetInfo.check_and_update_column_info(
                    dataset_info, item
                )
                updated_infos.append(update_info)
            dataset_info = DatasetInfo.as_combination(
                updated_infos, display_name=dataset_info.display_name
            )
            dataset_info.files = csv_paths
            result = self._upload_dataset_csvs(
                project_id, dataset_id, csv_files, dataset_info
            )
            LOG.info(f'Dataset uploaded {result}')

    def upload_dataset_from_file(
        self,
        project_id: str,
        dataset_id: str,
        file_path: str,
        file_type: str = 'csv',
        file_schema=Dict[str, Any],
        info: Optional[DatasetInfo] = None,
        size_check_enabled: bool = False,
    ):
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)
        file_path = _type_enforce('dataset_dir', file_path, Path)

        if file_type.endswith('avro'):
            return self.process_avro(
                project_id,
                dataset_id,
                pathlib.Path(file_path),
                file_schema,
                size_check_enabled,
                info,
            )
        elif file_type.endswith('csv'):
            return self.process_csv(
                project_id,
                dataset_id,
                pathlib.Path(file_path),
                size_check_enabled,
                info,
            )

        raise ValueError(
            f'Invalid file_type :{file_type}. Valid file types are : {SUPPORTABLE_FILE_EXTENSIONS}'
        )

    def process_csv(
        self, project_id, dataset_id, csv_file_path: Path, size_check_enabled, info
    ):
        dataset = {}
        dataset[csv_file_path.name] = pd.read_csv(csv_file_path)
        return self.upload_dataset(
            project_id,
            dataset,
            dataset_id,
            size_check_enabled=size_check_enabled,
            info=info,
        )

    def process_avro(
        self,
        project_id: str,
        dataset_id: str,
        avro_file_path: Path,
        file_schema: Dict,
        size_check_enabled,
        info,
    ):
        dataset = {}
        logging.info(f'avro_file : {avro_file_path}')
        with open(avro_file_path, 'rb') as fh:
            buf = BytesIO(fh.read())
            files = {avro_file_path: FileStorage(buf, avro_file_path)}
            results = upload_dataset(files, 'LOCAL_DISK', 'avro', file_schema)
            df = pd.DataFrame(results)
            dataset[avro_file_path.name] = df
            return self.upload_dataset(
                project_id=project_id,
                dataset_id=dataset_id,
                dataset=dataset,
                size_check_enabled=size_check_enabled,
                info=info,
            )

    def run_model(
        self,
        project_id: str,
        model_id: str,
        df: pd.DataFrame,
        log_events=False,
        casting_type=False,
    ) -> pd.DataFrame:
        """Executes a model in the Fiddler engine on a DataFrame.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.
        :param df: A dataframe contining model inputs as rows.
        :param log_events: Variable determining if the the predictions
            generated should be logged as production traffic
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
        the type referenced in model info. Default to False.

        :returns: A pandas DataFrame containing the outputs of the model.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        if casting_type:
            try:
                model_info = self.get_model_info(project_id, model_id)
            except RuntimeError:
                raise RuntimeError(
                    f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
                )
            df = cast_input_data(df, model_info)

        data_array = _df_to_dict(df)
        payload = dict(
            project_id=project_id,
            model_id=model_id,
            data=data_array,
            logging=log_events,
        )

        payload.pop('project_id')
        payload.pop('model_id')

        path = ['execute', self.org_id, project_id, model_id]
        res = self._call_executor_service(path, json_payload=payload)
        return pd.DataFrame(res)

    def run_explanation(
        self,
        project_id: str,
        model_id: str,
        df: pd.DataFrame,
        explanations: Union[str, Iterable[str]] = 'shap',
        dataset_id: Optional[str] = None,
        casting_type: Optional[bool] = False,
        return_raw_response=False,
    ) -> Union[
        AttributionExplanation,
        MulticlassAttributionExplanation,
        List[AttributionExplanation],
        List[MulticlassAttributionExplanation],
    ]:
        """Executes a model in the Fiddler engine on a DataFrame.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.
        :param df: A dataframe containing model inputs as rows. Only the first
            row will be explained.
        :param explanations: A single string or list of strings specifying
            which explanation algorithms to run.
        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine. Required for most tabular explanations, but
            optional for most text explanations.
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
        the type referenced in model info. Default to False.

        :returns: A single AttributionExplanation if `explanations` was a
            single string, or a list of AttributionExplanation objects if
            a list of explanations was requested.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        if casting_type:
            try:
                model_info = self.get_model_info(project_id, model_id)
            except RuntimeError:
                raise RuntimeError(
                    f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
                )
            df = cast_input_data(df, model_info)

        # Explains a model's prediction on a single instance
        # wrap single explanation name in a list for the API
        if isinstance(explanations, str):
            explanations = (explanations,)

        data_array = _df_to_dict(df)
        payload = dict(
            project_id=project_id,
            model_id=model_id,
            data=data_array[0],
            explanations=[dict(explanation=ex) for ex in explanations],
        )
        if dataset_id is not None:
            payload['dataset'] = dataset_id

        payload.pop('project_id')
        payload.pop('model_id')

        path = ['explain', self.org_id, project_id, model_id]
        res = self._call_executor_service(path, json_payload=payload)

        explanations_list = res['explanations']

        if return_raw_response:
            return explanations_list

        # TODO: enable more robust check for multiclass explanations
        is_multiclass = 'explanation' not in explanations_list[0]
        deserialize_fn = (
            MulticlassAttributionExplanation.from_dict
            if is_multiclass
            else AttributionExplanation.from_dict
        )
        ex_objs = [
            deserialize_fn(explanation_dict) for explanation_dict in explanations_list
        ]
        if len(ex_objs) == 1:
            return ex_objs[0]
        else:
            return ex_objs

    def run_feature_importance(
        self,
        project_id: str,
        model_id: str,
        dataset_id: str,
        dataset_splits: Optional[List[str]] = None,
        slice_query: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Get global feature importance for a model over a dataset.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.
        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine.
        :param dataset_splits: If specified, importance will only be computed
            over these splits. Otherwise, all splits will be used. Only a
            single split is currently supported.
        :param slice_query: A special SQL query.
        :param kwargs: Additional parameters to be passed to the importance
            algorithm. For example, `n_inputs`, `n_iterations`, `n_references`,
            `ci_confidence_level`.
        :return: A named tuple with the explanation results.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        if (
            dataset_splits is not None
            and len(dataset_splits) > 1
            and not isinstance(dataset_splits, str)
        ):
            raise NotImplementedError(
                'Unfortunately, only a single split is '
                'currently supported for feature '
                'importances.'
            )

        source = (
            None
            if dataset_splits is None
            else dataset_splits
            if isinstance(dataset_splits, str)
            else dataset_splits[0]
        )

        payload = dict(
            subject='feature_importance',
            project_id=project_id,
            model_id=model_id,
            dataset_id=dataset_id,
            source=source,
            slice_query=slice_query,
        )
        payload.update(kwargs)

        payload.pop('subject')
        payload.pop('project_id')
        payload.pop('model_id')
        payload['dataset'] = payload.pop('dataset_id')

        path = ['feature_importance', self.org_id, project_id, model_id]
        res = self._call(path, json_payload=payload)
        # wrap results into named tuple
        res = namedtuple('FeatureImportanceResults', res)(**res)
        return res

    def run_fairness(
        self,
        project_id: str,
        model_id: str,
        dataset_id: str,
        protected_features: list,
        positive_outcome: Union[str, int],
        slice_query: Optional[str] = None,
        score_threshold: Optional[float] = 0.5,
    ) -> Dict[str, Any]:
        """Get fairness metrics for a model over a dataset.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.
        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine.
        :param protected_features: List of protected features
        :param positive_outcome: Name or value of the positive outcome
        :param slice_query: If specified, slice the data.
        :param score_threshold: positive score threshold applied to get outcomes
        :return: A dictionary with the fairness metrics, technical_metrics,
        labels distribution and model outcomes distribution
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        if isinstance(protected_features, str):
            protected_features = [protected_features]

        payload = dict(
            subject='fairness',
            project_id=project_id,
            model_id=model_id,
            dataset_id=dataset_id,
            protected_features=protected_features,
            slice_query=slice_query,
            score_threshold=score_threshold,
            positive_outcome=positive_outcome,
        )

        payload.pop('subject')
        payload.pop('project_id')
        payload.pop('model_id')

        path = ['fairness', self.org_id, project_id, model_id]
        res = self._call(path, json_payload=payload)
        return res

    def get_mutual_information(
        self,
        project_id: str,
        dataset_id: str,
        features: list,
        normalized: Optional[bool] = False,
        slice_query: Optional[str] = None,
        sample_size: Optional[int] = None,
        seed: Optional[float] = 0.25,
    ):
        """
        The Mutual information measures the dependency between two random variables.
        It's a non-negative value. If two random variables are independent MI is equal to zero.
        Higher MI values means higher dependency.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine.
        :param features: list of features to compute mutual information with respect to all the variables in the dataset.
        :param normalized: If set to True, it will compute Normalized Mutual Information (NMI)
        :param slice_query: Optional slice query
        :param sample_size: Optional sample size for the selected dataset
        :param seed: Optional seed for sampling
        :return: a dictionary of mutual information w.r.t the given features.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        if isinstance(features, str):
            features = [features]
        if not isinstance(features, list):
            raise ValueError(
                f'Invalid type: {type(features)}. Argument features has to be a list'
            )
        correlation = {}
        for col_name in features:
            payload = dict(
                col_name=col_name,
                normalized=normalized,
                slice_query=slice_query,
                sample_size=sample_size,
                seed=seed,
            )
            path = ['dataset_mutual_information', self.org_id, project_id, dataset_id]
            res = self._call(path, json_payload=payload)
            correlation[col_name] = res
        return correlation

    def create_project(self, project_id: str):
        """Create a new project.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine. Must be a short string without whitespace.

        :returns: Server response for creation action.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)

        self._safe_name_check(project_id, MAX_ID_LEN)
        res = None
        try:
            path = ['new_project', self.org_id, project_id]
            res = self._call(path)
        except Exception as e:
            if 'already exists' in str(e):
                print('Project already exists, no change.')
            else:
                raise e

        return res

    def share_project(
        self,
        project_name: str,
        role: str,
        user_name: Optional[str] = None,
        team_name: Optional[str] = None,
    ):
        """Share a project with other users and/or teams.

        :param project_name: The name of the project to share.
        :param role: one of ["READ", "WRITE", "OWNER"].
        :param user_name: (optional) username, typically an email address.
        :param team_name: (optional) name of the team.

        :returns: Server response for creation action.
        """
        if user_name is None and team_name is None:
            err = 'one of user_name, team_name must be provided'
            raise ValueError(err)

        if user_name is not None and team_name is not None:
            err = 'Only one of user_name or team_name must be provided'
            raise ValueError(err)

        if role not in ['READ', 'WRITE', 'OWNER']:
            err = 'role must be one of READ, WRITE, or OWNER'
            raise ValueError(err)

        payload = {
            'role': role,
            'user_name': user_name,
            'team_name': team_name,
        }

        path = ['apply_project_role', self.org_id, project_name]
        return self._call(path, json_payload=payload)

    def unshare_project(
        self,
        project_name: str,
        role: str,
        user_name: Optional[str] = None,
        team_name: Optional[str] = None,
    ):
        """un-Share a project with other users and/or teams.

        :param project_name: The name of the project.
        :param role: one of ["READ", "WRITE", "OWNER"].
        :param user_name: (optional) username, typically an email address.
        :param team_name: (optional) name of the team.

        :returns: Server response for creation action.
        """
        if user_name is None and team_name is None:
            err = 'one of user_name, team_name must be provided'
            raise ValueError(err)

        if user_name is not None and team_name is not None:
            err = 'Only one of user_name or team_name must be provided'
            raise ValueError(err)

        if role not in ['READ', 'WRITE', 'OWNER']:
            err = 'role must be one of READ, WRITE, or OWNER'
            raise ValueError(err)

        payload = {
            'role': role,
            'user_name': user_name,
            'team_name': team_name,
        }

        path = ['delete_project_role', self.org_id, project_name]
        return self._call(path, json_payload=payload)

    def list_org_roles(self):
        """List the users in the organization.

        :returns: list of users and their roles in the organization.
        """
        path = ['roles', self.org_id]
        return self._call(path, is_get_request=True)

    def list_project_roles(self, project_name: str):
        """List the users and teams with access to a given project.

        :returns: list of users and teams with access to a given project.
        """
        path = ['roles', self.org_id, project_name]
        return self._call(path, is_get_request=True)

    def list_teams(self):
        """List the teams and the members in each team.

        :returns: dictionary with teams as keys and list of members as values.
        """
        path = ['teams', self.org_id]
        return self._call(path, is_get_request=True)

    def _create_model(
        self,
        project_id: str,
        dataset_id: str,
        target: str,
        features: Optional[List[str]] = None,
        train_splits: Optional[List[str]] = None,
        model_id: str = 'fiddler_generated_model',
        model_info: Optional[ModelInfo] = None,
    ):
        """Trigger auto-modeling on a dataset already uploaded to Fiddler.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.

        :param dataset_id: The unique identifier of the dataset in the
            Fiddler engine.
        :param target: The column name of the target to be modeled.
        :param features: If specified, a list of column names to use as
            features. If not specified, all non-target columns will be used
            as features.
        :param train_splits: A list of splits to train on. If not specified,
            all splits will be used as training data. Currently only a single
            split can be specified if `train_splits` is not None.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine.

        :returns: Server response for creation action.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        self._safe_name_check(project_id, MAX_ID_LEN)
        self._safe_name_check(model_id, MAX_ID_LEN)
        if train_splits is not None and len(train_splits) > 1:
            raise NotImplementedError(
                'Sorry, currently only single-split training is '
                'supported. Please only pass a maximum of one element to '
                '`train_splits`.'
            )
        source = None if train_splits is None else train_splits[0]
        dataset_column_names = self.get_dataset_info(
            project_id, dataset_id
        ).get_column_names()

        # raise exception if misspelled target
        if target not in dataset_column_names:
            raise ValueError(
                f'Target "{target}" not found in the columns of '
                f'dataset {dataset_id} ({dataset_column_names})'
            )

        # raise if target in features or features not in columns
        if features is not None:
            if target in features:
                raise ValueError(f'Target "{target}" cannot also be in ' f'features.')
            features_not_in_dataset = set(features) - set(dataset_column_names)
            if len(features_not_in_dataset) > 0:
                raise ValueError(
                    f'All features should be in the dataset, but '
                    f'the following features were not found in '
                    f'the dataset: {features_not_in_dataset}'
                )

        # use all non-target columns from dataset if no features are specified
        if features is None:
            features = list(dataset_column_names)
            features.remove(target)

        payload = {
            'dataset': dataset_id,
            'model_name': model_id,
            'source': source,
            'inputs': features,
            'targets': [target],
        }

        if model_info:
            if self.strict_mode:
                model_info.validate()
            payload['model_info'] = dict(model=model_info.to_dict())

        path = ['generate', self.org_id, project_id]
        result = self._call_executor_service(path, json_payload=payload)
        return result

    def _upload_model_custom(
        self,
        artifact_path: Path,
        info: ModelInfo,
        project_id: str,
        model_id: str,
        associated_dataset_ids: Optional[List[str]] = None,
        deployment_type: Optional[
            str
        ] = 'predictor',  # model type. one of {'predictor', 'executor'}
        image_uri: Optional[str] = None,  # image to be used for newly uploaded model
        namespace: Optional[str] = 'default',  # kubernetes namespace
        port: Optional[int] = 5100,  # port on which model is served
        replicas: Optional[int] = 1,  # number of replicas
        cpus: Optional[int] = 0.25,  # number of CPU cores
        memory: Optional[str] = '128m',  # amount of memory required.
        gpus: Optional[int] = 0,  # number of GPU cores
        await_deployment: Optional[bool] = True,  # wait for deployment
    ):
        """Uploads a custom model object to the Fiddler engine along with
            custom glue-code for running the model. Optionally, a new runtime
            (k8s deployment) can be specified for the model via
            the deployment_type and the image_uri parameters.

            Note: The parameters namespace, port, replicas, cpus, memory, gpus,
            await_deployment are only used if an image_uri is specified.

        :param artifact_path: A path to a directory containing all of the
            model artifacts needed to run the model. This includes a
            `package.py` file with the glue code needed to run the model.
        :param info: A ModelInfo object describing the details of the model.
        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param model_id: The unique identifier of the model in the specified
            project on the Fiddler engine. Must be a short string without
            whitespace.
        :param associated_dataset_ids: The unique identifiers of datasets in
            the Fiddler engine to associate with the model.

        :param deployment_type: One of {'predictor', 'executor'}
        'predictor': where the model just exposes a `/predict` endpoint
                     - typically simple sklearn like models
        'executor': where fiddler needs the model internals
                     - typically deep models like tensorflow and pytorch etc

        :param image_uri: A URI of the form <registry>/<image-name>:<tag> which
            if specified will be used to create a new runtime and then serve the
            model.

        :param namespace: The kubernetes namespace to use for the newly created
            runtime.

        :param port: The port to use for the newly created runtime.

        :param replicas: The number of replicas running the model.
        :param cpus: The number of CPU cores reserved per replica.
        :param memory: The amount of memory reservation per replica.
        :param gpus: The number of GPU cores reserved per replica.

        :param await_deployment: whether to block until deployment completes.

        :returns: Server response for upload action.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        self._safe_name_check(model_id, MAX_ID_LEN)

        if not artifact_path.is_dir():
            raise ValueError(f'The {artifact_path} must be a directory.')

        model_info = FiddlerApi._add_dataset_ids_to_model_info(
            info, associated_dataset_ids
        )

        if self.strict_mode:
            model_info.validate()

        # upload the model
        payload = dict(
            project=project_id,
            model=model_id,
            model_schema=dict(model=model_info.to_dict()),
            framework=info.framework,
            upload_as_archive=True,
            model_type='custom',
            deployment_type=deployment_type,
            image=image_uri,
            namespace=namespace,
            port=port,
            replicas=replicas,
            cpus=cpus,
            memory=memory,
            gpus=gpus,
            await_deployment=await_deployment,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tarfile_path = Path(tmp) / 'files'
            shutil.make_archive(
                base_name=str(Path(tmp) / 'files'),
                format='tar',
                root_dir=str(artifact_path),
                base_dir='.',
            )
            LOG.info(
                f'[{model_id}] model upload: uploading custom model from'
                f' artifacts in {str(artifact_path)} tarred to '
                f'{str(tarfile_path)}'
            )

            endpoint_path = ['model_upload', self.org_id, project_id]
            result = self._call(
                endpoint_path, json_payload=payload, files=[Path(tmp) / 'files.tar']
            )
            return result

    def upload_model_package(
        self,
        artifact_path: Path,
        project_id: str,
        model_id: str,
        deployment_type: Optional[
            str
        ] = 'predictor',  # model deployment type. One of {'predictor', 'executor'}
        image_uri: Optional[str] = None,  # image to be used for newly uploaded model
        namespace: Optional[str] = 'default',  # kubernetes namespace
        port: Optional[int] = 5100,  # port on which model is served
        replicas: Optional[int] = 1,  # number of replicas
        cpus: Optional[int] = 0.25,  # number of CPU cores
        memory: Optional[str] = '128m',  # amount of memory required.
        gpus: Optional[int] = 0,  # number of GPU cores
        await_deployment: Optional[bool] = True,  # wait for deployment
    ):
        # Type enforcement
        artifact_path = _type_enforce('artifact_path', artifact_path, Path)
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        if not artifact_path.is_dir():
            raise ValueError(f'not a valid model dir: {artifact_path}')
        yaml_file = artifact_path / 'model.yaml'
        if not yaml_file.is_file():
            raise ValueError(f'Model yaml not found {yaml_file}')
        with yaml_file.open() as f:
            model_info = ModelInfo.from_dict(yaml.safe_load(f))
            self._upload_model_custom(
                artifact_path,
                model_info,
                project_id,
                model_id,
                deployment_type=deployment_type,
                image_uri=image_uri,
                namespace=namespace,
                port=port,
                replicas=replicas,
                cpus=cpus,
                memory=memory,
                gpus=gpus,
                await_deployment=await_deployment,
            )

    @staticmethod
    def _add_dataset_ids_to_model_info(model_info, associated_dataset_ids):
        model_info = copy.deepcopy(model_info)
        # add associated dataset ids to ModelInfo
        if associated_dataset_ids is not None:
            for dataset_id in associated_dataset_ids:
                assert (
                    ' ' not in dataset_id
                ), 'Dataset identifiers should not contain whitespace'
            model_info.misc['datasets'] = associated_dataset_ids
        return model_info

    def _trigger_model_predictions(
        self, project_id: str, model_id: str, dataset_id: str
    ):
        """Makes the Fiddler service compute and cache model predictions on a
        dataset."""
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        payload = dict(model=model_id, dataset=dataset_id)
        result = self._call_executor_service(
            ['dataset_predictions', self.org_id, project_id], payload
        )

        return result

    def trigger_pre_computation(
        self,
        project_id: str,
        model_id: str,
        dataset_id: str,
        overwrite_cache: Optional[bool] = False,
        batch_size: Optional[int] = 10,
        calculate_predictions: Optional[bool] = True,
        cache_global_pdps: Optional[bool] = False,
        cache_global_impact_importance: Optional[bool] = True,
        cache_dataset=False,
    ):
        """Triggers various precomputation steps within the Fiddler service based on input parameters.

        :param project_id:                        the project to which the model whose events are
                                                  being published belongs.
        :param model_id:                          the model whose events are being published.
        :param dataset_id:                        id of the dataset to be used.
        :param overwrite_cache:                   Boolean indicating whether to overwrite previously cached
                                                  information.
        :param batch_size:                        Batch size of global PDP calculation.
        :param calculate_predictions:             Boolean indicating whether to pre-calculate and store model
                                                  predictions.
        :param cache_global_pdps:                 Boolean indicating whether to pre-calculate and cache global partial
                                                  dependence plots.
        :param cache_global_impact_importance:    Boolean indicating whether to pre-calculate and global feature impact
                                                  and global feature importance.
        :param cache_dataset:                     Boolean indicating whether to cache dataset histograms.
                                                  Should be set to True for large datasets.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        if calculate_predictions:
            print(
                f'Beginning to process and upload predictions for dataset {dataset_id} with model {model_id}...'
            )

            path = ['dataset_predictions', self.org_id, project_id]
            payload = dict(model=model_id, dataset=dataset_id)
            result = self._call_executor_service(path, payload)

            print(f'{result}\n')

        if cache_global_pdps or cache_global_impact_importance:
            print(
                f'Beginning to precache for dataset {dataset_id} with model {model_id}...'
            )

            path = ['precache_globals', self.org_id, project_id, model_id]
            payload = {
                'dataset_id': dataset_id,
                'cache_global_pdps': cache_global_pdps,
                'cache_global_impact_importance': cache_global_impact_importance,
                'overwrite_cache': overwrite_cache,
                'batch_size': batch_size,
            }

            result = self._call_executor_service(path, payload, stream=True)
            for res in result:
                print_streamed_result(res)

        if cache_dataset:
            print('Beginning to cache dataset')
            try:
                model_info = self.get_model_info(project_id, model_id)
            except RuntimeError:
                raise RuntimeError(
                    f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
                )
            col_name = model_info.inputs[0].name
            try:
                path = ['dataset_histogram', self.org_id, project_id, model_id]
                payload = {}
                payload['feature'] = col_name
                res = self._call(path, json_payload=payload)
            except Exception as e:
                print('Failed to cache dataset, error message: ')
                raise e

    def initialize_monitoring(  # noqa
        self,
        project_id: str,
        model_id: str,
        enable_modify: Optional = False,
        verbose: Optional[bool] = False,
    ):
        """
        Ensure that monitoring has been setup and Fiddler is ready to ingest events.

        :param project_id:          The project for which to initialize monitoring.
        :param model_id:            The model for which to initialize monitoring.
        :param model_id:            The model for which to initialize monitoring.
        :param enable_modify:       Grant the Fiddler backend permission to
                                    modify model related objects, schema, etc.

                                    Can be bool  `True`/`False`, indicating global
                                    write/read-only permission.

                                    Alternatively, can be a sequence of elements
                                    from `fiddler.core_objects.InitMonitoringModifications`,
                                    in which case all listed elements will be
                                    assumed to be modifiable, and omitted ones
                                    will be read-only.
        :param verbose:             Bool indicating whether to run in verbose
                                    mode with longer debug messages for errors.

        :returns bool indicating whether monitoring could be setup correctly.
        """
        # TODO: only trigger model predictions if they do not already exist
        model_info = None
        dataset_id = None
        try:
            model_info = self.get_model_info(project_id, model_id)
        except Exception as e:
            print(
                f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
            )
            raise e
        try:
            assert model_info is not None
            dataset_id = model_info.datasets[0]
            assert dataset_id is not None
        except Exception as e:
            print(
                f'Unable to infer dataset from model_info for given project_id={project_id} and model_id={model_id}. Did your model_info specify a dataset?'
            )
            if verbose:
                print('The inferred dataset_id was: ')
                print(dataset_id)
                print()
                print('The inferred model_info was: ')
                print(model_info)
            raise e
        predictions_exist = False
        try:
            path = ['model_predictions_exist', self.org_id, project_id]
            payload = {
                'model': model_id,
                'dataset': dataset_id,
            }  # is dataset_id same as dataset_name?
            predictions_exist = self._call(path, json_payload=payload)
        except Exception as e:
            if verbose:
                print('Failed to check for predictions, regenerating by default')
                print(e)
            LOG.warning('Failed to check for predictions, regenerating by default')
            LOG.warning(e)
        if not predictions_exist:
            self._trigger_model_predictions(project_id, model_id, dataset_id)
        else:
            LOG.info(
                f'Predictions already exist for model={model_id}, dataset={dataset_id}'
            )
        default_modify = False
        if type(enable_modify) == bool:
            default_modify = enable_modify
        enable_backend_modifications = {
            check.value: default_modify
            for check in possible_init_monitoring_modifications
        }
        if type(enable_modify) == list or type(enable_modify) == tuple:
            for mod in enable_modify:
                if type(mod) == InitMonitoringModifications:
                    mod = mod.value
                enable_backend_modifications[mod] = True
        elif type(enable_modify) == bool:
            pass
        else:
            raise NotImplementedError

        overall_result = True
        init_result = None
        try:
            path = ['init_monitoring', self.org_id, project_id, model_id]
            payload = {}
            payload['enable_modifications'] = enable_backend_modifications
            init_result = self._call(path, json_payload=payload)
        except Exception as e:
            print('Failed to setup monitoring, error message: ')
            raise e
        if init_result is not None:
            if init_result['success']:
                if verbose:
                    print(f"ERRORS: {init_result['errors']}")
                    print(f"MESSAGE: {init_result['message']}")
            else:
                print(f"ERRORS: {init_result['errors']}")
                print(f"MESSAGE: {init_result['message']}")
        else:
            print('Failed to setup monitoring, could not parse server response.')
            init_result = {'success': False}
        overall_result = overall_result and init_result['success']
        # For now, we only permit precomputation if no failures are found # TODO: allow precomputations for incomplete schema?
        if init_result['success'] is False:
            return False
        if verbose:
            print('Precomputing Dataset Histograms')
        precompute_result = None
        try:
            path = ['precompute', self.org_id, project_id, model_id]
            payload = {
                # 'dataset': dataset_id,
            }
            precompute_result = self._call(path, json_payload=payload)
        except Exception as e:
            print('Failed to precompute histograms, error message: ')
            raise e
        if precompute_result is not None:
            if precompute_result['success']:
                if verbose:
                    print('Successfully precomputed histograms, details: ')
                    print(precompute_result['message'])
            else:
                print('Failed to precompute histograms, details: ')
                print(precompute_result['message'])
        else:
            print('Failed to precompute histograms, could not parse server response.')
            precompute_result = {'success': False}
        overall_result = overall_result and precompute_result['success']

        if verbose:
            print(
                f'overall_result: {overall_result},\n\t- init_result: {init_result},\n\t- precompute_result: {precompute_result}'
            )
        return overall_result

    def publish_event(
        self,
        project_id: str,
        model_id: str,
        event: dict,
        event_id: Optional[str] = None,
        update_event: Optional[bool] = None,
        event_timestamp: Optional[int] = None,
        timestamp_format: Optional[FiddlerTimestamp] = FiddlerTimestamp.INFER,
        casting_type: Optional[bool] = False,
        dry_run: Optional[bool] = False,
    ):
        """
        Publishes an event to Fiddler Service.
        :param project_id: The project to which the model whose events are being published belongs
        :param model_id: The model whose events are being published
        :param dict event: Dictionary of event details, such as features and predictions.
        :param event_id: Unique str event id for the event
        :param update_event: Bool indicating if the event is an update to a previously published row
        :param event_timestamp: The UTC timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param timestamp_format:   Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
        the type referenced in model info. Default to False.
        :param dry_run: If true, the event isnt published and instead the user gets a report which shows
        IF the event along with the model would face any problems with respect to monitoring

        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        event = _type_enforce('event', event, dict)
        if event_id:
            event_id = _type_enforce('event_id', event_id, str)

        if casting_type:
            try:
                model_info = self.get_model_info(project_id, model_id)
            except RuntimeError:
                raise RuntimeError(
                    f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
                )
            event = cast_input_data(event, model_info)

        event['__timestamp_format'] = timestamp_format.value

        if update_event:
            event['__event_type'] = 'update_event'
            event['__updated_at'] = event_timestamp
            if event_id is None:
                raise ValueError('An update event needs an event_id')
        else:
            event['__event_type'] = 'execution_event'
            event['__occurred_at'] = event_timestamp

        if event_id is not None:
            event['__event_id'] = event_id

        if dry_run:
            violations = self._pre_flight_monitoring_check(project_id, model_id, event)
            violations_list = []
            print('\n****** publish_event dry_run report *****')
            print(f'Found {len(violations)} Violations:')
            for violation in violations:
                violations_list.append(
                    {'type': violation.type.value, 'desc': violation.desc}
                )
                print(f'Type: {violation.type.value: <11}{violation.desc}')
            result = json.dumps(violations_list)
        else:
            path = ['external_event', self.org_id, project_id, model_id]
            # The ._call uses `timeout` and `num_tries` logic due to an issue with Mac/Docker.
            # This is only enabled using the env variable `FIDDLER_RETRY_PUBLISH`; otherwise it
            # is a normal ._call function
            result = self._call(path, event, timeout=2, num_tries=5)

        return result

    def _pre_flight_monitoring_check(self, project_id, model_id, event):
        violations = []
        violations += self._basic_monitoring_tests(project_id, model_id)
        if len(violations) == 0:
            model_info = self.get_model_info(project_id, model_id)
            dataset_info = self.get_dataset_info(project_id, model_info.datasets[0])
            violations += self._basic_drift_checks(project_id, model_info, model_id)
            violations += self.monitoring_validator.pre_flight_monitoring_check(
                event, model_info, dataset_info
            )
        return violations

    def _basic_monitoring_tests(self, project_id, model_id):
        """ Basic checks which would prevent monitoring from working altogether. """
        violations = []
        try:
            model_info = self.get_model_info(project_id, model_id)
        except RuntimeError:
            msg = f'Error: Model:{model_id} in project:{project_id} does not exist'
            violations.append(MonitoringViolation(MonitoringViolationType.FATAL, msg))
            return violations

        try:
            _ = self.get_dataset_info(project_id, model_info.datasets[0])
        except RuntimeError:
            msg = f'Error: Dataset:{model_info.datasets[0]} does not exist'
            violations.append(MonitoringViolation(MonitoringViolationType.FATAL, msg))
            return violations

        return violations

    def add_monitoring_config(
        self,
        config_info: dict,
        project_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ):
        """Adds a config for either an entire org, or project or a model.
        Here's a sample config:
        {
            'min_bin_value': 3600, # possible values 300, 3600, 7200, 43200, 86400, 604800 secs
            'time_ranges': ['Day', 'Week', 'Month', 'Quarter', 'Year'],
            'default_time_range': 7200,
            'tag': 'anything you want'
        }
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        path = ['monitoring_setup', self.org_id]
        if project_id:
            path.append(project_id)
        if model_id:
            if not project_id:
                raise ValueError(
                    'We need to have a `project_id` when a model is specified'
                )
            path.append(model_id)

        result = self._call(path, config_info)
        return result

    def publish_events_log(
        self,
        project_id: str,
        model_id: str,
        logs: pd.DataFrame,
        force_publish: Optional[bool] = None,
        ts_column: Optional[str] = None,
        default_ts: Optional[int] = None,
        num_threads: Optional[int] = 1,
        batch_size: Optional[int] = None,
        casting_type: Optional[bool] = False,
    ):
        """
        [SOON TO BE DEPRECATED] Publishes prediction log to Fiddler Service.
        :param project_id:    The project to which the model whose events are being published belongs
        :param model_id:      The model whose events are being published
        :param logs:          Data frame of event details, such as features and predictions.
        :param force_publish: Continue with publish even if all input and output columns not in log.
        :param ts_column:     Column to extract timestamp value from.
                              Timestamp must be UTC in format: `%Y-%m-%d %H:%M:%S.%f` (e.g. 2020-01-01 00:00:00.000000)
                              or as the timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param default_ts:    Default timestamp to use if ts_column not specified.
                              Must be given as the timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param num_threads:   Number of threads to parallelize this function over. Dataset will be divided evenly
                              over the number of threads.
        :param batch_size:    Size of dataframe to publish in any given run.
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
        the type referenced in model info. Default to False.

        """
        # Type enforcement
        print(
            'WARNING: This method will be deprecated in a future version. Please use the method `publish_events_batch` instead.'
        )
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        if num_threads < 1 or num_threads > 20:
            raise ValueError(
                'Please adjust parameter `num_threads` to be between 1 and 20.'
            )
        if batch_size and (batch_size < 1 or batch_size > 100000):
            raise ValueError(
                'Please adjust parameter `batch_size` to be between 1 and 100000, or type `None`.'
            )
        if default_ts and not isinstance(default_ts, int):
            raise ValueError(
                'Please adjust parameter `default_ts` to be of type `int` or type `None`.'
            )
        model_info = self.get_model_info(project_id, model_id)
        if casting_type:
            logs = cast_input_data(logs, model_info)

        log_columns = [c for c in list(logs.columns)]
        in_columns = [c.name for c in model_info.inputs]
        in_not_found = [c for c in in_columns if c not in log_columns]
        out_columns = [c.name for c in model_info.outputs]
        out_not_found = [c for c in out_columns if c not in log_columns]
        if (out_not_found or in_not_found) and not force_publish:
            raise ValueError(
                f'Model output columns "{out_not_found}" or input columns "{in_not_found}"'
                f'not found in logs. If this is expected try again with force_publish=True.'
            )

        payload = dict()
        if ts_column is not None:
            if ts_column not in log_columns:
                raise ValueError(f'Did not find {ts_column} in the logs columns.')
            payload['ts_column'] = ts_column
        else:
            if default_ts is None:
                default_ts = int(round(time.time() * 1000))
            payload['default_ts'] = default_ts
        include_index = logs.index.name is not None

        worker_lock = threading.Lock()
        workers_list = []

        class _PublishEventsLogWorker(threading.Thread):
            """
            Handles the call to `publish_events_log`
            """

            def __init__(
                self,
                thread_id,
                df,
                client,
                payload,
                org_id,
                project_id,
                model_id,
                include_index,
                batch_size,
                worker_lock,
                only_worker,
            ):
                threading.Thread.__init__(self)
                self.thread_id = thread_id
                self.df = df
                self.client = client
                self.payload = copy.deepcopy(payload)
                self.org_id = org_id
                self.project_id = project_id
                self.model_id = model_id
                self.include_index = include_index
                self.batch_size = batch_size
                self.worker_lock = worker_lock
                self.only_worker = only_worker
                self.path = [
                    'publish_events_log',
                    self.org_id,
                    self.project_id,
                    self.model_id,
                ]

            def run(self):
                df_batches = []
                if self.batch_size:
                    # Divide dataframe into size of self.batch_size
                    num_chunks = math.ceil(len(self.df) / self.batch_size)
                    for j in range(num_chunks):
                        df_batches.append(
                            self.df[j * self.batch_size : (j + 1) * self.batch_size]
                        )
                else:
                    df_batches.append(self.df)

                with tempfile.TemporaryDirectory() as tmp:
                    # To maintain the same data types during transportation from client
                    #  to server, we must explicitly send and recreate the data types through
                    #  a file. Otherwise, Pandas.from_csv() will convert quoted strings to integers.
                    #  See: https://github.com/pandas-dev/pandas/issues/35713
                    log_path = Path(tmp) / 'log.csv'
                    dtypes_path = Path(tmp) / 'dtypes.csv'
                    self.df.dtypes.to_frame('types').to_csv(dtypes_path)
                    csv_paths = [dtypes_path, log_path]

                    for curr_batch in df_batches:
                        # Overwrite CSV with current batch
                        curr_batch.to_csv(log_path, index=self.include_index)

                        result = self.client._call(
                            self.path, json_payload=self.payload, files=csv_paths
                        )

                        with self.worker_lock:
                            # Used to prevent printing clash
                            if self.only_worker:
                                print(result)
                            else:
                                print(f'thread_id {self.thread_id}: {result}')

        # Divide dataframe evenly amongst each thread
        df_split = np.array_split(logs, num_threads)

        for i in range(num_threads):
            workers_list.append(
                _PublishEventsLogWorker(
                    i,
                    df_split[i],
                    self,
                    payload,
                    self.org_id,
                    project_id,
                    model_id,
                    include_index,
                    batch_size,
                    worker_lock,
                    num_threads == 1,
                )
            )
            workers_list[i].start()

        for i in range(num_threads):
            workers_list[i].join()

    def publish_events_batch(  # noqa
        self,
        project_id: str,
        model_id: str,
        batch_source: Union[pd.DataFrame, str],
        id_field: Optional[str] = None,
        update_event: Optional[bool] = False,
        timestamp_field: Optional[str] = None,
        timestamp_format: Optional[FiddlerTimestamp] = FiddlerTimestamp.INFER,
        data_source: Optional[BatchPublishType] = None,
        casting_type: Optional[bool] = False,
        credentials: Optional[dict] = None,
        group_by: Optional[str] = None,
    ):
        """
        Publishes a batch events object to Fiddler Service.
        :param project_id:    The project to which the model whose events are being published belongs.
        :param model_id:      The model whose events are being published.
        :param batch_source:  Batch object to be published. Can be one of: Pandas DataFrame, CSV file, PKL Pandas DataFrame, or Parquet file.
        :param id_field:  Column to extract id value from.
        :param update_event: Bool indicating if the events are updates to previously published rows
        :param timestamp_field:     Column to extract timestamp value from.
                              Timestamp must match the specified format in `timestamp_format`.
        :param timestamp_format:   Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param data_source:   Source of batch object. In case of failed inference, can be one of:
                                - BatchPublishType.DATAFRAME
                                - BatchPublishType.LOCAL_DISK
                                - BatchPublishType.AWS_S3
                                - BatchPublishType.GCP_STORAGE
        :param casting_type: Bool indicating if fiddler should try to cast the data in the event with
                             the type referenced in model info. Default to False.
        :param credentials:  Dictionary containing authorization for AWS or GCP.

                             For AWS S3, list of expected keys are
                              ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']
                              with 'aws_session_token' being applicable to the AWS account being used.

                             For GCP, list of expected keys are
                              ['gcs_access_key_id', 'gcs_secret_access_key', 'gcs_session_token']
                              with 'gcs_session_token' being applicable to the GCP account being used.
        :param group_by: Column to group events together for Model Performance metrics. For example,
                         in ranking models that column should be query_id or session_id, used to
                         compute NDCG and MAP. Be aware that the batch_source file/dataset provided should have
                         events belonging to the SAME query_id/session_id TOGETHER and cannot be mixed
                         in the file. For example, having a file with rows belonging to query_id 31,31,31,2,2,31,31,31
                         would not work. Please sort the file by group_by group first to have rows with
                         the following order: query_id 31,31,31,31,31,31,2,2
        """

        def infer_source(source_object):
            """
            Attempts to infer the type of object passed to batch publish
            """
            if isinstance(source_object, pd.DataFrame):
                return BatchPublishType.DATAFRAME

            if isinstance(source_object, str):
                if re.match(r'((s3-|s3\.)?(.*)\.amazonaws\.com|^s3://)', source_object):
                    return BatchPublishType.AWS_S3
                if re.match(
                    r'((gs-|gs\.)?(.*)\.cloud.google\.com|^gs://)', source_object
                ):
                    return BatchPublishType.GCP_STORAGE
                return BatchPublishType.LOCAL_DISK

            return BatchPublishType.UNKNOWN

        path = ['publish_events_batch', self.org_id, project_id, model_id]

        if data_source is None:
            data_source = infer_source(batch_source)
            print(
                f'`data_source` not specified. Inferred `data_source` as '
                f'BatchPublishType.{BatchPublishType(data_source.value).name}'
            )
        if data_source not in [
            BatchPublishType.DATAFRAME,
            BatchPublishType.LOCAL_DISK,
            BatchPublishType.AWS_S3,
            BatchPublishType.GCP_STORAGE,
        ]:
            raise ValueError('Please specify a valid BatchPublishType')

        payload = dict()
        payload['casting_type'] = casting_type
        payload['is_update_event'] = update_event
        payload['data_source'] = data_source.value
        payload['timestamp_format'] = timestamp_format.value
        if id_field is not None:
            payload['id_field'] = id_field
        if timestamp_field is not None:
            payload['timestamp_field'] = timestamp_field
        if group_by is not None:
            payload['group_by'] = group_by

        # Default to current time for case when no timestamp field specified
        if timestamp_field is None:
            curr_timestamp = formatted_utcnow(
                milliseconds=int(round(time.time() * 1000))
            )
            print(
                f'`timestamp_field` not specified. Using current UTC time `{curr_timestamp}` as default'
            )
            payload['default_timestamp'] = curr_timestamp

        # Dataframe
        if data_source == BatchPublishType.DATAFRAME:
            # Converting dataframe to local disk format for transmission
            payload['data_source'] = BatchPublishType.LOCAL_DISK.value
            df = batch_source.copy()
            if df.index.name is not None:
                df.reset_index(inplace=True)
            clean_df_types(df)

            with tempfile.TemporaryDirectory() as tmp:
                # To maintain the same data types during transportation from client
                #  to server, we must explicitly send and recreate the data types through
                #  a file. Otherwise, Pandas.from_csv() will convert quoted strings to integers.
                #  See: https://github.com/pandas-dev/pandas/issues/35713
                log_path = Path(tmp) / 'log.csv'
                dtypes_path = Path(tmp) / 'dtypes.csv'
                df.dtypes.to_frame('types').to_csv(dtypes_path)
                csv_paths = [dtypes_path, log_path]

                # Overwrite CSV with current batch
                df.to_csv(log_path, index=False)

                result = self._call(
                    path, json_payload=payload, files=csv_paths, stream=True
                )

                final_return = None
                for res in result:
                    print_streamed_result(res)
                    final_return = res

                return final_return

        # Local disk
        if data_source == BatchPublishType.LOCAL_DISK:
            local_file_path = batch_source
            result = self._call(
                path,
                json_payload=payload,
                files=[Path(local_file_path)],
                stream=True,
            )

            final_return = None
            for res in result:
                print_streamed_result(res)
                final_return = res

            return final_return

        # S3
        if data_source == BatchPublishType.AWS_S3:
            s3_sri_path = batch_source
            # Validate S3 creds
            validate_s3_uri_access(s3_sri_path, credentials, throw_error=True)
            with tempfile.NamedTemporaryFile() as tmp:
                # tmp is a dummy file passed to BE for ease of API consolidation
                payload['file_path'] = s3_sri_path
                payload['credentials'] = credentials
                result = self._call(
                    path, json_payload=payload, files=[Path(tmp.name)], stream=True
                )

                final_return = None
                for res in result:
                    print_streamed_result(res)
                    final_return = res

                return final_return

        # GCP
        if data_source == BatchPublishType.GCP_STORAGE:
            gcp_sri_path = batch_source
            # Validate GCS creds
            if credentials is not None:
                gcs_credentials = {}
                if 'gcs_access_key_id' in credentials:
                    gcs_credentials['aws_access_key_id'] = credentials[
                        'gcs_access_key_id'
                    ]
                if 'gcs_secret_access_key' in credentials:
                    gcs_credentials['aws_secret_access_key'] = credentials[
                        'gcs_secret_access_key'
                    ]
                if 'gcs_session_token' in credentials:
                    gcs_credentials['aws_session_token'] = credentials[
                        'gcs_session_token'
                    ]
            else:
                gcs_credentials = None
            validate_gcp_uri_access(gcp_sri_path, gcs_credentials, throw_error=True)
            with tempfile.NamedTemporaryFile() as tmp:
                # tmp is a dummy file passed to BE for ease of API consolidation
                payload['file_path'] = gcp_sri_path
                payload['credentials'] = gcs_credentials
                result = self._call(
                    path, json_payload=payload, files=[Path(tmp.name)], stream=True
                )

                final_return = None
                for res in result:
                    print_streamed_result(res)
                    final_return = res

                return final_return

    def publish_events_batch_schema(  # noqa
        self,
        batch_source: Union[pd.DataFrame, str],
        publish_schema: Dict[str, Any],
        data_source: Optional[BatchPublishType] = None,
        credentials: Optional[dict] = None,
        group_by: Optional[str] = None,
    ):
        """
        Publishes a batch events object to Fiddler Service.
        :param batch_source:  Batch object to be published. Can be one of: Pandas DataFrame, CSV file, PKL Pandas DataFrame, or Parquet file.
        :param publish_schema: Dict object specifying layout of data.
        :param data_source:   Source of batch object. In case of failed inference, can be one of:
                                - BatchPublishType.DATAFRAME
                                - BatchPublishType.LOCAL_DISK
                                - BatchPublishType.AWS_S3
                                - BatchPublishType.GCP_STORAGE
        :param credentials:  Dictionary containing authorization for AWS or GCP.

                             For AWS S3, list of expected keys are
                              ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']
                              with 'aws_session_token' being applicable to the AWS account being used.

                             For GCP, list of expected keys are
                              ['gcs_access_key_id', 'gcs_secret_access_key', 'gcs_session_token']
                              with 'gcs_session_token' being applicable to the GCP account being used.
        :param group_by: Column to group events together for Model Performance metrics. For example,
                         in ranking models that column should be query_id or session_id, used to
                         compute NDCG and MAP.
        """

        def infer_source(source_object):
            """
            Attempts to infer the type of object passed to batch publish
            """
            if isinstance(source_object, pd.DataFrame):
                return BatchPublishType.DATAFRAME

            if isinstance(source_object, str):
                if re.match(r'((s3-|s3\.)?(.*)\.amazonaws\.com|^s3://)', source_object):
                    return BatchPublishType.AWS_S3
                if re.match(
                    r'((gs-|gs\.)?(.*)\.cloud.google\.com|^gs://)', source_object
                ):
                    return BatchPublishType.GCP_STORAGE
                return BatchPublishType.LOCAL_DISK

            return BatchPublishType.UNKNOWN

        path = ['publish_events_batch_schema', self.org_id]

        if data_source is None:
            data_source = infer_source(batch_source)
            print(
                f'`data_source` not specified. Inferred `data_source` as '
                f'BatchPublishType.{BatchPublishType(data_source.value).name}'
            )
        if data_source not in [
            BatchPublishType.DATAFRAME,
            BatchPublishType.LOCAL_DISK,
            BatchPublishType.AWS_S3,
            BatchPublishType.GCP_STORAGE,
        ]:
            raise ValueError('Please specify a valid BatchPublishType')

        payload = dict()
        payload['data_source'] = data_source.value
        payload['publish_schema'] = publish_schema
        payload['group_by'] = group_by

        # Dataframe
        if data_source == BatchPublishType.DATAFRAME:
            # Converting dataframe to local disk format for transmission
            payload['data_source'] = BatchPublishType.LOCAL_DISK.value
            df = batch_source.copy()
            if df.index.name is not None:
                df.reset_index(inplace=True)
            clean_df_types(df)

            with tempfile.TemporaryDirectory() as tmp:
                # To maintain the same data types during transportation from client
                #  to server, we must explicitly send and recreate the data types through
                #  a file. Otherwise, Pandas.from_csv() will convert quoted strings to integers.
                #  See: https://github.com/pandas-dev/pandas/issues/35713
                log_path = Path(tmp) / 'log.csv'
                dtypes_path = Path(tmp) / 'dtypes.csv'
                df.dtypes.to_frame('types').to_csv(dtypes_path)
                csv_paths = [dtypes_path, log_path]

                # Overwrite CSV with current batch
                df.to_csv(log_path, index=False)

                result = self._call(
                    path, json_payload=payload, files=csv_paths, stream=True
                )

                final_return = None
                for res in result:
                    print_streamed_result(res)
                    final_return = res

                return final_return

        # Local disk
        if data_source == BatchPublishType.LOCAL_DISK:
            local_file_path = batch_source
            result = self._call(
                path,
                json_payload=payload,
                files=[Path(local_file_path)],
                stream=True,
            )

            final_return = None
            for res in result:
                print_streamed_result(res)
                final_return = res

            return final_return

        # S3
        if data_source == BatchPublishType.AWS_S3:
            s3_sri_path = batch_source
            # Validate S3 creds
            validate_s3_uri_access(s3_sri_path, credentials, throw_error=True)
            with tempfile.NamedTemporaryFile() as tmp:
                # tmp is a dummy file passed to BE for ease of API consolidation
                payload['file_path'] = s3_sri_path
                payload['credentials'] = credentials
                result = self._call(
                    path, json_payload=payload, files=[Path(tmp.name)], stream=True
                )

                final_return = None
                for res in result:
                    print_streamed_result(res)
                    final_return = res

                return final_return

        # GCP
        if data_source == BatchPublishType.GCP_STORAGE:
            gcp_sri_path = batch_source
            # Validate GCS creds
            if credentials is not None:
                gcs_credentials = {}
                if 'gcs_access_key_id' in credentials:
                    gcs_credentials['aws_access_key_id'] = credentials[
                        'gcs_access_key_id'
                    ]
                if 'gcs_secret_access_key' in credentials:
                    gcs_credentials['aws_secret_access_key'] = credentials[
                        'gcs_secret_access_key'
                    ]
                if 'gcs_session_token' in credentials:
                    gcs_credentials['aws_session_token'] = credentials[
                        'gcs_session_token'
                    ]
            else:
                gcs_credentials = None
            validate_gcp_uri_access(gcp_sri_path, gcs_credentials, throw_error=True)
            with tempfile.NamedTemporaryFile() as tmp:
                # tmp is a dummy file passed to BE for ease of API consolidation
                payload['file_path'] = gcp_sri_path
                payload['credentials'] = gcs_credentials
                result = self._call(
                    path, json_payload=payload, files=[Path(tmp.name)], stream=True
                )

                final_return = None
                for res in result:
                    print_streamed_result(res)
                    final_return = res

                return final_return

    def publish_parquet_s3(
        self,
        project_id: str,
        model_id: str,
        parquet_file: str,
        auth_context: Optional[Dict[str, Any]] = None,
        ts_column: Optional[str] = None,
        default_ts: Optional[int] = None,
    ):
        """
        [SOON TO BE DEPRECATED] Publishes parquet events file from S3 to Fiddler instance. Experimental and may be expanded in the future.

        :param project_id:    The project to which the model whose events are being published belongs
        :param model_id:      The model whose events are being published
        :param parquet_file:  s3_uri for parquet file to be published
        :param auth_context:  Dictionary containing authorization for AWS. List of expected keys are
                              ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']
                              with 'aws_session_token' being applicable to the AWS account being used.
        :param ts_column:     Column to extract time stamp value from.
                              Timestamp must be UTC in format: `%Y-%m-%d %H:%M:%S.%f` (e.g. 2020-01-01 00:00:00.000000)
                              or as the timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param default_ts:    Default timestamp to use if ts_column not specified.
                              Must be given as the timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        """
        # Type enforcement
        print(
            'WARNING: This method will be deprecated in a future version. Please use the method `publish_events_batch` instead.'
        )
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)

        payload = dict()
        payload['file_path'] = parquet_file
        payload['auth_context'] = auth_context

        # Validate S3 creds
        validate_s3_uri_access(parquet_file, auth_context, throw_error=True)

        if ts_column is not None:
            payload['ts_column'] = ts_column
        else:
            if default_ts is None:
                default_ts = int(round(time.time() * 1000))
            payload['default_ts'] = default_ts

        publish_path = ['publish_parquet_file', self.org_id, project_id, model_id]
        publish_result = self._call(publish_path, json_payload=payload, stream=True)
        for res in publish_result:
            print(res)

    def _deploy_container_model(
        self,
        project_id: str,
        model_id: str,
        dataset_id: str,
        model_info: ModelInfo,
        deployment: DeploymentOptions,
    ):
        if deployment.deployment_type == 'far':
            dtype = 'executor'
        else:
            dtype = 'predictor'
            if model_info.mlflow_params is None:
                default_mlflow_url = (
                    f'http://{self.org_id}-{project_id}-{model_id}:8080/invocations'
                )
                model_info.mlflow_params = MLFlowParams(
                    relative_path_to_saved_model='.', live_endpoint=default_mlflow_url
                )

        package_py = (
            'def get_model():\n  '
            'raise ValueError("This should not called. '
            'Use mlflow model container instead")'
        )

        with tempfile.TemporaryDirectory() as tmp:
            artifact_path = Path(tmp)
            package_file = artifact_path / 'package.py'
            package_file.write_text(package_py)

            return self._upload_model_custom(
                artifact_path,
                model_info,
                project_id,
                model_id,
                [dataset_id],
                deployment_type=dtype,
                image_uri=deployment.image_uri,
                namespace=deployment.namespace,
                port=deployment.port,
                replicas=deployment.replicas,
                cpus=deployment.cpus,
                memory=deployment.memory,
                gpus=deployment.gpus,
                await_deployment=deployment.await_deployment,
            )

    def register_model(
        self,
        project_id: str,
        model_id: str,
        dataset_id: str,
        model_info: ModelInfo,
        deployment: DeploymentOptions = None,
        cache_global_impact_importance=True,
        cache_global_pdps=False,
        cache_dataset=True,
    ):
        """
        Register a model in fiddler. This will generate a surrogate model,
        which can be replaced later with original model.

        Note: This method can take a while if the dataset is large. It is
        recommended to call register_model on a smaller representative
        dataset, before trying out on larger dataset.

        :param project_id: id of the project
        :param model_id: name to be used for the dataset and model
        :param dataset_id: id of the dataset to be used
        :param model_info: model info
        :param deployment: option deployment options
        :param cache_global_impact_importance: Boolean indicating whether to pre-calculate and global feature impact
        and global feature importance.
        :param cache_global_pdps: Boolean indicating whether to pre-calculate and cache global partial dependence plots.
        :param cache_dataset: Boolean indicating whether to cache dataset histograms.
        Should be set to True for large datasets.
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        self._safe_name_check(model_id, MAX_ID_LEN)

        print('Loading dataset info ...')
        dataset_info = self.get_dataset_info(project_id, dataset_id)

        print('Validating model info ...')
        ModelInfoValidator(model_info, dataset_info).validate()
        if self.strict_mode:
            model_info.validate()

        if deployment is None:
            deployment = DeploymentOptions(deployment_type='surrogate')

        for i in range(4):
            try:
                if deployment.deployment_type == 'surrogate':
                    print('Generating a model using the baseline dataset ...')
                    self._create_model(
                        project_id,
                        dataset_id,
                        target=model_info.targets[0].name,
                        features=[],
                        train_splits=None,
                        model_id=model_id,
                        model_info=model_info,
                    )
                elif (
                    deployment.deployment_type == 'predictor'
                    or deployment.deployment_type == 'far'
                ):
                    self._deploy_container_model(
                        project_id, model_id, dataset_id, model_info, deployment
                    )
                else:
                    raise ValueError(
                        f'deployment_type not supported'
                        f' {deployment.deployment_type}'
                    )
                break
            except Exception as e:
                if i == 3:
                    raise e
                else:
                    print('retrying ...')

        print('Running tests ...')
        for i in range(5):
            try:
                sample_df = self._get_dataset_sample(project_id, dataset_id, 10)
                self.run_model(project_id, model_id, sample_df, log_events=False)
                print('All tests passed ..')
                break
            except Exception as e:
                if i == 4:
                    print(f'Test failed, please retry register_model. error: {e}')
                    raise e
                else:
                    print(f'Retrying test {i}')

        output_names = [o.name for o in model_info.outputs]
        dataset_cols = [c.name for c in dataset_info.columns]
        outputs_available = all(elem in dataset_cols for elem in output_names)

        if outputs_available:
            print('Model output provided in the baseline dataset')
            fiddler_id_fk = '__dataset_fiddler_id'
            outputs_df = self.get_slice(
                sql_query=f'select {",".join(output_names)} from {dataset_id}',
                project_id=project_id,
            )
            outputs_df[fiddler_id_fk] = outputs_df['__fiddler_id']
            output_names.insert(0, fiddler_id_fk)
            # slice query is returning columns with sanitized name. It must
            # return original names instead. todo
            output_names = [sanitized_name(n) for n in output_names]
            outputs_df = outputs_df[output_names]

            output_columns = [Column(fiddler_id_fk, DataType.INTEGER)]
            output_columns.extend(model_info.outputs)

            with tempfile.TemporaryDirectory() as tmp:
                tmp_dir = Path(tmp)
                path = tmp_dir / 'data.csv'
                outputs_df.to_csv(path, index=False, header=None)
                self._import_model_predictions(
                    project_id,
                    dataset_id,
                    model_id,
                    [oc.to_dict() for oc in output_columns],
                    [path],
                )
            calculate_predictions = False
        else:
            print(
                'Model output was not found in the baseline dataset. '
                'Calculating predictions using the surrogate model instead. '
                'Based on the size of the dataset this might take a while.'
            )
            calculate_predictions = True
        try:
            self.trigger_pre_computation(
                project_id,
                model_id,
                dataset_id,
                calculate_predictions=calculate_predictions,
                cache_global_pdps=cache_global_pdps,
                cache_global_impact_importance=cache_global_impact_importance,
                cache_dataset=cache_dataset,
            )
        except Exception as e:
            print(
                'Failed to pre-compute stats, you can '
                'retry this by calling trigger_pre_computation'
            )
            raise e

        project_url = self.url.replace('host.docker.internal', 'localhost', 1)
        return (
            f'Model successfully registered on Fiddler. \n '
            f'Visit {project_url}/projects/{project_id} '
        )

    def generate_sample_events(
        self,
        project_id: str,
        model_id: str,
        dataset_id: str,
        number_of_events: Optional[int] = 100,
        time_range: Optional[int] = 8,
    ):
        """
        Generate monitoring traffic for the given model. Traffic is generated
        by randomly sampling rows from the specified dataset.

        Note: This method can be used to generate monitoring traffic for
        testing purpose. In production, use publish_event or publish_events_logs
        to send model input and output to fiddler.

        :param project_id:
        :param model_id:
        :param dataset_id:
        :param number_of_events: number of prediction events to generate
        :param time_range: number of days. time_range is used
                to spread the traffic
        :return: sample events that can be published to fiddler
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        dataset_id = _type_enforce('dataset_id', dataset_id, str)

        if number_of_events < 1 or number_of_events > 1000:
            raise ValueError('number_of_events must be between 1 and 1000')

        if time_range < 1 or time_range > 365:
            raise ValueError('time_range must be between 1 and 365 days')

        event_sample_df = self._get_dataset_sample(
            project_id, dataset_id, number_of_events
        )

        # get prediction result
        result = self.run_model(project_id, model_id, event_sample_df, log_events=False)

        result_df = pd.concat([event_sample_df, result], axis=1)

        # create well distributed time stamps
        ONE_DAY_MS = 8.64e7
        event_time = round(time.time() * 1000) - (ONE_DAY_MS * time_range)
        interval = round((time.time() * 1000 - event_time) / number_of_events)
        time_stamp = []
        for i in range(0, len(result_df)):
            time_stamp.append(event_time)
            event_time = event_time + random.randint(1, interval * 2)
        result_df['__occurred_at'] = time_stamp

        return result_df

    def _get_dataset_sample(self, project_id, dataset_id, sample_size):
        dataset_dict = self.get_dataset(
            project_id, dataset_id, max_rows=sample_size, sampling=True
        )
        datasets = dataset_dict.values()
        for df in datasets:
            df.reset_index(inplace=True, drop=True)
        df = pd.concat(datasets, ignore_index=True)
        if len(df) > sample_size:
            df = df[:sample_size]
        # note: len(df) can be less than sample_size
        return df

    def get_model(self, project_id: str, model_id: str, output_dir: Path):
        """
        download the model binary, package.py and model.yaml to the given
        output dir.

        :param project_id: project id
        :param model_id: model id
        :param output_dir: output directory
        :return: model artifacts
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        output_dir = _type_enforce('output_dir', output_dir, Path)

        if output_dir.exists():
            raise ValueError(f'output dir already exists {output_dir}')

        headers = dict()
        headers.update(self.auth_header)

        _, tfile = tempfile.mkstemp('.tar.gz')
        url = f'{self.url}/get_model/{self.org_id}/{project_id}/{model_id}'

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(tfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)

        tar = tarfile.open(tfile)
        output_dir.mkdir(parents=True)
        tar.extractall(path=output_dir)
        tar.close()
        os.remove(tfile)
        return True

    def update_model(
        self,
        project_id: str,
        model_id: str,
        model_dir: Path,
        force_pre_compute: bool = True,
    ):
        """
        update the specified model, with model binary and package.py from
        the specified model_dir

        Note: changes to model.yaml is not supported right now.

        :param project_id: project id
        :param model_id: model id
        :param model_dir: model directory
        :param force_pre_compute: if true refresh the pre-computated values.
               This can also be done manually by calling trigger_pre_computation
        :return: model artifacts
        """
        # Type enforcement
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        model_dir = _type_enforce('model_dir', model_dir, Path)

        if not model_dir.is_dir():
            raise ValueError(f'not a valid model directory: {model_dir}')
        yaml_file = model_dir / 'model.yaml'
        if not yaml_file.is_file():
            raise ValueError(f'Model yaml not found {yaml_file}')
        with yaml_file.open() as f:
            model_info = ModelInfo.from_dict(yaml.safe_load(f))

        if len(model_info.datasets) < 1:
            raise ValueError('Unable to find dataset in model.yaml')

        if len(model_info.datasets) > 1:
            raise ValueError('More than one dataset specified in model.yaml')
        dataset_id = model_info.datasets[0]

        remote_model_info = self.get_model_info(project_id, model_id)
        ddiff = DeepDiff(remote_model_info, model_info, ignore_order=True)

        if len(ddiff) > 0:
            raise ValueError(
                f'remote model info, does not match '
                f'local model info: {ddiff}. Updating model info '
                f'not currently supported'
            )

        print('Loading dataset info')
        dataset_info = self.get_dataset_info(project_id, dataset_id)

        if self.strict_mode:
            print('Validating ...')
            # todo: enable this validator. It need sklearn etc framework libs
            # in client path. So, not sure if we should do this by default
            # validator = PackageValidator(model_info, dataset_info, model_dir)
            # passed, errors = validator.run_chain()
            # if not passed:
            #     raise ValueError(f'validation failed with errors: {errors}')

            ModelInfoValidator(model_info, dataset_info).validate()
            model_info.validate()
        else:
            print('Validation skipped')

        print('Creating model tar file')
        with tempfile.TemporaryDirectory() as tmp:
            shutil.make_archive(
                base_name=str(Path(tmp) / 'model_package'),
                format='tar',
                root_dir=str(model_dir),
                base_dir='.',
            )
            payload = {}
            endpoint_path = ['update_model', self.org_id, project_id, model_id]
            self._call(
                endpoint_path,
                json_payload=payload,
                files=[Path(tmp) / 'model_package.tar'],
            )
            print('Model updated')

        print('Testing updated model')
        should_log = self.capture_server_log
        status = True
        for i in range(3):
            try:
                self.capture_server_log = True
                sample_df = self._get_dataset_sample(project_id, dataset_id, 10)
                self.run_model(project_id, model_id, sample_df, log_events=False)
                print('Server Logs: ')
                print(self.last_server_log)
                print()
                print('All tests passed ..')
                break
            except Exception as e:
                status = False
                if i == 2:
                    print(f'Test failed with error: {e}')
                else:
                    print(f'Retrying test {i}')
            finally:
                self.capture_server_log = should_log

        if status and force_pre_compute:
            try:
                self.trigger_pre_computation(
                    project_id,
                    model_id,
                    dataset_id,
                    overwrite_cache=True,
                    calculate_predictions=True,
                    cache_global_pdps=True,
                    cache_global_impact_importance=True,
                )
            except Exception as e:
                print(
                    'Model was updated successfully, but failed to refresh '
                    'pre-computed values. You can retry this operation by '
                    f'calling trigger_pre_computation(), error: {e}'
                )
                status = False
        return status

    def list_segments(
        self,
        project_id: str,
        model_id: str,
        activated: Optional[bool] = None,
        schema_version: Optional[float] = None,
    ):
        """
        List all segments currently associated with a model. Can filter by activated / schema_version if desired.

        activated = [None/True/False], for all, activated-only, deactivate-only, respectively
        schema_verios = [None/0.1] for all, 0.1 respectively
        """
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        res = None
        path = ['list_segments', self.org_id, project_id, model_id]
        payload = {}
        payload['activated'] = activated
        payload['schema_version'] = schema_version
        res = self._call(path, json_payload=payload)
        if res is None:
            print('Could not get segments for this model.')
        return res

    def upload_segment(
        self,
        project_id: str,
        model_id: str,
        segment_id: str,
        segment_info: SegmentInfo,
    ):
        """Validates and uploads an existing SegmentInfo object to Fiddler."""
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        segment_id = _type_enforce('segment_id', segment_id, str)
        self._safe_name_check(segment_id, MAX_ID_LEN)

        model_info = None
        try:
            model_info = self.get_model_info(project_id, model_id)
        except Exception as e:
            print(
                f'Did not find ModelInfo for project "{project_id}" and model "{model_id}".'
            )
            raise e

        try:
            assert _validate_segment(segment_id, segment_info, model_info)
        except MalformedSchemaException as mse:
            print(
                f'Could not validate SegmentInfo, does the object conform to schema version {CURRENT_SCHEMA_VERSION}?'
            )
            raise mse
        seg_info = segment_info.to_dict()

        res = None
        path = ['define_segment', self.org_id, project_id, model_id, segment_id]
        res = self._call(path, json_payload=seg_info)
        if res is None:
            print('Could not create segment.')
        return res

    def activate_segment(self, project_id: str, model_id: str, segment_id: str):
        """Activate an existing segment in Fiddler"""
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        segment_id = _type_enforce('segment_id', segment_id, str)
        res = None
        path = ['activate_segment', self.org_id, project_id, model_id, segment_id]
        res = self._call(path)
        if res is None:
            print('Could not activate segment.')
        return res

    def deactivate_segment(self, project_id: str, model_id: str, segment_id: str):
        """Deactivate an existing segment in Fiddler"""
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        segment_id = _type_enforce('segment_id', segment_id, str)
        res = None
        path = ['deactivate_segment', self.org_id, project_id, model_id, segment_id]
        res = self._call(path)
        if res is None:
            print('Could not deactivate segment.')
        return res

    def delete_segment(self, project_id: str, model_id: str, segment_id: str):
        """Deletes a deactivated segments from Fiddler"""
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        segment_id = _type_enforce('segment_id', segment_id, str)
        res = None
        path = ['delete_segment', self.org_id, project_id, model_id, segment_id]
        res = self._call(path)
        if res is None:
            print('Could not delete segment.')
        return res

    def get_segment_info(self, project_id: str, model_id: str, segment_id: str):
        """Get the SegmentInfo specified from Fiddler"""
        project_id = _type_enforce('project_id', project_id, str)
        model_id = _type_enforce('model_id', model_id, str)
        segment_id = _type_enforce('segment_id', segment_id, str)
        res = None
        path = ['get_segment', self.org_id, project_id, model_id, segment_id]
        res = self._call(path)
        if res is None:
            print('Could not get segment_info.')
        if res['success']:
            return SegmentInfo.from_dict(res['segment_info'])
        else:
            return None


def _validate_segment(segment_id, segment_info, model_info):
    """helper to validate a segment"""
    if segment_info.segment_id != segment_id:
        raise MalformedSchemaException(
            f'Specified segment_id={segment_id} != segment_info.segment_id={segment_info.segment_id}.'
        )
    return segment_info.validate(model_info)

    # def get_segment_filter_labels(self, project_id, model_id, features=None):
    #     """Potentially for use in seg-monitoring v2: custom segments"""
    #     model_info = self.get_model_info(project_id, model_id)
    #     all_cols = []
    #     if model_info.inputs is not None:
    #         all_cols += model_info.inputs
    #     if model_info.outputs is not None:
    #         all_cols += model_info.outputs
    #     if model_info.targets is not None:
    #         all_cols += model_info.targets
    #     if model_info.decisions is not None:
    #         all_cols += model_info.decisions
    #     if model_info.metadata is not None:
    #         all_cols += model_info.metadata
    #     all_symbols = [col.name for col in all_cols]
    #     if features is None:
    #         features = all_symbols
    #     invalid_cols = [col for col in features if col not in all_symbols]
    #     if len(invalid_cols) > 0:
    #         raise ValueError(f'Cannot produce segment filter labels for features {invalid_cols}, as they could not be found in the model schema.')
    #     result_features = [col for col in features]
    #     return symbols(result_features), result_features


class ExperimentalFeatures:
    def __init__(self, client):
        self.client = client
        self.embeddings = None

    def initialize_embeddings(self, path):
        """
        Initializes NLP embeddings.
        :param path: A file path containing an embeddings file.
        """
        embedding_index = {}

        with open(path, encoding='utf8') as f:
            print('Reading embedding file ...')
            for line in f:
                values = line.split()
                word = values[0]
                vectors = np.asarray(values[1:], dtype='float32')
                embedding_index[word] = vectors

        self.embeddings = embedding_index
        print('Embeddings initialized.')

    def embed_texts(self, texts):
        """Helper to embed texts"""
        if self.embeddings is None:
            raise Exception(
                'No embeddings initialized.  Please run ' 'initialize_embeddings first.'
            )

        emb_length = len(self.embeddings[next(iter(self.embeddings))])
        tokenized_texts = self.make_word_list(texts)
        output_embeddings = []

        for text in tokenized_texts:
            word_embeddings = [
                self.embeddings[word] for word in text if word in self.embeddings
            ]
            if len(word_embeddings) == 0:
                output_embeddings.append(np.zeros([emb_length]))
            else:
                v = np.sum(np.asarray(word_embeddings).reshape(-1, emb_length), axis=0)
                output_embeddings.append(v / np.sqrt(v @ v))

        return np.asarray(output_embeddings)

    def upload_dataset_with_nlp_embeddings(
        self, project_id, dataset_id, dataset, info, text_field_to_index
    ):
        """
        Uploads a dataset with NLP embeddings.
        :param project_id: The project to which the dataset will be uploaded.
        :param dataset_id: A unique ID for the dataset.
        :param dataset: A dictionary mapping names of data files to pandas DataFrames.
        :param info: The fdl.DatasetInfo object for the dataset.
        :param text_field_to_index: The text field to be indexed.
        """
        info = copy.copy(info)
        indexed_dfs = {}
        first = True
        for k, input_df in dataset.items():
            df = input_df.reset_index(drop=True)
            embeddings = self.embed_texts(df[text_field_to_index].tolist())
            emb_df = pd.DataFrame(
                embeddings,
                columns=[
                    f'_emb_{text_field_to_index}_{i}'
                    for i in range(embeddings.shape[1])
                ],
            )

            final_df = pd.concat([df, emb_df], axis=1)
            indexed_dfs[k] = final_df
            if first:
                emb_dataset_info = DatasetInfo.from_dataframe(emb_df)
                info.columns = info.columns + emb_dataset_info.columns
            first = False

        res = self.client.upload_dataset(
            project_id=project_id, dataset_id=dataset_id, dataset=indexed_dfs, info=info
        )

        return res

    def nlp_similarity_search(
        self,
        project_id,
        dataset_id,
        model_id,
        nlp_field='',
        string_to_match='',
        num_results=5,
        where_clause='',
        drop_emb_cols=True,
    ):
        """
        Performs text-wise similarity search for NLP data.
        :param project_id: The project containing the dataset and model.
        :param dataset_id: The dataset associated with the model.
        :param model_id: The model associated with the dataset.
        :param nlp_field: The field containing NLP data.
        :param string_to_match: The string being searched against.
        :param num_results: The number of results to return.
        :param where_clause: Optional WHERE clause for filtering.
        """

        def generate_dist_query(string):
            # computes the SQL dot-product of a particular point's embeddings
            # and embedding column names.
            emb_point = self.embed_texts([string])[0]
            fields = [f'_emb_{nlp_field}_{i}' for i in range(len(emb_point))]
            prods = [f'{val}*{field}' for val, field in zip(emb_point, fields)]
            return '+'.join(prods)

        dist = generate_dist_query(string_to_match)

        q = f'SELECT *, {dist} as cossim FROM "{dataset_id}.{model_id}" {where_clause} ORDER BY cossim DESC LIMIT {num_results}'

        path = ['executor', self.client.org_id, project_id, 'slice_query']
        out = self.client._call(path, json_payload={'sql': q, 'project': project_id})
        info = out[0]
        data = out[1:]

        if drop_emb_cols:
            emb_cols = [x for x in info['columns'] if '_emb' in x]
            return pd.DataFrame(data, columns=info['columns']).drop(emb_cols, axis=1)
        else:
            return pd.DataFrame(data, columns=info['columns'])

    DIST_NUMERIC = 0  # Distance can be computed numerically
    DIST_BINARY = 1  # Distance is binary

    DIST_METRIC_BY_DATA_TYPE = {
        'int': DIST_NUMERIC,
        'category': DIST_BINARY,
        'float': DIST_NUMERIC,
        'bool': DIST_BINARY,
        'str': DIST_BINARY,
    }

    def tabular_similarity_search(
        self,
        project_id,
        dataset_id,
        model_id,
        feature_point_to_match,
        features_in_dist=[],
        exclude_features_in_dist=[],
        most_similar=True,
        num_results=5,
        where_clause='',
    ):
        """
        Performs row-wise similarity search for tabular data.
        :param project_id: The project containing the dataset and model.
        :param dataset_id: The dataset associated with the model.
        :param model_id: The model associated with the dataset.
        :param feature_point_to_match: The event being searched against.
        :param num_results: The number of results to return.
        :param where_clause: Optional WHERE clause for filtering.
        """

        # If the input is a DataFrame, convert it to a series
        if isinstance(feature_point_to_match, pd.DataFrame):
            feature_point = feature_point_to_match.iloc[0]
        else:
            feature_point = feature_point_to_match

        query_target = f'{dataset_id}.{model_id}'

        ################
        # Let's get all the info about the fields in the slice so we can
        # build a distance query.  Metrics for each field will vary by data
        # type.

        q = f'SELECT * FROM "{query_target}" {where_clause}  LIMIT 0'

        path = ['executor', self.client.org_id, project_id, 'slice_query']
        out = self.client._call(path, json_payload={'sql': q, 'project': project_id})
        info = out[0]

        feature_dtype_hash = {
            x['column-name']: x['data-type'] for x in info['model_schema']['inputs']
        }

        if not features_in_dist:
            features_in_dist = feature_dtype_hash.keys()

        # Make sure the user provided enough fields for the specified
        # model's inputs.
        missing_features = set(feature_dtype_hash.keys()) - set(feature_point.index)

        if missing_features:
            raise Exception(
                f'feature_point_to_match is missing: '
                f'{missing_features} which is a '
                f'necesary input for the model specified ('
                f'{project_id}:{model_id}).'
            )

        # Make sure any exclude_features actually reside in the dataset
        unknown_excludes = set(exclude_features_in_dist) - set(
            feature_dtype_hash.keys()
        )

        if unknown_excludes:
            raise Exception(
                f'Exclude features include: '
                f'{unknown_excludes} which not '
                f'an input for the model ('
                f'{project_id}:{model_id}).'
            )

        ################
        # Get the standard deviation of the numeric fields for scaling. In the
        # future, add options for alternatives e.g. Median Absolute Distance

        scalable_fields = [
            fname
            for fname in features_in_dist
            if self.DIST_METRIC_BY_DATA_TYPE[feature_dtype_hash[fname]]
            == self.DIST_NUMERIC
            and fname not in exclude_features_in_dist
        ]

        if scalable_fields:
            q_items = [
                f'cast(stddev({self._fix_db_name(fname)}) as FLOAT)'
                for fname in scalable_fields
            ]

            q = f'SELECT {", ".join(q_items)} FROM "{query_target}" {where_clause}'

            out = self.client._call(
                path, json_payload={'sql': q, 'project': project_id}
            )

            scale_factors = {x: y for x, y in zip(scalable_fields, out[1])}

        def generate_dist_query():
            query_items = []
            for feature_name in features_in_dist:
                feature_type = feature_dtype_hash[feature_name]
                if feature_name in exclude_features_in_dist:
                    continue
                if self.DIST_METRIC_BY_DATA_TYPE[feature_type] == self.DIST_NUMERIC:
                    query_items.append(
                        f'POWER(({self._fix_db_name(feature_name)}-{feature_point[feature_name]})/{scale_factors[feature_name]},2)'
                    )
                else:
                    query_items.append(
                        f'CASE WHEN {self._fix_db_name(feature_name)}=\'{feature_point[feature_name]}\' THEN 0.0 ELSE 1.0 END'
                    )

            return 'CAST(POWER(' + ' + '.join(query_items) + ', 0.5) AS FLOAT)'

        q = f'SELECT {generate_dist_query()} AS __distance, * FROM "{query_target}" {where_clause} ORDER BY __distance {"" if most_similar else "DESC"} LIMIT {num_results}'

        out = self.client._call(path, json_payload={'sql': q, 'project': project_id})

        ######
        # Make a map to unmangle all the column names before output
        orig_fields = {}

        for x in info['model_schema']['inputs']:
            orig_fields[self._fix_db_name(x['column-name'])] = x['column-name']

        for x in info['model_schema']['targets']:
            orig_fields[self._fix_db_name(x['column-name'])] = x['column-name']

        for x in info['model_schema']['outputs']:
            orig_fields[self._fix_db_name(x['column-name'])] = x['column-name']
        ######

        out_cols = [
            orig_fields[x] if x in orig_fields else x for x in out[0]['columns']
        ]

        out_df = pd.DataFrame(out[1:], columns=out_cols)

        # return out_df, q
        return out_df

    def run_nlp_feature_impact(
        self,
        project_id,
        dataset_id,
        model_id,
        prediction_field_name=None,
        source=None,
        num_texts=None,
    ):
        """
        Performs ablation feature impact on a collection of text samples
        determining which words have the most impact on the
        prediction. Will default to first prediction of a multi-output model
        if no prediction_field_name is specified.

        Returns the name of the prediction field being explained, a list
        of the prediction fields available, and a list of tuples containing
        average-impact, word-token, and occurrence count.
        :param project_id: The project containing the dataset and model.
        :param dataset_id: The dataset associated with the model.
        :param model_id: The model associated with the dataset.
        :param source: The dataset split to compute feature impact over.
        """
        afi = self.FeatureImpactWBatchedRetrieval(
            api=self.client,
            project_id=project_id,
            dataset_id=dataset_id,
            model_id=model_id,
            source=source,
            num_texts=num_texts,
            output_key=prediction_field_name,
        )

        texts = self.make_word_list(afi.texts)

        for text in texts:
            afi.get_prediction(
                None, ' '.join(text)
            )  # Full texts is base-prediction; no words ablated.

            for word in text:
                afi.get_prediction(word, ' '.join([w for w in text if w is not word]))

        # Get predictions from any remaining words in the queue.
        afi.flush_cache()

        afi.mean_word_impact = {
            word: afi.total_word_impact[word] / afi.word_counts[word]
            for word in afi.word_counts.keys()
        }

        afi.sorted_impact = sorted(
            zip(afi.mean_word_impact.values(), afi.mean_word_impact.keys()),
            reverse=True,
        )

        return (
            afi.requested_key,
            afi.prediction_keys,
            [(impact, key, afi.word_counts[key]) for impact, key in afi.sorted_impact],
        )

    # Non-member experimental functions/classes

    def _fix_db_name(self, name):
        """
        Helper to convert non-alphanumeric characters to underscores.
        :param name: str A feature name to make SQL-compatible
        :return: str A SQL-compatible field name.
        """
        # Copied from database.py
        # Allow only a-z, 0-9, and _
        return re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()

    # ["A!dog.", "Let's Dance!"] -> [["a", "dog"], ["let's", "dance"]]

    def make_word_list(self, texts):
        """Helper for other NLP features"""
        out = []
        # This is essentially how the Keras tokenizer preprocesses.
        for text in texts:
            # replace punctuation with space unless single-quote
            x = re.sub('[!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n]', ' ', text)
            # condense multiple space characters, strip leading + trailing
            # finally split into a word list.  Append to a list with an
            # entry per text.
            x = re.sub(' +', ' ', x).strip().lower().split(' ')
            out.append(x)

        return out

    class FeatureImpactWBatchedRetrieval:
        """Helper class to support NLP feature impact"""

        DEFAULT_BATCH_SIZE = 1000
        DEFAULT_NUM_TEXTS = 250

        def __init__(
            self,
            api,
            project_id,
            dataset_id,
            model_id,
            source=None,
            num_texts=DEFAULT_NUM_TEXTS,
            batch_size=DEFAULT_BATCH_SIZE,
            output_key=None,
        ):
            self.api = api
            self.dataset = api.get_dataset(
                project_id=project_id,
                dataset_id=dataset_id,
                max_rows=1000000 if num_texts is None else num_texts,
            )

            self.batch_size = batch_size
            self.text_field_name = (
                api.get_model_info(project_id, model_id).inputs[0].name
            )

            self.texts = []
            if source is None:
                source = next(iter(self.dataset))

            self.texts = self.dataset[source][self.text_field_name].values

            self.project_id = project_id
            self.model_id = model_id

            self.requested_key = output_key
            self.prediction_keys = None

            self.word_counts = {}
            self.total_word_impact = {}
            self.last_base_prediction = None
            self.clear_cache()

        def clear_cache(self):
            self.predict_cache_size = 0
            self.cache_word = []
            self.cache_text = []

        def run_predictions(self, texts):
            if len(texts) > 0:

                prediction = self.api.run_model(
                    project_id=self.project_id,
                    model_id=self.model_id,
                    df=pd.DataFrame({self.text_field_name: texts}),
                )

                self.prediction_keys = prediction.columns

                if self.requested_key is None:
                    self.requested_key = self.prediction_keys[0]

                return prediction[self.requested_key]
            else:
                return []

        def flush_cache(self):
            preds = self.run_predictions(self.cache_text)
            for word, pred in zip(self.cache_word, preds):
                if word is None:
                    self.last_base_prediction = pred
                else:
                    if word not in self.word_counts:
                        self.word_counts[word] = 0
                        self.total_word_impact[word] = 0

                    self.word_counts[word] += 1
                    self.total_word_impact[word] += self.last_base_prediction - pred

            self.clear_cache()

        def get_prediction(self, word, text):
            self.predict_cache_size += 1

            if self.predict_cache_size > self.batch_size:
                self.flush_cache()
            else:
                self.cache_word.append(word)
                self.cache_text.append(text)
