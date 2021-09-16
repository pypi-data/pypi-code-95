__all__ = ["Definition"]

from numpy import iterable

from .._ipa_content_provider import IPAContentProviderLayer
from ..._content_type import ContentType


class Definition(IPAContentProviderLayer):
    def __init__(
        self,
        universe,
        surface_layout=None,
        outputs=None,
        extended_params=None,
    ):
        if not iterable(universe):
            universe = [universe]

        super().__init__(
            content_type=ContentType.SURFACES,
            universe=universe,
            outputs=outputs,
            extended_params=extended_params,
        )
