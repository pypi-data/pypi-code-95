__all__ = ["Definition"]

from numpy import iterable

from .._curves._zc_curve_types import Universe, Outputs
from ..._types import ExtendedParams
from ....tools import create_str_definition

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType


class Definition(ContentProviderLayer):
    """
    Parameters
    ----------
    universe : zc_curve.Definition, list of zc_curve.Definition

    outputs: list of (str or Outputs), optional
        Contains the sections that will be returned by the API.
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
     >>> import refinitiv.data.content.ipa.curves.zc_curves as zc_curves
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
     >>> definition = zc_curves.Definition(universe=definition)
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
        universe: Universe,
        outputs: Outputs = None,
        extended_params: ExtendedParams = None,
    ):
        if not iterable(universe):
            universe = [universe]

        super().__init__(
            content_type=ContentType.ZC_CURVES,
            universe=universe,
            outputs=outputs,
            extended_params=extended_params,
        )

    def __repr__(self):
        return create_str_definition(
            self, middle_path="content.ipa.curves", end_path="zc_curves"
        )
