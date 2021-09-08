import os
import asyncio

from toilmoresdk import (
    Toilmore,
)
from toilmoresdk.submit_machine import OptimizationResponseStatus
from toilmoresdk.api_config import ApiConfig
from toilmoresdk.constants import PrecursorEnum
from toilmoresdk.tests.proxy_to_dev import ProxyServer

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WIREMOCK_ROOT_DIR = os.path.abspath(
    os.path.join(
        THIS_DIR,
        '../../../../javascript/src/dev_support'
    )
)

proxy_server = ProxyServer(
    True,
    "wiremock-root-no-faults",
    WIREMOCK_ROOT_DIR
)

config = ApiConfig(
    # LIGHT_API contains our light api endpoint.
    api_endpoint=proxy_server.prepare_light_api(),
    # Use a valid API token below:
    api_token='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    # Use a valid domain below, as received when
    # you created the token.
    domain='shimmercat.com',
    debug_mode=True
)

toilmore = Toilmore(config)

loop = asyncio.get_event_loop()

image_path = "./32x32.png"
precursor = PrecursorEnum.WEBP0
r = loop.run_until_complete(
    toilmore.optimize(image_path, precursor)
)

try:
    assert r.status == OptimizationResponseStatus.SUCCESS
    proxy_server.kill_process()
except AssertionError:
    proxy_server.kill_process()
    raise
