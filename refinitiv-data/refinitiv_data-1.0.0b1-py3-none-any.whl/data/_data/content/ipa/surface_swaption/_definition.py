__all__ = ["Definition"]

from .._ipa_content_provider import IPAContentProviderLayer
from .._surfaces import SwaptionSurfaceRequestItem
from ..._content_type import ContentType


class Definition(IPAContentProviderLayer):
    def __init__(
        self,
        instrument_type=None,
        surface_layout=None,
        surface_parameters=None,
        underlying_definition=None,
        surface_tag=None,
        extended_params=None,
    ):
        request_item = SwaptionSurfaceRequestItem(
            instrument_type=instrument_type,
            surface_layout=surface_layout,
            surface_parameters=surface_parameters,
            underlying_definition=underlying_definition,
            surface_tag=surface_tag,
        )
        super().__init__(
            content_type=ContentType.SURFACES,
            universe=request_item,
            extended_params=extended_params,
        )
