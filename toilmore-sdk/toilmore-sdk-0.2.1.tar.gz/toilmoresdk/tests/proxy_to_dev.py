import os
import subprocess as sp
import time

from toilmoresdk.api_config import ApiEndpoint

WIREMOCK_JAR = (
    "wiremock-jre8-standalone-2.27.0.jar"
)
PREDEFINED_PORT = 9253
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WIREMOCK_ROOT_DIR = os.path.abspath(
    os.path.join(
        THIS_DIR,
        'dev_support'
    )
)


class ProxyServer(object):

    def __init__(
        self,
        start_proxy: bool = None,
        use_root: str = None,
        wire_mock_root_dir: str = None
    ):
        self.p = None
        if start_proxy is None:
            start_proxy = True
        self.start_proxy = start_proxy
        if start_proxy:
            if not wire_mock_root_dir:
                wire_mock_root_dir = WIREMOCK_ROOT_DIR
            jar_path = os.path.join(wire_mock_root_dir, WIREMOCK_JAR)
            assert isinstance(use_root, str)
            use_root_s = use_root
            wiremock_root = os.path.join(wire_mock_root_dir, use_root_s)
            args = [
                "java",
                "-jar", jar_path,
                "--root-dir", wiremock_root,
                "--port", str(PREDEFINED_PORT),
                "--verbose"
            ]
            self.p = sp.Popen(args)
            cmd_line = " ".join(args)
            print(f"Will run: {cmd_line}")

    def get_ip(self):
        if self.start_proxy:
            time.sleep(10)
        return '127.0.0.1'

    def prepare_light_api(self) -> ApiEndpoint:
        return ApiEndpoint(
            protocol="http",
            port=PREDEFINED_PORT,
            host=self.get_ip(),
            version="2020.1",
            api_module="light"
        )

    def kill_process(self):
        if self.p:
            self.p.kill()
