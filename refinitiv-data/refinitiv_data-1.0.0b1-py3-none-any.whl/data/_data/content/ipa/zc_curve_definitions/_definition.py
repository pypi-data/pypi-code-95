__all__ = ["Definition"]

from numpy import iterable

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType


class Definition(ContentProviderLayer):
    def __init__(self, universe, extended_params=None):
        if not iterable(universe):
            universe = [universe]

        super().__init__(
            content_type=ContentType.ZC_CURVE_DEFINITIONS,
            universe=universe,
            extended_params=extended_params,
        )
