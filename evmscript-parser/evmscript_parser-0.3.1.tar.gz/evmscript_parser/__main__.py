"""
CLI of EVM scripts parser.
"""
import sys
import logging
import argparse

from mimetypes import guess_type, types_map

from .package import CLI_NAME
from .core.parse import parse_script
from .core.decode import decode_function_call
from .core.decode.ABI import ABIProviderEtherscanApi
from .core.exceptions import (
    ParseStructureError,
    ABIEtherscanNetworkError, ABIEtherscanStatusCode
)

from .core.decode.ABI.etherscan import (
    DEFAULT_NET, NET_URL_MAP
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        add_help=True,
        description=__doc__,
        prog=CLI_NAME
    )

    parser.add_argument('evmscript',
                        type=str,
                        help='Encoded script string.')
    parser.add_argument('apitoken',
                        type=str,
                        help='API key as string or a path to txt file '
                             'with it.')

    parser.add_argument('--net',
                        type=str,
                        default=DEFAULT_NET,
                        help=f'net name is case-insensitive, '
                             f'default is {DEFAULT_NET}',
                        choices=NET_URL_MAP.keys())
    parser.add_argument('--debug-message',
                        action='store_true',
                        help='Show debug info')
    parser.add_argument('--retries',
                        type=int,
                        default=5,
                        help='Number of retries of calling Etherscan API.')

    return parser.parse_args()


def main():
    """Describe utils functionality."""
    args = parse_args()

    if args.debug_message:
        level = logging.DEBUG

    else:
        level = logging.INFO

    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=level
    )

    m_type, _ = guess_type(args.apitoken)
    if m_type == types_map['.txt']:
        with open(args.apitoken, 'r') as api_token_file:
            token = api_token_file.read().strip()

    else:
        token = args.apitoken

    logging.debug(f'API key: {token}')

    try:
        parsed = parse_script(args.evmscript)
    except ParseStructureError as err:
        logging.error(f'Parsing error: {repr(err)}')
        sys.exit(1)

    abi_provider = ABIProviderEtherscanApi(
        token, args.net, args.retries
    )

    calls = []
    for call in parsed.calls:
        try:
            calls.append(decode_function_call(
                call.address, call.method_id, call.encoded_call_data,
                abi_provider
            ))

        except ABIEtherscanNetworkError as err:
            logging.error(f'Network layer error: {repr(err)}')

        except ABIEtherscanStatusCode as err:
            logging.error(f'API error: {repr(err)}')

    logging.info(f'Parsed:\n{repr(calls)}')


if __name__ == '__main__':
    main()
