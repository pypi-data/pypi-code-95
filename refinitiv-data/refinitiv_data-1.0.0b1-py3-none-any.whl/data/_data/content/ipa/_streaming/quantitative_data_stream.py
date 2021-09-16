# coding: utf-8

import traceback
from collections.abc import Callable
import pandas as pd


from ....delivery.stream import RDPStream
from ....delivery.stream import StateManager


class QuantitativeDataStream(StateManager):
    """
        Open a streaming quantitative analytic service subscription.

    Parameters
    ----------
    universe: list

    fields: list

    api: str, optional
         Means the default streaming API can be changed

    extended_params: dict
        Default: None

    on_response: callable object (stream, response_message)
        Default: None

    on_update: callable object (stream, update_message)
        Default: None

    on_state: callable object (stream, state_message):
        Called when the stream has new state.
        Default: None

    Methods
    -------
    open()
        Open the QuantitativeDataStream connection
    close()
        Close the QuantitativeDataStream connection, releases resources
    get_snapshot()
        Get DataFrame with stream
    """

    class Params(object):
        def __init__(self, *args, **kwargs):
            self._universe = None
            self._fields = None
            self._extended_params = None
            #   callbacks
            self._on_response_cb = None
            self._on_update_cb = None
            #       state
            self._on_state_cb = None
            #       error
            self._on_error_cb = None

        def universe(self, universe: list):
            self._universe = universe
            return self

        def extended_params(self, extended_params: dict):
            self._extended_params = extended_params
            return self

        def on_response(self, on_response_cb: Callable):
            self._on_response_cb = on_response_cb
            return self

        def on_update(self, on_update_cb: Callable):
            self._on_update_cb = on_update_cb
            return self

        def on_state(self, on_state_cb: Callable):
            self._on_state_cb = on_state_cb
            return self

        def on_error(self, on_error_cb: Callable):
            self._on_error_cb = on_error_cb
            return self

    def __init__(
        self,
        universe: list,
        fields: list = None,
        #   extended parameters
        extended_params: dict = None,
        #   session
        session: object = None,
        api: str = None,
        #   callbacks
        on_response: Callable = None,
        on_update: Callable = None,
        on_state: Callable = None,
    ):

        #   QPS information
        self._universe = universe
        self._fields = fields
        self._extended_params = extended_params

        #   session
        from refinitiv.data._data.core.session import get_default

        self._session = session or get_default()
        assert self._session is not None

        #   initialize the parent classes
        StateManager.__init__(self, loop=self._session._loop, logger=self._session)

        #   api
        self._api = (
            api
            if api is not None
            else "streaming/quantitative-analytics/financial-contracts"
        )

        #   callback functions
        self._on_response_cb = on_response
        self._on_update_cb = on_update
        self._on_state_cb = on_state

        #   intermediate data for quantitative analytic
        self._data = None
        self._headers = None

        self._column_names = None if self._fields is None else self._fields

        #   build RDP item stream for QPS
        self._stream = RDPStream(
            session=self._session,
            service=None,
            view=self._fields,
            parameters=None,
            #   QPS parameters
            universe=self._universe,
            extended_params=self.extended_params,
            api=self._api,
            on_ack=self.__on_ack,
            on_response=self.__on_response,
            on_update=self.__on_update,
            on_alarm=self.__on_alarm,
        )

    def __repr__(self):
        repr_str = super().__repr__()
        repr_str = repr_str.replace(
            ">", f" {{name='{self._universe}', state={self.state}}}>"
        )
        return repr_str

    @property
    def extended_params(self):
        subscription_extended_params = (
            dict(self._extended_params) if self._extended_params is not None else {}
        )
        return subscription_extended_params

    @property
    def df(self):
        if self._data is None or self._column_names is None:
            #   no data for build a dataframe
            return

        #   build a dataframe with column name
        return pd.DataFrame.from_records(self._data, columns=self._column_names)

    def get_snapshot(self):
        """
        Returns DataFrame snapshot a streaming quantitative analytic service

        Returns
        -------
        pd.DataFrame

        """
        return self.df

    #   callbacks
    def on_response(self, on_response_cb: Callable):
        """
        This callback is called with the reference to the stream object, the instrument name and the instrument response

        Parameters
        ----------
        on_response_cb : Callable
            Called when the stream has response

        Returns
        -------
        current instance

        """
        self._on_response_cb = on_response_cb
        return self

    def on_update(self, on_update_cb: Callable):
        """
        This callback is called with the reference to the stream object, the instrument name and the instrument update

        Parameters
        ----------
        on_update_cb : Callable
            Called when the stream has a new update

        Returns
        -------
        current instance

        """
        self._on_update_cb = on_update_cb
        return self

    def on_state(self, on_state_cb: Callable):
        """
        This callback is called with the reference to the stream object, when the stream has new state

        Parameters
        ----------
        on_state_cb : Callable
            Called when the stream has a new state

        Returns
        -------
        current instance

        """
        self._on_state_cb = on_state_cb
        return self

    ####################################################
    #   open/close methods

    async def _do_open_async(self):
        #   open RDP item stream
        self._session.debug(
            f"Start asynchronously StreamingTDS subscription {self._stream.stream_id} for {self._universe}"
        )
        self.state = await self._stream.open_async()

    async def _do_close_async(self):
        self._session.debug(
            f"Stop asynchronously StreamingTDS subscription {self._stream.stream_id} for {self._universe}"
        )
        self.state = await self._stream.close_async()

    def _do_pause(self):
        # for override
        raise NotImplementedError(
            "ERROR!!! Currently, TradeDataStream does not support pause."
        )

    def _do_resume(self):
        # for override
        raise NotImplementedError(
            "ERROR!!! Currently, TradeDataStream does not support resume."
        )

    ####################################################
    #   callbacks

    #   RDP
    def __on_ack(self, stream: object, ack: dict):
        #   check for on_state callback
        if "state" in ack:
            #   call the callback for on_state:
            self._on_state(stream, ack["state"])

    def __on_response(self, stream: object, response: dict):

        #   check for data and headers
        if "data" in response:
            self._data = response["data"]
            self._session.debug(f"Received on_response - data={self._data}")

        if "headers" in response:
            self._headers = response["headers"]
            self._session.debug(f"Received on_response - headers={self._headers}")

            #   build column name from header
            self._column_names = [col["name"] for col in self._headers]

        #   call on_response callback function
        self._on_response(stream, response)

    def __on_update(self, stream, update):
        #   check for data and headers
        if "data" in update:
            self._data = update["data"]
            self._session.debug(f"Received on_update - data={self._data}")

        #   call on_update callback function
        self._on_update(stream, update)

    def __on_alarm(self, stream, alarm):
        #   check for on_state callback
        if "state" in alarm:
            #   call the callback for on_state:
            self._on_state(stream, alarm["state"])

    # QPS
    def _on_response(self, stream, response_message: dict):
        self._session.debug(
            f"{self.__class__.__name__}._on_response(response_message={response_message})"
        )
        #   call the on_response callback function
        if self._on_response_cb:
            #   valid on_response callback
            try:
                self._on_response_cb(self, self._data, self._column_names)
            except Exception as e:
                #   on_add callback has an exception
                self._session.error(
                    f"{self.__class__.__name__} on_response callback raised exception: {e!r}"
                )
                self._session.debug(f"{traceback.format_exc()}")

    def _on_update(self, stream, update_message: dict):
        self._session.debug(
            f"{self.__class__.__name__}._on_update(update_message={update_message})"
        )
        #   call the on_update callback function
        if self._on_update_cb:
            #   valid on_update callback
            try:
                self._on_update_cb(self, self._data, self._column_names)
            except Exception as e:
                #   on_add callback has an exception
                self._session.error(
                    f"{self.__class__.__name__} on_update callback raised exception: {e!r}"
                )
                self._session.debug(f"{traceback.format_exc()}")

    def _on_state(self, stream, state_message: dict):
        self._session.debug(
            f"{self.__class__.__name__}._on_state(state_message={state_message})"
        )
        #   call the on_state callback function
        if self._on_state_cb:
            #   valid on_state callback
            try:
                self._on_state_cb(self, state_message)
            except Exception as e:
                #   on_add callback has an exception
                self._session.error(
                    f"{self.__class__.__name__} on_state callback raised exception: {e!r}"
                )
                self._session.debug(f"{traceback.format_exc()}")
