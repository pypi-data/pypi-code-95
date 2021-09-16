__all__ = ["Definition"]

from .trade_data_service_stream import Stream
from ....tools import create_str_definition
from ....core import get_valid_session


class Definition:
    """
    This class describes Analytics Trade Data Service.

    Parameters
    ----------
    universe : list, optional
        A list of RIC or symbol or user's id for retrieving trading analytics data.
    fields : list, optional
        A list of enumerate fields.
    api : str, optional
        Means the default streaming API can be changed
    events : Events, optional
        Enable/Disable the detail of order event in the streaming.
        Default: False
    finalized_orders : FinalizedOrders, optional
        Enable/Disable the cached of finalized order of current day in the streaming.
        Default: False
    filters : list, optional
        Set the condition of subset of trading streaming data.
    universe_type : UniverseTypes, optional
        A type of given universe can be RIC, Symbol or UserID.
        Default: UniverseTypes.RIC
    extended_params : dict, optional
        If necessary other parameters

    Methods
    -------
    get_stream(session=session)
        Get stream object of this definition

    Examples
    --------
    >>> from refinitiv.data.content import trade_data_service
    >>> definition = trade_data_service.Definition()
    """

    def __init__(
        self,
        universe: list = None,
        fields: list = None,
        api: str = None,
        extended_params: dict = None,
        events: "Events" = None,
        finalized_orders: "FinalizedOrders" = None,
        filters: list = None,
        universe_type: "UniverseTypes" = None,
    ):
        self._universe = universe
        self._fields = fields
        self._api = api
        self._extended_params = extended_params
        self._universe_type = universe_type
        self._events = events
        self._finalized_orders = finalized_orders
        self._filters = filters

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content",
            end_path="trade_data_service",
            content={"universe": self._universe},
        )

    def get_stream(self, session=None) -> Stream:
        """
        Returns a streaming trading analytics subscription.

        Parameters
        ----------
        session : Session, optional
            The Session used by the TradeDataService to retrieve data from the platform

        Returns
        -------
        TradeDataStream

        Examples
        --------
        >>> from refinitiv.data.content import trade_data_service
        >>> definition = trade_data_service.Definition()
        >>> stream = definition.get_stream()
        >>> stream.open()
        """
        session = get_valid_session(session)
        stream = Stream(
            session=session,
            universe=self._universe,
            fields=self._fields,
            api=self._api,
            extended_params=self._extended_params,
            universe_type=self._universe_type,
            events=self._events,
            finalized_orders=self._finalized_orders,
            filters=self._filters,
        )
        return stream
