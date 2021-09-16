from typing import Optional, Any, Union, List

from ._hp_data_provider import Adjustments, EventTypes
from .._content_provider import ContentProviderLayer
from .._content_type import ContentType


class Definition(ContentProviderLayer):
    """
    Summary line of this class that defines parameters for requesting events from historical pricing

    Parameters
    ----------
    universe : str
        The entity universe
    eventTypes : list of EventTypes or EventTypes or str, optional
        The market events EventTypes
    start : str, optional
        The start date and timestamp of the query in ISO8601 with UTC only
    end : str, optional
        The end date and timestamp of the query in ISO8601 with UTC only
    adjustments : list of Adjustments or Adjustments or str, optional
        The adjustment list or Adjustments type
    count : int, optional
        The maximum number of data returned. Values range: 1 - 10000
    fields : list, optional
        The list of fields that are to be returned in the response
    closure : Any, optional
        Specifies the parameter that will be merged with the request
    extended_params : dict, optional
        If necessary other parameters

    Examples
    --------
    >>> from refinitiv.data.content.historical_pricing import events
    >>> definition_events = events.Definition("EUR")
    >>> response = definition_events.get_data()

    """

    def __init__(
        self,
        universe: str,
        eventTypes: Union[List[EventTypes], EventTypes, str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        adjustments: Union[List[Adjustments], Adjustments, str] = None,
        count: Optional[int] = None,
        fields: Optional[list] = None,
        closure: Optional[Any] = None,
        extended_params: Optional[dict] = None,
    ):
        super().__init__(
            content_type=ContentType.HISTORICAL_PRICING_EVENTS,
            universe=universe,
            event_types=eventTypes,
            start=start,
            end=end,
            adjustments=adjustments,
            count=count,
            fields=fields,
            closure=closure,
            extended_params=extended_params,
        )
