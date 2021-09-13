import os
import logging
from uuid import UUID, uuid1
from typing import Dict, Optional, Tuple
from importlib.metadata import version

from rkclient.client import RKClient
from rkclient.entities import PEM, Artifact

log = logging.getLogger("rkclient")

RK_VERSION = version('RecordKeeper_Client')
MOCK_ENV_VAR = "RK_MOCK"


class RKClientMock(RKClient):
    def __init__(self, receiver_url: str, emitter_id: Optional[UUID] = None, timeout_sec: int = 5): # noqa
        log.info(f"ver {RK_VERSION} - using MOCK client")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def prepare_pem(self,
                    type: str,
                    predecessor_id: Optional[UUID] = None,
                    properties: Optional[Dict] = None,
                    tag_name: str = 'latest',
                    tag_namespace: Optional[UUID] = None) -> PEM:
        return PEM(uuid1(), 'mocked', None, uuid1(), '')

    def prepare_artifact(self,
                         type: str,
                         properties: Dict[str, str],
                         uid: Optional[UUID] = None) -> Artifact:
        return Artifact(uuid1(), 'mocked', {}, False)

    def send_pem(self, pem: PEM) -> Tuple[str, bool]:
        log.debug("send pem - mocked")
        return "", True

    def ping(self) -> Tuple[str, bool]:
        log.debug("ping - mocked")
        return "", True

    def get_info(self) -> Tuple[str, bool]:
        log.debug("get info - mocked")
        return "{'postgres_enabled': true, 'neo4j_enabled': true, 'version':" + RK_VERSION + "} ", True

    def get_tag(self, namespace: UUID, tag_name: str) -> Tuple[str, bool]:
        log.debug("get tag - mocked")
        return "", True

    def set_tag(self, namespace: UUID, tag_name: str, pem: PEM) -> Tuple[str, bool]:
        log.debug("set tag - mocked")
        return "", True


class RKClientFactory:

    @staticmethod
    def get(*args, **kwargs) -> RKClient:
        rk_mock = os.environ.get(MOCK_ENV_VAR)
        if rk_mock is not None and rk_mock.lower() == 'true':
            return RKClientMock(*args, **kwargs)
        else:
            return RKClient(*args, **kwargs)
