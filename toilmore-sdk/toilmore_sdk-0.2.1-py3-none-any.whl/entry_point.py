"""
toilmoresdk command line to optimize images. As a general note when you use
[-v | --verbose] parameter the logger will show the logs that happen while
the image is being optimized. Examples of usage:

- Light API request:

$ toilmoresdk --api-endpoint light --image-path ./my_image.jpg --api-token 143d6bf8edd1fbf240803c972dd1de0f38b3a4b5 --domain pixellena.com --precursor webp0 --max-overhead 2 --output ./my_image.webp --verbose

or with the short version of the parameters:

$ toilmoresdk -e light -i ./my_image.jpg -t 143d6bf8edd1fbf240803c972dd1de0f38b3a4b5 -d pixellena.com -p webp0 -m 2 -o ./my_image.webp -v

- Lux API request:

$ toilmoresdk --api-endpoint lux --image-path ./my_image.jpg --api-token 143d6bf8edd1fbf240803c972dd1de0f38b3a4b5 --domain pixellena.com --precursor webp0 --adjustments ./my_adjustments.json --output ./my_image.webp --verbose

or with the short version of the parameters:

$ toilmoresdk -e lux -i ./my_image.jpg -t 143d6bf8edd1fbf240803c972dd1de0f38b3a4b5 -d pixellena.com -p webp0 -a ./my_adjustments.json -o ./my_image.webp -v

"""

import argparse
import sys
import os
import logging
import asyncio

from toilmoresdk.environment.logging import setup_logger
from toilmoresdk import constants
from toilmoresdk import (
    LIGHT_API,
    LUX_API,
    Toilmore,
)
from toilmoresdk.http_requester import (
    EnvelopeOptions,
)
from toilmoresdk.submit_machine import (
    OptimizationResponseStatus,
    RejectionNoticeToHumanEnum,
)
from toilmoresdk.stream_helpers import store_file_content
from toilmoresdk.version import __version__


def main():
    print(f'toilmoresdk=={__version__}')
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action='store_true',
        help="Show more detailed logs, mainly for debugging purposes."
    )
    parser.add_argument(
        '-e',
        '--api-endpoint',
        dest='api_endpoint',
        required=True,
        help="Toilmore API sub-service. Possible values are either: "
             "'light' or 'lux'."
    )
    parser.add_argument(
        '-i',
        '--image-path',
        dest='image_path',
        required=True,
        help="Image path."
    )
    parser.add_argument(
        '-d',
        '--domain',
        dest='domain',
        required=True,
        help="Domain."
    )
    parser.add_argument(
        '-t',
        '--api-token',
        dest='api_token',
        required=True,
        help="Authentication token."
    )
    parser.add_argument(
        '-p',
        '--precursor',
        dest='precursor',
        required=True,
        help="Precursor. The format to which the optimized image will be "
             "encoded. Possible values: [webp0, avifo0, jp2o0, prjpg, pngzo]"
    )
    parser.add_argument(
        "-a",
        "--adjustments",
        nargs='?',
        default='',
        dest='adjustments',
        help="Path to the adjustments file in JSON format. "
             "To know more about the adjustments please visit: "
             "https://demo.pixellena.com/adjustments/"
    )
    parser.add_argument(
        "-m",
        "--max-overhead",
        nargs='?',
        default='',
        dest='max_overhead',
        help="Produces a deny status response if the resulting image is "
             "bigger than the original image times the value of this "
             "parameter. The default value is 0.99, minimum 0.1, "
             "and maximum 10."
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs='?',
        default='',
        dest='output',
        help="Either the absolute path to where the optimized image will be "
             "stored at, or just the  optimized image filename. In case it is "
             "not an absolute path we will assume it is a filename, and we "
             "will store it at the same directory the original image is."
    )

    ############### Now we can parse the arguments ############################
    args = parser.parse_args()

    is_verbose = hasattr(args, 'verbose') and args.verbose
    debug_level = logging.DEBUG if is_verbose else logging.ERROR
    setup_logger(level=debug_level)
    logger = logging.getLogger("toilmoresdk")

    api = args.api_endpoint
    if api not in [
        constants.LIGHT_API_KEY,
        constants.LUX_API_KEY
    ]:
        logger.error(
            'Bad input error: "api sub-service" parameter must be one of: '
            '[%s, %s].',
            constants.LIGHT_API_KEY,
            constants.LUX_API_KEY
        )
        sys.exit(5)
    image_path = args.image_path
    if not os.path.isfile(image_path):
        logger.error(
            'Bad input error: "image-path" the image %s does not exist, '
            'or it is not a valid file.',
            image_path
        )
        sys.exit(5)

    api_token = args.api_token
    domain = args.domain
    precursor_arg = args.precursor
    allowed_precursors = constants.PrecursorEnum.list()
    if precursor_arg not in allowed_precursors:
        logger.error(
            'Bad input error: "precursor", it must be one of %s',
            allowed_precursors
        )
        sys.exit(5)
    precursor = constants.PrecursorEnum(args.precursor)

    max_overhead = args.max_overhead
    envelope_options = None
    adjustments = None
    if api == constants.LIGHT_API_KEY:
        api_endpoint = LIGHT_API
        if max_overhead:
            envelope_options = EnvelopeOptions(
                max_overhead=max_overhead
            )
    else:
        api_endpoint = LUX_API
        adjustments_path = args.adjustments
        if not os.path.isfile(adjustments_path):
            logger.error(
                'Bad input error: "adjustments" the adjustments JSON file at '
                '%s does not exist, '
                'or it is not a valid file.',
                adjustments_path
            )
            sys.exit(5)
    toilmore = Toilmore(
        {
            'api_endpoint': api_endpoint,
            'api_token': api_token,
            'domain': domain,
            'debug_mode': is_verbose,
        }
    )

    loop = asyncio.get_event_loop()
    r = loop.run_until_complete(
        toilmore.optimize(
            image_path,
            precursor,
            adjustments,
            envelope_options
        )
    )

    if r.status == OptimizationResponseStatus.FAILURE:
        rejection_notice = r.rejection_notice
        rejection_notice_enum = rejection_notice.rejection_notice
        human_readable_explanation = (
            RejectionNoticeToHumanEnum[rejection_notice_enum.name].value
        )
        print(
            f'Failure: {human_readable_explanation}'
        )
    elif r.status == OptimizationResponseStatus.SUCCESS:
        output = args.output
        optimized_image_dir_abs_path = os.path.abspath(
            os.path.dirname(image_path)
        )
        base_filename, file_extension = os.path.splitext(image_path)
        output_filename = '{}{}'.format(
            base_filename,
            constants.PrecursorToExtensionEnum[precursor.name].value
        )
        if output:
            if os.path.isdir(output):
                output = os.path.join(output, output_filename)
            # Let's assume just the filename was set as output, and we then
            # store it where the original image is.
            else:
                output = os.path.join(optimized_image_dir_abs_path, output)
        else:
            output = os.path.join(
                optimized_image_dir_abs_path,
                output_filename
            )
        loop.run_until_complete(
            store_file_content(r.response_stream, output)
        )
        print(f'Optimized image stored at: {output}')


if __name__ == '__main__':

    main()
