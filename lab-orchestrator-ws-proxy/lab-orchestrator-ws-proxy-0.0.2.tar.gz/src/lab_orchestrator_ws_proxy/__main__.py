"""
Environment Variables:
- SECRET_KEY: Secret key that should be used for jwt token decode.
- LOCAL_DEV_MODE: If False, it's assumed that this is run inside kubernetes. If True secure connections are disabled.
                  Default: False
- HOST: The host this proxy runs on. Default: 0.0.0.0
- PORT: The port this proxy runs on. Default: 5001
- KUBERNETES_SERVICE_HOST: Host where to proxy the websockets. Inside of kubernetes this has a preset default value.
- KUBERNETES_SERVICE_PORT: Port where to proxy the websockets. Inside of kubernetes this has a preset default value.
- LOGLEVEL: Python Loglevel to use. Default: INFO
"""
import os
import logging
from distutils.util import strtobool

from lab_orchestrator_ws_proxy_lib import ws_proxy_lib


LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)


def main():
    secret_key = os.environ["SECRET_KEY"]
    api_path = "/apis/subresources.kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/{vmi_name}/vnc"
    local_dev_mode = bool(strtobool(os.environ.get("LOCAL_DEV_MODE", "False")))
    ws_proxy_host = os.environ.get("HOST", "0.0.0.0")
    ws_proxy_port = int(os.environ.get("PORT", "5001"))
    kubernetes_service_host = os.environ["KUBERNETES_SERVICE_HOST"]
    kubernetes_service_port = os.environ["KUBERNETES_SERVICE_PORT"]
    if local_dev_mode:
        # local dev mode
        remote_url = os.environ.get("WS_REMOTE_URL", "ws://localhost:8001")
    else:
        # kubernetes mode
        remote_url = f"wss://{kubernetes_service_host}:{kubernetes_service_port}"
    ws = ws_proxy_lib.WebsocketProxy(remote_url=remote_url, api_path=api_path, local_dev_mode=local_dev_mode,
                                     secret_key=secret_key)
    logging.info("Starting WebsocketProxy")
    logging.info(f"Local Dev Mode: {local_dev_mode}")
    logging.info(f"Kubernetes Service Host: {kubernetes_service_host}")
    logging.info(f"Kubernetes Service Port: {kubernetes_service_port}")
    logging.info(f"Remote Url: {remote_url}")
    ws.run(ws_proxy_host, ws_proxy_port)
    logging.info("Stopped WebsocketProxy")


if __name__ == '__main__':
    main()
