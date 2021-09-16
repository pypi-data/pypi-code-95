__all__ = ["Definition"]

from ....tools import create_str_definition
from .._curves._forward_curve_request_item import ForwardCurveRequestItem
from .._curves._forward_curve_types import (
    OptStr,
    ExtendedParams,
    CurveDefinition,
    ForwardCurveDefinitions,
    CurveParameters,
)
from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType


class Definition(ContentProviderLayer):
    """
    Parameters
    ----------
    curve_definition : SwapZcCurveDefinition, optional

    curve_parameters : SwapZcCurveParameters, optional

    forward_curve_definitions : list of ForwardCurveDefinition, optional

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
     >>> import refinitiv.data.content.ipa.curves.forward_curve as forward_curve
     >>> definition = forward_curve.Definition(
     ...     curve_definition=forward_curve.SwapZcCurveDefinition(
     ...         currency="EUR",
     ...         index_name="EURIBOR",
     ...         name="EUR EURIBOR Swap ZC Curve",
     ...         discounting_tenor="OIS",
     ...     ),
     ...     forward_curve_definitions=[
     ...         forward_curve.ForwardCurveDefinition(
     ...             index_tenor="3M",
     ...             forward_curve_tag="ForwardTag",
     ...             forward_start_date="2021-02-01",
     ...             forward_curve_tenors=[
     ...                 "0D",
     ...                 "1D",
     ...                 "2D",
     ...                 "3M",
     ...                 "6M",
     ...                 "9M",
     ...                 "1Y",
     ...                 "2Y",
     ...                 "3Y",
     ...                 "4Y",
     ...                 "5Y",
     ...                 "6Y",
     ...                 "7Y",
     ...                 "8Y",
     ...                 "9Y",
     ...                 "10Y",
     ...                 "15Y",
     ...                 "20Y",
     ...                 "25Y"
     ...             ]
     ...         )
     ...     ]
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
        curve_definition: CurveDefinition = None,
        forward_curve_definitions: ForwardCurveDefinitions = None,
        curve_parameters: CurveParameters = None,
        curve_tag: OptStr = None,
        extended_params: ExtendedParams = None,
    ):
        request_item = ForwardCurveRequestItem(
            curve_definition=curve_definition,
            forward_curve_definitions=forward_curve_definitions,
            curve_parameters=curve_parameters,
            curve_tag=curve_tag,
        )
        super().__init__(
            content_type=ContentType.FORWARD_CURVE,
            universe=request_item,
            extended_params=extended_params,
        )

    def __repr__(self):
        return create_str_definition(
            self, middle_path="content.ipa.curves", end_path="forward_curve"
        )
