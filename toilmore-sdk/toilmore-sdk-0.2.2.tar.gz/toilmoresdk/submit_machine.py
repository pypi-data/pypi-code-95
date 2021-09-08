from enum import Enum
from typing import (
    NamedTuple,
    Optional,
    Union,
)
import asyncio
import logging
import os
import json

import jsonschema

from .http_requester import (
    RequestIssueException,
    ToilmoreHTTPRequester,
    EnvelopeOptions,
    UseTag,
    ApiRequest,
)
from .api_config import ApiConfig
from .stream_helpers import (
    ImageArg,
    stream_from_argument,
    pass_and_compute_hash,
    StreamFactory,
)
from .environment.logging import setup_logger
from . import constants
from .image_codecs import RecognizedImageType


class RejectionNoticeEnum(Enum):
    # Invalid token
    ACCESS_DENIED = "ACCESS_DENIED"
    # Image is too big
    IMAGE_IS_TOO_BIG = "IMAGE_IS_TOO_BIG"
    # No presigned URL?
    UNCLEAR = "UNCLEAR"
    # We have a bundled error from the http requester
    HTTP_REQUEST_ERROR = "HTTP_REQUEST_ERROR"
    # Timeout
    TIMEOUT = "TIMEOUT"


class RejectionNotice(NamedTuple):
    rejection_notice: RejectionNoticeEnum
    inner_error: Optional[RequestIssueException] = None


class RejectionNoticeToHumanEnum(Enum):
    ACCESS_DENIED = (
        "Access denied failure! Invalid authentication token or domain name, "
        "please make sure you set the right api token and domain for "
        "the request."
    )
    IMAGE_IS_TOO_BIG = (
        "Optimized image too big failure! Not possible to create an optimized "
        "image that has a smaller size and also preserves quality of the "
        "original file. Use the max_overhead parameter if you want to get an "
        "optimized image which is bigger than the original image. "
        "Read more here: "
        "https://demo.pixellena.com/adjustments about this parameter."
    )
    UNCLEAR = (
        "Unclear failure! We could not get the optimized image either because "
        "the download "
        "link was not generated or because we could not download the image "
        "from the bucket."
    )
    HTTP_REQUEST_ERROR = (
        "Http requester error! See the rejection_notice and the inner_error "
        "for more details."
    )
    TIMEOUT = (
        "Timeout failure! We got a timeout error from the toilmore API, please "
        "try again later."
    )


class OptimizationResponseStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


class OptimizationResponse(NamedTuple):
    status: OptimizationResponseStatus
    rejection_notice: Optional[RejectionNotice] = None
    response_stream: Optional[StreamFactory] = None


class Toilmore(object):
    """
     Main API wrapper. It keeps track of image optimization requests and their
     async nature.
     Instance one of these for all requests to a single endpoint.

     Example:

    import os
    import asyncio

    from toilmoresdk import (
        LIGHT_API,
        Toilmore,
    )
    from toilmoresdk.submit_machine import OptimizationResponseStatus
    from toilmoresdk.stream_helpers import store_file_content
    from toilmoresdk.api_config import ApiConfig
    from toilmoresdk.constants import PrecursorEnum

    config = ApiConfig(
        # LIGHT_API contains our light api endpoint.
        api_endpoint=LIGHT_API,
        # Use a valid API token below:
        api_token='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        # Use a valid domain below, as received when
        # you created the token.
        domain='YYYYYYYYYYYYYYYYYYYYYYYYYY'
    )

    toilmore = Toilmore(config)

    loop = asyncio.get_event_loop()

    image_path = "./my_image.jpg"
    precursor = PrecursorEnum.WEBP0
    r = loop.run_until_complete(
        toilmore.optimize(image_path, precursor)
    )

    if r.status == OptimizationResponseStatus.FAILURE:
        rejection_notice = r.rejection_notice
        print(
            'rejection_notice: {}, inner_error: {}'.format(
                rejection_notice.rejection_notice,
                rejection_notice.inner_error
            )
        )
    elif r.status == OptimizationResponseStatus.SUCCESS:
        output_dir = os.path.dirname(image_path)  # You can change that to any other directory.
        base_filename, file_extension = os.path.splitext(image_path)
        loop.run_until_complete(
            store_file_content(
                r.response_stream,
                output_dir,
                base_filename,
                precursor
            )
        )
        print('Optimized image stored at: ', output_dir)

    """
    def __init__(
        self,
        config: Union[ApiConfig, dict],
        logger: logging.Logger = None
    ):
        """

        :param config: An object specifying the auth token, API endpoint and
     *               the domain to register image operations under.
        :param logger:
        """
        if isinstance(config, dict):
            config = ApiConfig(**config)
        self._config = config
        api_token = config.api_token
        self._api_endpoint = config.api_endpoint
        domain = config.domain

        debug_mode = config.debug_mode

        self._http_requester = ToilmoreHTTPRequester(
            self._api_endpoint,
            api_token,
            domain,
            debug_mode
        )
        self.debug_mode = debug_mode

        if logger:
            self._logger = logger
        else:
            setup_logger(logging.DEBUG)
            self._logger = logging.getLogger('toilmoresdk')

    def get_schema_contents(self, indicated_filename: str) -> dict:
        schema_filename = os.path.join(
            os.path.dirname(__file__),
            'json_schemas',
            indicated_filename
        )
        with open(schema_filename, 'r') as fin:
            return json.load(fin)

    def validate_adjustments(self, adjustments=Optional[dict]) -> dict:
        # "light" API does not support adjustments...
        if self._api_endpoint.api_module == constants.LIGHT_API_KEY:
            return {}
        if not adjustments:
            return {}
        try:
            schema = self.get_schema_contents('adjuster-schema.json')
            jsonschema.validate(adjustments, schema=schema)
            return adjustments
        except jsonschema.exceptions.ValidationError as err:
            # Bad
            error_msg = 'Received invalid adjustments in request: {}'.format(
                str(err)
            )
            self.emit_debug_message(error_msg)
            raise RequestIssueException(
                error_msg
            )

    async def optimize(
        self,
        image_arg: ImageArg,
        precursor: constants.PrecursorEnum,
        adjustments: Optional[dict] = None,
        envelope_options: Optional[EnvelopeOptions] = None
    ) -> OptimizationResponse:
        """
        Optimize an image using a given `precursor`.
        For us, `precursor` denotes a
        fixed target image format + encoder variant.
        They are detailed at our API docs page: https://pixellena.com/lux-api/.

        :param image_arg: The contents of the image to optimize.
        :param precursor: The precursor (see above).
        :param adjustments: see Adjustments: https://pixellena.com/lux-api/
                            in our API docs.
        :param envelope_options: Object with other misc options that the API
            accept, optional.
        :return:
        """
        try:
            adjustments = self.validate_adjustments(adjustments)
        except RequestIssueException as e:
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.HTTP_REQUEST_ERROR,
                inner_error=e
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )
        allowed_precursors = constants.PrecursorEnum.list()
        if precursor.value not in allowed_precursors:
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.HTTP_REQUEST_ERROR,
                inner_error=RequestIssueException(
                    f'WrongPrecursor. Allowed values are: {allowed_precursors}'
                )
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

        self.emit_debug_message('Starting to optimize the image...')
        return await self.optimize_with_precursor(
            image_arg,
            precursor,
            adjustments,
            envelope_options
        )

    async def optimize_with_precursor(
        self,
        image_arg: ImageArg,
        precursor: constants.PrecursorEnum,
        adjustments: Optional[dict] = None,
        envelope_options: Optional[EnvelopeOptions] = None
    ) -> OptimizationResponse:
        """
        Optimize an image using a given `precursor`.
        For us, `precursor` denotes a
        fixed target image format + encoder variant.
        They are detailed at our API docs page: https://pixellena.com/lux-api/.

        :param image_arg: The contents of the image to optimize.
        :param precursor: The precursor (see above).
        :param adjustments: see Adjustments: https://pixellena.com/lux-api/
*           in our API docs.
        :param envelope_options: Object with other misc options that the API
            accept, optional.
        :return:
        """
        use_envelope_options = (
            envelope_options if envelope_options else None
        )

        stream_factory = await stream_from_argument(image_arg)
        st = stream_factory()
        one_pass_info = await pass_and_compute_hash(st)
        # This is not an accepted image input...
        if not one_pass_info.image_type:
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.HTTP_REQUEST_ERROR,
                inner_error=RequestIssueException(
                    'The image input is not allowed. We only accept: {}'.format(
                        RecognizedImageType.list()
                    )
                )
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

        api_request = ApiRequest(
            one_pass_info=one_pass_info,
            precursor_name=precursor,
            adjustments=adjustments if adjustments else {},
            envelope_options=use_envelope_options
        )
        try:
            res0 = await self._http_requester.empty_submit(
                api_request,
                UseTag.INITIAL_LOOKUP,
                0
            )
        except RequestIssueException as e:
            self.emit_debug_message(
                'optimize_with_precursor error: {}'.format(str(e))
            )
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.UNCLEAR,
                inner_error=e
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )
        res_status = res0.status
        success_or_deny = res0.body.get('success_or_deny', None)
        if res_status == 200 and success_or_deny == 'success':
            # It means we already have an optimized image.
            optimization_response = await self._handle_ready_response(res0.body)
            self.emit_debug_message('Got success response!')
            return optimization_response

        if success_or_deny == 'deny':
            self.emit_debug_message(
                str(RejectionNoticeEnum.IMAGE_IS_TOO_BIG)
            )
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.IMAGE_IS_TOO_BIG
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

        if success_or_deny == 'processing':
            self.emit_debug_message('Image is processing yet...')
            return await self._wait_for_ready(0, api_request, 0, image_arg)

        # If came here, it's probably because we need a file.
        if res_status == 404 and success_or_deny == 'expecting-file':
            self.emit_debug_message(
                'expecting-file... re-uploading the file...'
            )
            return await self._continue_to_submit(
                stream_factory,
                api_request
            )

        if res_status == 401:
            self.emit_debug_message(
                'Access denied! Please update your api token!'
            )
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.ACCESS_DENIED
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

        self.emit_debug_message('Got an unexpected response from the API.')
        rn = RejectionNotice(
            rejection_notice=RejectionNoticeEnum.UNCLEAR
        )
        return OptimizationResponse(
            status=OptimizationResponseStatus.FAILURE,
            rejection_notice=rn
        )

    async def _handle_ready_response(
        self,
        response_body: dict
    ) -> OptimizationResponse:
        presigned_url = response_body.get('presigned_url', None)
        # Now we just need to make a get ...
        if presigned_url:
            try:
                stream = await self._http_requester.request_presigned(
                    presigned_url
                )
            except RequestIssueException:
                self.emit_debug_message(
                    '_handle_ready_response -> request_presigned error! '
                    'Could not download the optimized image from: {}'.format(
                        presigned_url
                    )
                )
                rn = RejectionNotice(
                    rejection_notice=RejectionNoticeEnum.UNCLEAR
                )
                return OptimizationResponse(
                    status=OptimizationResponseStatus.FAILURE,
                    rejection_notice=rn
                )
            return OptimizationResponse(
                status=OptimizationResponseStatus.SUCCESS,
                response_stream=stream()
            )
        else:
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.UNCLEAR
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

    async def _continue_to_submit(
        self,
        image_arg: ImageArg,
        api_request: ApiRequest
    ) -> OptimizationResponse:

        try:
            res1 = await self._http_requester.submit_with_body(
                image_arg,
                api_request,
                UseTag.POST_BYTES,
                0
            )
            if res1.status == 201 and res1.body.get('status') == 'queued':
                # Got here, meaning that the image was successfully submitted.
                # Next, we need to wait for it to be optimized.... do wait a
                # little
                # before submitting the first request... 10 seconds will do
                await asyncio.sleep(10)
                return await self._wait_for_ready(
                    0,
                    api_request,
                    0,
                    image_arg
                )
            else:
                self.emit_debug_message(
                    '_continue_to_submit, got bad response status: {}'.format(
                        res1.status
                    )
                )
                rn = RejectionNotice(
                    rejection_notice=RejectionNoticeEnum.UNCLEAR
                )
                return OptimizationResponse(
                    status=OptimizationResponseStatus.FAILURE,
                    rejection_notice=rn
                )
        except RequestIssueException as e:
            self.emit_debug_message(
                '_continue_to_submit, http request error: {}'.format(
                   str(e)
                )
            )
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.HTTP_REQUEST_ERROR,
                inner_error=e
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )
        except Exception as e:
            self.emit_debug_message(
                '_continue_to_submit, unexpected error: {}'.format(
                   str(e)
                )
            )
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.UNCLEAR
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

    async def _wait_for_ready(
        self,
        total_time_used: int,
        api_request: ApiRequest,
        attempt_no: int,
        image_arg: ImageArg
    ) -> OptimizationResponse:
        # 20 minutes is kind of long and should not happen, but ...
        # Make this configurable.
        if total_time_used >= 1200:
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.TIMEOUT
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )
        try:
            res0 = await self._http_requester.empty_submit(
                api_request,
                UseTag.CHECK_PROCESSING_STATUS,
                attempt_no
            )
            success_or_deny = res0.body.get('success_or_deny')
            if res0.status == 200 and success_or_deny == 'success':
                # It means we already have an optimized image.
                optimization_response = await self._handle_ready_response(
                    res0.body
                )
                self.emit_debug_message('Got optimized image!')
                return optimization_response

            if success_or_deny == 'deny':
                rn = RejectionNotice(
                    rejection_notice=RejectionNoticeEnum.IMAGE_IS_TOO_BIG
                )
                return OptimizationResponse(
                    status=OptimizationResponseStatus.FAILURE,
                    rejection_notice=rn
                )

            if success_or_deny == 'processing':
                await asyncio.sleep(30)
                # Let's wait and call again.
                again = self._wait_for_ready(
                    30 + total_time_used,
                    api_request,
                    attempt_no + 1,
                    image_arg
                )

                return await again

            # If came here, it's probably because we need a file.
            if success_or_deny == 'expecting-file':
                self.emit_debug_message(
                    '_wait_for_ready: "expecting-file", re-uploading the file...'
                )
                stream_factory = await stream_from_argument(image_arg)
                return await self._continue_to_submit(
                    stream_factory,
                    api_request
                )

            # Working around infelicity with temporary errors.
            if res0.status == 404:
                # This may happen after submit in the time where the trace
                # has not yet been indexed by ES...
                self.emit_debug_message(
                    'Got 404 waiting for ready: {}, will re-try'.format(
                        str(res0)
                    )
                )
                # Let's wait and call again
                await asyncio.sleep(30)
                # Let's wait and call again
                again = self._wait_for_ready(
                    30 + total_time_used,
                    api_request,
                    attempt_no + 1,
                    image_arg
                )

                return await again

            # I shouldn't make it here!
            self.emit_debug_message(
                'ERROR: Got to end of "_wait_for_read" {}'.format(res0.status)
            )
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.UNCLEAR
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )
        except RequestIssueException as e:
            self.emit_debug_message('ERROR: HTTP error: {}'.format(str(e)))
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.HTTP_REQUEST_ERROR,
                inner_error=e
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )
        except Exception as e:
            self.emit_debug_message('ERROR: Unclear: {}'.format(str(e)))
            rn = RejectionNotice(
                rejection_notice=RejectionNoticeEnum.UNCLEAR
            )
            return OptimizationResponse(
                status=OptimizationResponseStatus.FAILURE,
                rejection_notice=rn
            )

    def emit_debug_message(self, msg: str):
        if self.debug_mode:
            self._logger.debug('[Submit machine]: %s', msg)
