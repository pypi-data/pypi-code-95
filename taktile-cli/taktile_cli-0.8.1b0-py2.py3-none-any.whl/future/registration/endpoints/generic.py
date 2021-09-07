import typing as t

from tktl.core.future.t import EndpointKinds

from .abc import Endpoint, XType, YType


class GenericEndpoint(Endpoint):
    kind: EndpointKinds = EndpointKinds.GENERIC

    @staticmethod
    def supported(
        *, X: XType = None, y: YType = None, profile: t.Optional[str] = None,
    ) -> bool:
        return profile is None and X is None and y is None
