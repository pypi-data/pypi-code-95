# coding: utf8

__all__ = ["Stream", "StreamState"]

import abc
from threading import Lock
from .state_manager import StateManager

from .state import StreamState


class Stream(StateManager, abc.ABC):
    def __init__(self, session, api=None):
        from ...core.session import get_valid_session

        session = get_valid_session(session)
        super().__init__(loop=session._loop)
        self.api = api or "streaming/pricing/main"
        self.stream_id = None
        self._stream_lock = Lock()
        self._session = session
        self._subscribe_response_future = None
        self._unsubscribe_response_future = None

    async def open_async(self, with_updates=True):
        if self._session.is_closed:
            raise AssertionError("Session must be open")

        return await super().open_async(with_updates=with_updates)

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def protocol_name(self):
        pass

    def _initialize_subscribe_response_future(self):
        #   check currently subscribe response future
        if (
            self._subscribe_response_future is not None
            and not self._subscribe_response_future.done()
        ):
            #   cancel the previous subscribe response future
            self._subscribe_response_future.cancel()

        #   create the subscribe response future
        self._subscribe_response_future = self._loop.create_future()

    def _initialize_unsubscribe_response_future(self):
        #   check currently unsubscribe response future
        if (
            self._unsubscribe_response_future is not None
            and not self._unsubscribe_response_future.done()
        ):
            #   cancel the previous subscribe response future
            self._loop.call_soon_threadsafe(self._unsubscribe_response_future.cancel)

        #   create the subscribe response future
        self._unsubscribe_response_future = self._loop.create_future()

    async def _wait_for_subscribe_response(self):
        await self._subscribe_response_future

    async def _wait_for_unsubscribe_response(self):
        await self._unsubscribe_response_future

    def _send(self, message):
        self._session.debug(
            f"Stream("
            f"id={self.stream_id}, name={self.name}, api={self.api})"
            f".send(message = {message})"
        )
        self._session.send(self.api, message)

    @staticmethod
    def _update_subscription_message_with_extended_params(
        session: object, subscription_message: dict, extended_params: dict
    ):
        subscription_message_with_extended_params = dict(subscription_message)
        #   extended parameters
        if extended_params is not None:
            #   add extended parameters into the subscription message
            for param, extended_val in extended_params.items():
                if param in subscription_message:
                    prev_value = subscription_message[param]
                    if isinstance(prev_value, dict) and isinstance(extended_val, dict):
                        session.debug(
                            f"override {param} with {extended_val} for subscribe message from extended parameters."
                        )
                        for key, val in extended_val.items():
                            session.debug(f"        override {key} with {val}.")
                            subscription_message_with_extended_params[param][key] = val
                    else:
                        session.debug(
                            f"override {param} (previous value is {prev_value}) with {extended_val} for subscribe message from extended parameters."
                        )
                        subscription_message_with_extended_params[param] = extended_val
                else:
                    session.debug(
                        f"adding new {param} with {extended_val} for subscribe message from extended parameters."
                    )
                    subscription_message_with_extended_params[param] = extended_val

        return subscription_message_with_extended_params

    ################################################
    #    callback functions

    @abc.abstractmethod
    def _on_status(self, status):
        """callback for status"""
        pass

    @abc.abstractmethod
    def _on_reconnect(
        self, failover_state, stream_state, data_state, state_code, state_text
    ):
        """Callback when the websocket connection in stream connection is reconnect"""
        pass
