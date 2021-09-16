from typing import Optional, Callable, Union, List

import pandas

from .. import Session
from ..content.streaming.streamingprices import StreamingPrices
from ..delivery.stream.state import StreamState as State
from ..tools._common import cached_property
from ..tools._repr_definition import create_str_definition


class Stream:
    """
    Summary line of this class are used for requesting, processing and managing a set of
    streaming level 1 (MarketPrice domain) quotes and trades

    Extended description of this class:
        The object automatically manages a set of streaming caches available for access
        at any time. Your application can then reach into this cache and pull out
        real-time fields by just calling a simple access method.
        The object also emits a number of different events, your application can
        listen to in order to be notified of the latest field values in real-times.
        The object iterable.

    Parameters
    ----------
    session : Session, optional
        Means default session would be used
    universe : str or list of str, optional
        The single/multiple instrument/s name (e.g. "EUR=" or ["EUR=", "CAD=", "UAH="])
    fields : list, optional
        Specifies the specific fields to be delivered when messages arrive
    extended_params : dict, optional
        If necessary other parameters

    Examples
    --------
    >>> from refinitiv.data.content import pricing
    >>> definition = pricing.Definition("EUR=")
    >>> stream = definition.get_stream()
    """

    def __init__(
        self,
        session: Session = None,
        universe: Union[str, List[str]] = None,
        fields: Optional[list] = None,
        extended_params: Optional[dict] = None,
    ) -> None:
        self._session = session
        self._universe = universe or []
        self._fields = fields
        self._extended_params = extended_params

    @cached_property
    def _stream(self) -> StreamingPrices:
        return StreamingPrices(
            universe=self._universe,
            session=self._session,
            fields=self._fields,
            extended_params=self._extended_params,
        )

    def open(self, with_updates: bool = True) -> State:
        """
        Summary line of this func open the Pricing connection by sending corresponding
        requests for all requested instruments

        Extended description of this class:
             It will be opened once all the requested instruments are received
             either on_refresh, on_status or other method.
             Then the pricing.Stream can be used in order to retrieve data.

        Parameters
        ----------
        with_updates : bool, optional
            actions:
                True - the streaming will work as usual and the data will be received
                continuously.
                False - only one data snapshot will be received
                (single Refresh 'NonStreaming') and stream will be closed automatically.

            Default: True

        Returns
        -------
        pricing.State

        Examples
        --------
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition("EUR=")
        >>> stream = definition.get_stream()
        >>> stream.open()
        """
        return self._stream.open(with_updates=with_updates)

    def close(self) -> State:
        """
        Summary line of this func closes the pricing connection, releases resources

        Returns
        -------
        pricing.State

        Examples
        --------
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition("EUR=")
        >>> stream = definition.get_stream()
        >>> stream.open()
        >>> stream.close()
        """
        return self._stream.close()

    def get_fields(self, universe: str, fields: Optional[list] = None) -> dict:
        """
        Returns a dict of the fields for a requested universe.

        Parameters
        ----------
        universe: str
            Name of the instrument (e.g. 'EUR=' ...).
        fields: list, optional
            The fields that are listed in the `fields` parameter.

        Returns
        -------
        dict

        Examples
        --------
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition(["AIRP.PA", "AIR.PA", "ALSO.PA"])
        >>> stream = definition.get_stream()
        >>> fields = stream.get_fields("AIRP.PA")
        >>> fields
        ... {'AIRP.PA': {'BID': 147.14, 'ASK': 147.16}}
        """
        _fields = {
            universe: {
                key: value
                for key, value in self._stream[universe].items()
                if fields is None or key in fields
            }
        }
        return _fields

    def get_snapshot(
        self,
        universe: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        convert: bool = True,
    ) -> pandas.DataFrame:
        """
        Returns a Dataframe filled with snapshot values for a list of instrument names
        and a list of fields.

        Parameters
        ----------
        universe: list of str, optional
            List of instruments to request snapshot data on.

        fields: list of str, optional
            List of fields to request.

        convert: bool, optional
            If True, force numeric conversion for all values.
            By default True.

        Returns
        -------
            pandas.DataFrame

            pandas.DataFrame content:
                - columns : instrument and fieled names
                - rows : instrument name and field values

        Raises
        ------
            Exception
                If request fails or if server returns an error

            ValueError
                If a parameter type or value is wrong

        Examples
        --------
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition(
        ...    ["MSFT.O", "GOOG.O", "IBM.N"],
        ...    fields=["BID", "ASK", "OPEN_PRC"]
        ...)
        >>> stream = definition.get_stream()
        >>> data = stream.get_snapshot(["MSFT.O", "GOOG.O"], ["BID", "ASK"])
        >>> data
        ... "      Instrument   BID       ASK        "
        ... "0     MSFT.O        150.9000   150.9500 "
        ... "1     GOOG.O        1323.9000  1327.7900"
        """
        return self._stream.get_snapshot(
            universe=universe, fields=fields, convert=convert
        )

    def on_refresh(self, func: Callable) -> "Stream":
        """
        Called when a stream on instrument_name was opened successfully or when the
        stream is refreshed by the server
        This callback is called with the reference to the steam object, the instrument
        name and the instrument full image

        Parameters
        ----------
        func : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        --------
        >>> import datetime
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition("EUR=")
        >>> stream = definition.get_stream()
        >>> def on_refresh(stream, ric, message):
        ...    current_time = datetime.datetime.now().time()
        ...    print("\t{} | Receive refresh [{}] : {}".format(current_time, ric, message))
        >>> stream.on_refresh(on_refresh)
        >>> stream.open()
        """
        self._stream.on_refresh(func)
        return self

    def on_update(self, func: Callable) -> "Stream":
        """
        Called when an update is received for a instrument_name
        This callback is called with the reference to the stream object, the instrument
        name and the instrument update

        Parameters
        ----------
        func : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        --------
        >>> import datetime
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition("EUR=")
        >>> stream = definition.get_stream()
        >>> def on_update(stream, ric, update):
        ...     current_time = datetime.datetime.now().time()
        ...     print("\t{} | Receive update [{}] : {}".format(current_time, ric, update))
        >>> stream.on_update(on_update)
        >>> stream.open()
        """
        self._stream.on_update(func)
        return self

    def on_status(self, func: Callable) -> "Stream":
        """
        Called when a status is received for a instrument_name
        This callback is called with the reference to the stream object, the instrument
        name and the instrument status

        Parameters
        ----------
        func : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        --------
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition("EUR=")
        >>> stream = definition.get_stream()
        >>> def on_status(stream, ric, status):
        ...     print("\tReceive status [{}] : {}".format(ric, status))
        >>> stream.on_status(on_status)
        >>> stream.open()
        """
        self._stream.on_status(func)
        return self

    def on_complete(self, func: Callable) -> "Stream":
        """
        Called when all subscriptions are completed
        This callback is called with the reference to the stream object

        Parameters
        ----------
        func : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        --------
        >>> import datetime
        >>> from refinitiv.data.content import pricing
        >>> definition = pricing.Definition("EUR=")
        >>> stream = definition.get_stream()
        >>> def on_complete(stream):
        ...    current_time = datetime.datetime.now().time()
        ...    print("\t{} | Receive complete".format(current_time))
        >>> stream.on_complete(on_complete)
        >>> stream.open()
        """
        self._stream.on_complete(func)
        return self

    def on_error(self, func: Callable) -> "Stream":
        self._stream.on_error(func)
        return self

    def __iter__(self):
        return self._stream.__iter__()

    def __getitem__(self, item):
        return self._stream.__getitem__(item)

    def __len__(self):
        return self._stream.__len__()

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content",
            end_path="pricing",
            name_class=self.__class__.__name__,
            content=f"{{name='{self._universe}'}}",
        )
