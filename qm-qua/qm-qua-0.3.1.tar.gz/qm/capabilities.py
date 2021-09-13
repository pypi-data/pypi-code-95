import dataclasses
from typing import Optional

from qua.info import QuaMachineInfo


@dataclasses.dataclass
class ServerCapabilities:
    has_job_streaming_state: bool

    @staticmethod
    def build(qop_version: str, qua_implementation: Optional[QuaMachineInfo]):
        return ServerCapabilities(
            has_job_streaming_state=_has_job_streaming_state(
                qop_version, qua_implementation
            )
        )


def _has_job_streaming_state(
    qop_version: str, qua_implementation: Optional[QuaMachineInfo]
):
    if qop_version is not None:
        if qop_version.startswith("2.10"):
            return True
    if qua_implementation is not None:
        return "qm.job_streaming_state" in qua_implementation.capabilities
    return False
