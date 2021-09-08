from typing import (
    NamedTuple,
    Optional,
    Dict,
    Callable,
)
from enum import Enum
import io
import logging

import aiohttp
from aiohttp_retry import (
    RetryClient,
    RetryOptions,
)
import ssl
import certifi

from .api_config import (
    ApiEndpoint,
)
from .stream_helpers import (
    OnePassInfo,
    stream_from_argument,
    ImageArg,
)
from . import constants

# How many times to retry a request.
RETRY_COUNT = 5


def status_code_bears_json(status_code: int) -> bool:

    return status_code != 503


class StatusAndBody(NamedTuple):
    status: int
    body: dict


class RequestIssuesEnum(Enum):
    BAD_JSON = "BadJSON"
    FIVE_HUNDRED = "FiveHundred"
    ABORTED = "RequestResponseAborted"
    GENERIC_ERROR = "GenericError"
    TIMEOUT = "RequestResponseTimedOut"
    TOO_MANY_ATTEMPTS = "TooManyAttempts"
    CONNECTION_ERROR = "ConnectionError"


class RequestIssueException(Exception):
    pass


class UseTag(Enum):
    INITIAL_LOOKUP = "InitialLookup"
    POST_BYTES = "PostBytes"
    CHECK_PROCESSING_STATUS = "CheckProcessingStatus"
    DOWNLOAD_FROM_PRESIGNED_URL = 'DownloadFromPresignedURL'


class EnvelopeOptions(NamedTuple):
    """
    This are parts of the API that are seldom
    needed, but which we have fields for.
    """
    relative_path: Optional[str] = None
    job_name: Optional[str] = None
    expected_optimized_image_filename: Optional[str] = None
    max_overhead: Optional[float] = None
    force_reprocessing: Optional[bool] = None
    task_thread: Optional[str] = None


class ApiRequest(NamedTuple):
    one_pass_info: OnePassInfo
    precursor_name: constants.PrecursorEnum
    adjustments: Dict
    envelope_options: Optional[EnvelopeOptions] = None


class ToilmoreHTTPRequester(object):
    """
    Manages the low-level details of requests to the API, without retries.
    """
    _api_endpoint: ApiEndpoint
    _domain: str
    _api_token: str
    _use_port: int
    _use_host: str
    _debug_mode: bool

    def __init__(
        self,
        api_endpoint: ApiEndpoint,
        api_token: str,
        domain: str,
        debug_mode: bool
    ) -> None:
        self._api_endpoint = api_endpoint
        self._api_token = api_token
        self._domain = domain
        self._debug_mode = debug_mode

        port = api_endpoint.port
        self._use_port = port if port else 80

        self._http_client_session = aiohttp.ClientSession()

        self._use_host = self._get_api_host()
        self._logger = logging.getLogger('toilmoresdk')
        self._sslcontext = ssl.create_default_context(
            cafile=certifi.where()
        )

    def _debug_message(self, use_tag: UseTag, msg: str) -> None:

        if self._debug_mode:
            self._logger.debug("[{%s}]: {%s}", use_tag, msg)

    async def empty_submit(
        self,
        api_request: ApiRequest,
        use_tag: UseTag,
        attempt_no: int,
        attempts: int = RETRY_COUNT
    ) -> StatusAndBody:
        """
        Call to the `optimized` endpoint without any file body, used for
        asserting status of a file.

        :param api_request:
        :param use_tag:
        :param attempt_no:
        :param attempts:
        :return:
        """
        file_hash = api_request.one_pass_info.file_hash
        request_json_body = self._get_request_json_body(
            api_request,
            file_hash,
            attempt_no
        )
        request_json_body['force_reprocessing'] = False
        retry_options = RetryOptions(
            attempts=attempts,
            start_timeout=20,
            max_timeout=1200,
            statuses=[500, ]
        )
        retry_client = RetryClient(
            raise_for_status=False,
            retry_options=retry_options,
            logger=self._logger if self._debug_mode else None
        )
        retry_client._client = self._http_client_session
        async with retry_client.post(
            self._make_url(file_hash),
            json=request_json_body,
            headers={
                'Authorization': self._make_auth_token()
            },
            ssl=self._sslcontext
        ) as response:
            status_code = response.status
            if int(status_code / 100) == 5:
                response_content = await response.content.read()
                self._debug_message(
                    use_tag,
                    "HTTP 50x Error: {}".format(response_content)
                )
                raise RequestIssueException(
                    RequestIssuesEnum.FIVE_HUNDRED
                )
            try:
                response_json = await response.json()
                return StatusAndBody(
                    status=status_code,
                    body=response_json
                )
            except Exception as e:
                self._debug_message(
                    use_tag,
                    "Response Error/BadJSON, {}".format(str(e))
                )
                raise RequestIssueException(RequestIssuesEnum.BAD_JSON)

    async def submit_with_body(
        self,
        file_arg: ImageArg,
        api_request: ApiRequest,
        use_tag: UseTag,
        attempt_no: int,
        attempts: int = RETRY_COUNT
    ) -> StatusAndBody:
        """
        Submits an image for optimization to the light/lux API.

        :param file_arg: A string (indicating a file name), bytes or a
            StreamFactory.
        :param api_request:
        :param use_tag:
        :param attempt_no:
        :param attempts:
        :return:
        """

        file_hash = api_request.one_pass_info.file_hash
        request_json_body = self._get_request_json_body(
            api_request,
            file_hash,
            attempt_no
        )
        retry_options = RetryOptions(
            attempts=attempts,
            start_timeout=20,
            max_timeout=1200,
            statuses=[500, ]
        )
        retry_client = RetryClient(
            raise_for_status=False,
            retry_options=retry_options,
            logger=self._logger if self._debug_mode else None
        )
        retry_client._client = self._http_client_session

        stream_factory = await stream_from_argument(file_arg)
        st = stream_factory()
        img_content = await st.read()
        with aiohttp.MultipartWriter("form-data") as mpwriter:
            # WARNING: The json should be added in first place!
            mpwriter.append_json(
                request_json_body
            )
            # In second place the file content!
            mpwriter.append(
                io.BytesIO(img_content)
            )

            url = self._make_url(file_hash)
            async with retry_client.post(
                url,
                data=mpwriter,
                headers={
                    'Authorization': self._make_auth_token()
                },
                ssl=self._sslcontext
            ) as response:
                status_code = response.status
                if int(status_code / 100) == 5:
                    response_content = await response.content.read()
                    self._debug_message(
                        use_tag,
                        "HTTP 50x Error: {}".format(response_content)
                    )
                    raise RequestIssueException(
                        RequestIssuesEnum.FIVE_HUNDRED
                    )
                try:
                    response_json = await response.json()
                    return StatusAndBody(
                        status=status_code,
                        body=response_json
                    )
                except:
                    self._debug_message(use_tag, "Response Error/BadJSON")
                    raise RequestIssueException(
                        RequestIssuesEnum.BAD_JSON
                    )

    def _get_request_json_body(
        self,
        api_request: ApiRequest,
        file_hash: str,
        attempt_no: int
    ) -> dict:
        use_envelope_options = api_request.envelope_options
        if use_envelope_options:
            force_reprocessing = use_envelope_options.force_reprocessing
            expected_optimized_image_filename = (
                use_envelope_options.expected_optimized_image_filename
            )
            task_thread = use_envelope_options.task_thread
        else:
            force_reprocessing = False
            expected_optimized_image_filename = None
            task_thread = file_hash
        adjustments = api_request.adjustments
        original_image_size_in_bytes = api_request.one_pass_info.file_size

        if not force_reprocessing:
            force_reprocessing = False
        if not adjustments:
            adjustments = {}
        if not expected_optimized_image_filename:
            expected_optimized_image_filename = (
                f"/python-sdk-call/at-hash/optimized/{file_hash}"
            )
        if not task_thread:
            task_thread = file_hash
        # Let's use a codified relative path so that we can test-match in tests
        use_relative_path = (
            f"/python-sdk-call/at-hash/input/{file_hash}/attempt_{attempt_no}"
        )

        request_json_body = {
            "image_file_hash": file_hash,
            "original_image_size_in_bytes": original_image_size_in_bytes,
            "relative_path": use_relative_path,
            "expected_optimized_image_filename":
                expected_optimized_image_filename,
            "precursor_name": api_request.precursor_name.value,
            "domains": [
                self._domain
            ],
            "force_reprocessing": force_reprocessing,
            "shimmercat_job_record": {
                "task_thread": task_thread,
            }
        }
        if self._api_endpoint.api_module == constants.LUX_API_KEY:
            request_json_body['shimmercat_job_record'].update({
                "adjustments": adjustments
            })
        max_overhead = (
            use_envelope_options.max_overhead if use_envelope_options else None
        )
        if max_overhead:
            request_json_body["max_overhead"] = int(max_overhead)

        return request_json_body

    def _make_auth_token(self):
        return "Token {} Domain {}".format(
            self._api_token,
            self._domain
        )

    def _make_url(self, file_hash: str):
        base_url = '{protocol}://{host}:{port}'.format(
            protocol=self._api_endpoint.protocol,
            host=self._use_host,
            port=self._api_endpoint.port
        )
        return '{}{}'.format(
            base_url,
            self._api_endpoint.url_prefix + "optimized/" + file_hash + "/"
        )

    async def request_presigned(self, presigned_url: str) -> Callable:
        try:
            retry_options = RetryOptions(
                attempts=RETRY_COUNT,
                start_timeout=10,
                max_timeout=180,
                statuses=[500, ]
            )
            retry_client = RetryClient(
                raise_for_status=False,
                retry_options=retry_options,
                logger=self._logger if self._debug_mode else None
            )
            retry_client._client = self._http_client_session
            async with retry_client.get(
                presigned_url,
                ssl=self._sslcontext
            ) as response:
                status_code = response.status
                response_content = await response.content.read()
                if int(status_code / 100) == 5:
                    self._debug_message(
                        UseTag.DOWNLOAD_FROM_PRESIGNED_URL,
                        "HTTP 50x Error: {}".format(response_content)
                    )
                    raise RequestIssueException(
                        RequestIssuesEnum.FIVE_HUNDRED
                    )
                return await stream_from_argument(response_content)
        except aiohttp.ClientConnectionError:
            raise RequestIssueException(RequestIssuesEnum.CONNECTION_ERROR)
        except aiohttp.ServerTimeoutError:
            raise RequestIssueException(RequestIssuesEnum.TIMEOUT)
        except Exception as e:
            self._logger.error(
                'request_presigned unexpected error: %s',
                str(e)
            )
            raise RequestIssueException(RequestIssuesEnum.GENERIC_ERROR)

    def _get_api_host(self):
        host_specified = self._api_endpoint.host

        if isinstance(host_specified, str):
            # OK
            return host_specified
        else:
            assert isinstance(host_specified, Callable)
            # Get the host.
            r_host = host_specified()
            if isinstance(r_host, str):
                return r_host
            else:
                raise Exception(
                    '_get_api_host error: Expecting string or Callable.'
                )
