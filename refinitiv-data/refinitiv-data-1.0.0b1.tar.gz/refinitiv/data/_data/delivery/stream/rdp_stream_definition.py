# coding: utf-8
from .rdp_stream import RDPStream


class Definition:
    """
    This class to subscribe to streaming items of RDP streaming protocol
    that exposed by the underlying of the Refinitiv Data

    Parameters
    ----------
    service: string, optional
        name of RDP service
    universe: list
        RIC to retrieve item stream.
    view: list
        data fields to retrieve item stream
    parameters: dict
        extra parameters to retrieve item stream.
    api: string
        specific name of RDP streaming defined
        in config file. i.e. 'streaming/trading-analytics/redi'
    extended_params: dict, optional
        Specify optional params
        Default: None

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.delivery import rdp_stream
    >>> defintion = rd.delivery.rdp_stream.Definition(
    ...     service=None,
    ...     universe=[],
    ...     view=None,
    ...     parameters={"universeType": "RIC"},
    ...     api='streaming/trading-analytics/redi'
    ... )
    """

    def __init__(
        self,
        service: str,
        universe: list,
        view: list,
        parameters: dict,
        api: str,
        extended_params=None,
        on_ack=None,
        on_response=None,
        on_update=None,
        on_alarm=None,
    ):
        self._service = service
        self._universe = universe
        self._view = view
        self._parameters = parameters
        self._api = api
        self._extended_params = extended_params
        self._on_ack = on_ack
        self._on_response = on_response
        self._on_update = on_update
        self._on_alarm = on_alarm

    def get_stream(self, session=None):
        from ...core.session import get_valid_session

        session = get_valid_session(session)

        stream = RDPStream(
            session=session,
            service=self._service,
            universe=self._universe,
            view=self._view,
            parameters=self._parameters,
            api=self._api,
            extended_params=self._extended_params,
            on_ack=self._on_ack,
            on_response=self._on_response,
            on_update=self._on_update,
            on_alarm=self._on_alarm,
        )
        return stream
