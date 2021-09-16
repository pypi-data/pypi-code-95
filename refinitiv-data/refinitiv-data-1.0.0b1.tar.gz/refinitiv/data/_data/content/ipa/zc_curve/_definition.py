__all__ = ["Definition"]

from ....tools import create_str_definition

from .._curves._zc_curve_types import OptConstituents, CurveDefinition, CurveParameters
from ..._content_provider import ContentProviderLayer
from .._curves._zc_curve_request_item import ZcCurveRequestItem
from ..._content_type import ContentType
from ..._types import OptStr, ExtendedParams


class Definition(ContentProviderLayer):
    """
    Parameters
    ----------
    constituents : Constituents, optional

    curve_definition : ZcCurveDefinitions, optional

    curve_parameters : ZcCurveParameters, optional

    curve_tag : str, optional

    extended_params : dict, optional
        If necessary other parameters.

    Methods
    -------
    get_data(session=session, on_response=on_response)
        Returns a response to the data platform
    get_data_async(session=None, on_response=None, async_mode=None)
        Returns a response asynchronously to the data platform

    Examples
    --------
     >>> import refinitiv.data.content.ipa.curves.zc_curve as zc_curve
     >>> definition = zc_curve.Definition(
     ...     curve_definition=zc_curve.ZcCurveDefinitions(
     ...         currency="CHF",
     ...         name="CHF LIBOR Swap ZC Curve",
     ...         discounting_tenor="OIS",
     ...     ),
     ...     curve_parameters=zc_curve.ZcCurveParameters(
     ...         use_steps=True
     ...     )
     ... )
     >>> response = definition.get_data()

     Using get_data_async
     >>> import asyncio
     >>> task = asyncio.gather(
     ...    definition.get_data_async(),
     ...)
     >>> asyncio.get_event_loop().run_until_complete(task)
     >>> response, *_ = task.result()
    """

    def __init__(
        self,
        constituents: OptConstituents = None,
        curve_definition: CurveDefinition = None,
        curve_parameters: CurveParameters = None,
        curve_tag: OptStr = None,
        extended_params: ExtendedParams = None,
    ):
        request_item = ZcCurveRequestItem(
            constituents=constituents,
            curve_definition=curve_definition,
            curve_parameters=curve_parameters,
            curve_tag=curve_tag,
        )
        super().__init__(
            content_type=ContentType.ZC_CURVES,
            universe=request_item,
            extended_params=extended_params,
        )

    def __repr__(self):
        return create_str_definition(
            self, middle_path="content.ipa.curves", end_path="zc_curve"
        )
